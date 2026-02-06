import openai
import anthropic
import json
import time
import spacy
from utils.text_processing import nlp  # Import the shared nlp object

# --- Prompts ---

RISK_PROMPT = """
You are a senior legal risk assessor. Analyze the provided contract text for potential risks to the party receiving this specific contract advice (assume we are the Service Provider or Employee unless specified otherwise, or just general SME risk).

Identify the following:
1. Clause-level risks (High/Medium/Low)
2. Unfavorable terms
3. Missing standard protective clauses

Return a JSON object with this structure:
{
  "summary": "Brief summary of the contract",
  "overall_risk_score": "Integer 1-100",
  "clauses": [
    {
      "title": "Clause Title or Topic",
      "text": "Snippet of the clause",
      "risk_level": "High/Medium/Low",
      "explanation": "Plain language explanation of what this means",
      "recommendation": "Advice on what to negotiate"
    }
  ],
  "missing_clauses": ["List of missing standard clauses"]
}
"""

# --- Service ---

def heuristic_analysis(text):
    """
    Performs an advanced rule-based analysis using keyword matching and spaCy entity extraction.
    This runs locally and does not require any API keys.
    """
    risks = []
    text_lower = text.lower()
    score = 20 # Base low risk
    
    # --- Entity Extraction (spaCy) ---
    entities = {}
    clause_count = len(text.split('\n\n')) # Rough paragraph count
    
    if nlp:
        doc = nlp(text)
        entities['dates'] = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
        entities['money'] = [ent.text for ent in doc.ents if ent.label_ == "MONEY"]
        entities['orgs'] = [ent.text for ent in doc.ents if ent.label_ == "ORG" or ent.label_ == "PERSON"]
        entities['gpe'] = [ent.text for ent in doc.ents if ent.label_ == "GPE"] # Jurisdiction/Location

    # --- Risk Rules ---
    
    # --- Risk Rules ---
    
    # 1. Non-Compete / Restrictive Covenants
    if any(k in text_lower for k in ["non-compete", "non compete", "restraint of trade", "exclusivity"]):
        risks.append({
            "title": "Restraint of Trade / Non-Compete",
            "text": "Clause containing 'non-compete' or 'exclusivity' was found.",
            "risk_level": "High",
            "explanation": "This restricts your ability to work for others or start a similar business.",
            "recommendation": "Negotiate to remove this or limit it to < 1 year and specific competitors."
        })
        score += 30

    # 2. Termination without Cause
    if "terminate" in text_lower and ("without cause" in text_lower or "convenience" in text_lower):
        risks.append({
            "title": "Termination for Convenience",
            "text": "Clause allows termination 'without cause' or for 'convenience'.",
            "risk_level": "High",
            "explanation": "The other party can fire you at any time for no reason.",
            "recommendation": "Ensure there is a mutual right to terminate and a paid notice period."
        })
        score += 20
    elif "termination" in text_lower: # Generic termination catch
         risks.append({
            "title": "Termination Clause",
            "text": "Standard termination clause found.",
            "risk_level": "Medium",
            "explanation": "Verify notice periods are equal for both parties.",
            "recommendation": "Standard notice is usually 30-90 days."
        })
         score += 10

    # 3. Indemnification (Unlimited Liability)
    if "indemnify" in text_lower:
        risk_level = "High"
        expl = "You are agreeing to pay for the other party's losses. This can be unlimited."
        if "cap" in text_lower or "limit" in text_lower:
            risk_level = "Medium"
            expl = "Indemnity found, but risk might be mitigated by a cap/limit (keyword detected)."
            
        risks.append({
            "title": "Indemnification",
            "text": "Clause containing 'indemnify' obligations.",
            "risk_level": risk_level,
            "explanation": expl,
            "recommendation": "Limit liability to the value of the contract (1x Fees)."
        })
        score += 25 if risk_level == "High" else 15

    # 4. Jurisdiction & Arbitration
    if "arbitration" in text_lower:
        risks.append({
            "title": "Dispute Resolution (Arbitration)",
            "text": "Arbitration clause detected.",
            "risk_level": "Medium",
            "explanation": "Arbitration is private but can be expensive and limits appeal rights.",
            "recommendation": "Check if the seat of arbitration is in your city."
        })
        score += 5
        
    # 5. Payment Terms
    if "net 60" in text_lower or "net 90" in text_lower:
        risks.append({
            "title": "Long Payment Terms",
            "text": "Payment terms of Net 60 or Net 90 detected.",
            "risk_level": "Medium",
            "explanation": "You will have to wait 2-3 months to get paid.",
            "recommendation": "Negotiate for Net 30 or Net 15."
        })
        score += 15

    # 6. Intellectual Property (IP)
    if "work for hire" in text_lower or "assigns all rights" in text_lower:
         risks.append({
            "title": "IP Assignment (Work for Hire)",
            "text": "Clause assigning all IP rights detected.",
            "risk_level": "High",
            "explanation": "You lose ownership of everything you create.",
            "recommendation": "Ensure you retain pre-existing IP and tools."
        })
         score += 15

    # --- 7. NEW: Ambiguity Detection ---
    ambiguous_terms = ["reasonable", "good faith", "mutual agreement", "promptly", "standard quality", "material breach", "as decided by"]
    found_ambiguities = [t for t in ambiguous_terms if t in text_lower]
    if found_ambiguities:
        risks.append({
            "title": "Ambiguous Terms Detected",
            "text": f"Found vague terms: {', '.join(found_ambiguities[:3])}...",
            "risk_level": "Medium",
            "explanation": "Vague terms are open to interpretation and often lead to disputes.",
            "recommendation": "Define terms quantitatively (e.g., 'within 7 days' instead of 'promptly')."
        })
        score += 10

    # --- 8. NEW: Regex Enhancements (Financials & Parties) ---
    import re
    # Financials (Rs. 5000, INR 5L, $100, 10,000/-)
    money_pattern = r'(?:Rs\.?|INR|₹|\$)\s*[\d,]+(?:\.\d{2})?|[\d,]+\s*/-'
    regex_money = re.findall(money_pattern, text)
    if regex_money:
        entities['money'].extend(regex_money)
        entities['money'] = list(set(entities['money']))[:5] # Dedupe & Top 5

    # Parties (Between X and Y)
    party_pattern = r"(?:between|amongst)\s+([A-Z][a-zA-Z\s\.]+)\s+(?:and|&)\s+([A-Z][a-zA-Z\s\.]+)"
    party_match = re.search(party_pattern, text, re.IGNORECASE)
    if party_match:
        regex_parties = [p.strip() for p in party_match.groups()]
        entities['orgs'].extend(regex_parties)
        entities['orgs'] = list(set(entities['orgs']))[:3] # Dedupe & limit

    
    # 7. Basic Hindi / Hinglish Checks (Local Multilingual Support)
    if any(k in text_lower for k in ["muwavza", "muqadma", "hrajana", "indemnity"]):
        risks.append({
            "title": "Indemnity (Hindi/English)",
            "text": "Potential indemnity terms found (possibly in Hindi/Hinglish).",
            "risk_level": "High",
            "explanation": "You might be liable for damages.",
            "recommendation": "Check for 'Muwavza' or 'Indemnity' clauses."
        })
        score += 20
        
    if any(k in text_lower for k in ["samapti", "radd", "terminate"]):
        # Already handled by English check, but ensuring coverage
        pass

    # Summary Generation
    summary = "This is an Automated Local Analysis (No AI). "
    if entities.get('orgs'):
        summary += f"Parties involved may include: {', '.join(entities['orgs'][:3])}. "
    if entities.get('money'):
        summary += f"Financial terms found: {', '.join(entities['money'][:3])}. "
    
    missing = []
    if "confidentiality" not in text_lower and "non-disclosure" not in text_lower and "gopniyata" not in text_lower:
        missing.append("Confidentiality / NDA Clause")
    if "force majeure" not in text_lower:
        missing.append("Force Majeure (Act of God)")

    return {
        "summary": summary,
        "overall_risk_score": min(score, 100),
        "clauses": risks,
        "missing_clauses": missing,
        "meta": {
            "clause_count": clause_count,
            "parties": entities.get('orgs', []),
            "jurisdiction": entities.get('gpe', []),
            "financials": entities.get('money', [])
        }
    }

def get_client_openai(api_key):
    return openai.OpenAI(api_key=api_key)

def get_client_anthropic(api_key):
    return anthropic.Anthropic(api_key=api_key)

def analyze_contract_with_llm(text, api_key, provider="Local Analysis"):
    """
    Orchestrates the analysis.
    """
    # Force local analysis if provider implies it or if key implies it
    if provider == "Local Analysis" or api_key == "offline" or not api_key:
        time.sleep(1)
        return heuristic_analysis(text)
    
    # Truncate if necessary (rough safety limit)
    truncated_text = text[:50000] 
    
    try:
        if provider == "Anthropic":
            client = get_client_anthropic(api_key)
            message = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                temperature=0,
                system="You are an expert legal AI assistant for Indian SMEs. Respond in JSON.",
                messages=[
                    {"role": "user", "content": f"{RISK_PROMPT}\n\nContract Text:\n{truncated_text}"}
                ]
            )
            response_text = message.content[0].text
            
        elif provider == "OpenAI":
            client = get_client_openai(api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are an expert legal AI assistant for Indian SMEs. Respond in JSON."},
                    {"role": "user", "content": f"{RISK_PROMPT}\n\nContract Text:\n{truncated_text}"}
                ]
            )
            response_text = response.choices[0].message.content
            
        else:
            # Fallback to local
            return heuristic_analysis(text)

        # Parse JSON
        try:
            analysis_result = json.loads(response_text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse LLM response via API. Try Local Analysis mode.", "raw_response": response_text}
            
        return analysis_result

    except Exception as e:
        # If API fails, notify user but maybe suggest local mode in UI?
        # For now just return error
        return {"error": f"API Error ({provider}): {str(e)}\n\nTry switching to 'Local Analysis' mode to avoid billing limits."}
