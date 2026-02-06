# --- Indian Law Mapping ---
INDIAN_LAW_MAPPING = {
    "Non-Compete": "Section 27, Indian Contract Act: Agreement in restraint of trade is void.",
    "Termination": "Indian Contract Act: Termination must be reasonable; abrupt termination may amount to breach.",
    "Indemnity": "Section 124, Indian Contract Act: Definition of 'Contract of Indemnity'. Check for capping capability.",
    "Confidentiality": "Information Technology Act, 2000 & Contract Act: Breach of confidence is actionable.",
    "Jurisdiction": "Section 28, Indian Contract Act: Agreements in restraint of legal proceedings are void.",
    "Penalty": "Section 74, Indian Contract Act: Compensation for breach of contract where penalty stipulated.",
    "Payment": "MSME Development Act, 2006: Delayed payments to MSMEs attract compound interest.",
    "Liability": "Check for Unfair Trade Practices under Consumer Protection Act, 2019 if B2C."
}

def process_analysis_results(llm_result):
    """
    Processes and normalizes the raw output from the LLM.
    Adds derived fields like risk labels and colors.
    """
    if not llm_result or "error" in llm_result:
        return llm_result

    # 1. Normalize Composite Score
    raw_score = llm_result.get("overall_risk_score", 0)
    try:
        # Handle cases where LLM returns "85/100" or similar
        if isinstance(raw_score, str):
            import re
            match = re.search(r'\d+', raw_score)
            score = int(match.group()) if match else 50
        else:
            score = int(raw_score)
    except Exception:
        score = 50 # Default median risk

    # Cap score
    score = max(0, min(100, score))
    llm_result["overall_risk_score"] = score

    # 2. Determine Risk Level Label & Color
    if score < 40:
        llm_result["risk_level_label"] = "Low Risk"
        llm_result["risk_color"] = "green"
    elif score < 75:
        llm_result["risk_level_label"] = "Medium Risk"
        llm_result["risk_color"] = "orange"
    else:
        llm_result["risk_level_label"] = "High Risk"
        llm_result["risk_color"] = "red"

    # 3. Process Clauses (ensure list structure)
    formatted_clauses = []
    for clause in llm_result.get("clauses", []):
        try:
            # Map LLM risk levels to standard set if needed
            r_level = clause.get("risk_level", "Low").title()
            if "High" in r_level: r_level = "High"
            elif "Medium" in r_level: r_level = "Medium"
            else: r_level = "Low"
            
            clause["risk_level"] = r_level
            
            # --- ADD COMPLIANCE CITATION ---
            # Try to match title or text to our Law Mapping categories
            txt_combo = (clause.get("title", "") + " " + clause.get("text", "")).lower()
            
            clause["citation"] = None # Default
            for cat, citation in INDIAN_LAW_MAPPING.items():
                if cat.lower() in txt_combo:
                    clause["citation"] = citation
                    break
            
            formatted_clauses.append(clause)
        except:
            continue
    
    llm_result["clauses"] = formatted_clauses

    return llm_result
