import io
from PyPDF2 import PdfReader
import docx
import spacy

# Try to load spaCy model, or handle if missing
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback or instructions to download
    # In a real app we might automate this, but for now we assume it's present or we proceed without it for basic tasks
    nlp = None

def extract_text_from_pdf(file_bytes):
    """Extracts text from a PDF file (bytes)."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_docx(file_bytes):
    """Extracts text from a DOCX file (bytes)."""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def extract_text_from_txt(file_bytes):
    """Extracts text from a TXT file (bytes)."""
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1")
    except Exception as e:
        return f"Error reading TXT: {str(e)}"

def clean_text(text):
    """Basic text cleaning."""
    # Remove excessive whitespace
    text = " ".join(text.split())
    return text

def get_sentences(text):
    """Splits text into sentences using spaCy if available, else simple split."""
    if nlp:
        doc = nlp(text)
        return [sent.text for sent in doc.sents]
    else:
        # Fallback simple splitting
        return text.split('. ')

def classify_contract(text):
    """
    Classifies the contract type based on keywords in the first 1000 characters.
    Returns: str (Contract Type)
    """
    text_head = text[:2000].lower()
    
    if any(k in text_head for k in ["employment agreement", "offer letter", "appointment letter", "employee"]):
        return "Employment Agreement"
    if any(k in text_head for k in ["non-disclosure", "confidentiality agreement", "nda"]):
        return "Non-Disclosure Agreement (NDA)"
    if any(k in text_head for k in ["service agreement", "master service", "msa", "consulting"]):
        return "Service Agreement"
    if any(k in text_head for k in ["lease", "rental agreement", "tenancy"]):
        return "Lease Agreement"
    if any(k in text_head for k in ["vendor", "supplier", "purchase order"]):
        return "Vendor Agreement"
        
    # Hindi/Hinglish Classification
    if any(k in text_head for k in ["naukri", "rozgar", "niyukti patra", "sevak"]):
        return "Employment Agreement (Hindi)"
    if any(k in text_head for k in ["gopniyata", "raaz", "chupa", "gupt"]):
        return "Non-Disclosure Agreement (Hindi)"
    if any(k in text_head for k in ["kiraya", "bhaada", "patta", "makan maalik"]):
        return "Lease Agreement (Hindi)"
        
    return "General Contract"

# --- Hindi to English Normalization ---

# --- Hindi to English Normalization ---

HINDI_LEGAL_TERMS = {
    # Employment
    "niyukti": "appointment", "नियुक्ति": "appointment",
    "rozgar": "employment", "रोजगार": "employment",
    "vetan": "salary", "वेतन": "salary",
    "tankhah": "salary", "तनख्वाह": "salary",
    "karyalaya": "office", "कार्यालय": "office",
    "avdhi": "duration", "अवधि": "duration",
    "samapti": "termination", "समाप्ति": "termination",
    "istifa": "resignation", "इस्तीफा": "resignation",
    "chutti": "leave", "छुट्टी": "leave",
    "naukri": "job", "नौकरी": "job",
    
    # NDA / Confidentiality
    "gopniyata": "confidentiality", "गोपनीयता": "confidentiality",
    "gupt": "confidential", "गुप्त": "confidential",
    "raaz": "secret", "राज": "secret",
    "prakat": "disclosure", "प्रकट": "disclosure",
    "ulangan": "violation", "उल्लंघन": "violation",
    
    # Lease / Property
    "kiraya": "rent", "किराया": "rent",
    "bhaada": "rent", "भाड़ा": "rent",
    "makan maalik": "landlord", "मकान मालिक": "landlord",
    "kirayedar": "tenant", "किरायदार": "tenant",
    "sampatti": "property", "संपत्ति": "property",
    "kabza": "possession", "कब्जा": "possession",
    "bayaana": "deposit", "बयाना": "deposit",
    
    # General Legal
    "karar": "agreement", "करार": "agreement",
    "samjhauta": "agreement", "समझौता": "agreement",
    "dastavej": "document", "दस्तावेज": "document",
    "kanuni": "legal", "कानूनी": "legal",
    "muwavza": "compensation", "मुआवजा": "compensation",
    "jurmana": "penalty", "जुर्माना": "penalty",
    "shart": "condition", "शर्त": "condition",
    "niyam": "rule", "नियम": "rule",
    "hastakshar": "signature", "हस्ताक्षर": "signature",
    "tarikh": "date", "तारीख": "date",
    "adhikar": "right", "अधिकार": "right",
    "jimmedari": "liability", "जिम्मेदारी": "liability",
    "vivad": "dispute", "विवाद": "dispute",
    "nyayalaya": "court", "न्यायालय": "court"
}

def normalize_hindi_text(text):
    """
    Replaces common Hindi/Hinglish legal terms with English equivalents
    to allow the English-based Risk Engine to process them.
    """
    normalized = text.lower()
    
    # Simple Dictionary Replacement (Case Insensitive)
    for hindi, english in HINDI_LEGAL_TERMS.items():
        # Using simple replace for now - adequate for this scale
        # Adding spaces to ensure we don't replace parts of words if possible
        normalized = normalized.replace(f" {hindi} ", f" {english} ")
        normalized = normalized.replace(f" {hindi}.", f" {english}.")
        normalized = normalized.replace(f"{hindi} ", f"{english} ") # Start of line
        
        # Also try Devanagari if needed (future expansion)
    
    return normalized
