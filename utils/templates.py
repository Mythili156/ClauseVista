
# Standard Contract Templates for Local Generation

def get_employment_agreement(name, date, salary):
    return f"""
# EMPLOYMENT AGREEMENT

**Date:** {date}

**BETWEEN:**
1. **Employer Name** (The "Company")
2. **{name}** (The "Employee")

**1. POSITION & DUTIES**
The Company agrees to employ the Employee as [Position Name]. The Employee agrees to perform such duties as may be assigned.

**2. COMPENSATION**
The Company shall pay the Employee a salary of INR {salary} per annum, subject to standard deductions.

**3. PROBATION PERIOD**
The Employee shall be on probation for a period of 6 months.

**4. TERMINATION**
Either party may terminate this agreement by providing 30 days of written notice or salary in lieu thereof.

**5. CONFIDENTIALITY**
The Employee agrees not to disclose any proprietary information of the Company during or after employment.

**(Signature of Employer)**              **(Signature of Employee)**
_____________________                  _____________________
"""

def get_nda(name, date, purpose):
    return f"""
# NON-DISCLOSURE AGREEMENT (NDA)

**Date:** {date}

**BETWEEN:**
1. **Disclosing Party**
2. **{name}** ("Receiving Party")

**1. PURPOSE**
The parties wish to explore a business opportunity regarding: "{purpose}".

**2. CONFIDENTIAL INFORMATION**
"Confidential Information" means all non-public information disclosed by the Disclosing Party.

**3. OBLIGATIONS**
The Receiving Party agrees to:
a) Maintain the confidentiality of the information.
b) Use it solely for the Purpose.
c) Not disclose it to any third party without prior written consent.

**4. DURATION**
This agreement shall remain in effect for 2 years from the date of disclosure.

**(Signature)**
_____________________
"""

def get_service_agreement(name, date, fee):
    return f"""
# SERVICE AGREEMENT

**Date:** {date}

**PARTIES:**
1. **Client Name**
2. **{name}** ("Service Provider")

**1. SERVICES**
The Service Provider agrees to provide the agreed-upon services in a professional manner.

**2. PAYMENT**
The Client agrees to pay a total fee of INR {fee} upon completion of milestones.

**3. INTELLECTUAL PROPERTY**
All work created under this agreement shall be the exclusive property of the Client (Work for Hire).

**4. TERMINATION**
Either party may terminate with 15 days notice.

**(Signature)**
_____________________
"""

def get_hindi_employment_agreement(name, date, salary):
    return f"""
# रोज़गार समझौता (Employment Agreement)

**दिनांक:** {date}

**मध्य:**
1. **कंपनी का नाम** ("नियोक्ता")
2. **{name}** ("कर्मचारी")

**1. पद और कर्तव्य**
कंपनी कर्मचारी को [पद का नाम] के रूप में नियुक्त करने के लिए सहमत है। कर्मचारी सौंपे गए कर्तव्यों का पालन करने के लिए सहमत है।

**2. मुआवजा (Compensation)**
कंपनी कर्मचारी को INR {salary} प्रति वर्ष का वेतन देगी, जो मानक कटौती के अधीन होगा।

**3. परिवीक्षा अवधि (Probation)**
कर्मचारी 6 महीने की अवधि के लिए परिवीक्षा पर रहेगा।

**4. समाप्ति (Termination)**
कोई भी पक्ष 30 दिनों की लिखित सूचना या उसके बदले वेतन देकर इस समझौते को समाप्त कर सकता है।

**5. गोपनीयता (Confidentiality)**
कर्मचारी रोजगार के दौरान या बाद में कंपनी की किसी भी proprietary जानकारी का खुलासा नहीं करने के लिए सहमत है।

**(नियोक्ता के हस्ताक्षर)**           **(कर्मचारी के हस्ताक्षर)**
_____________________                  _____________________
"""

def get_hindi_nda(name, date, purpose):
    return f"""
# गैर-प्रकटीकरण समझौता (NDA)

**दिनांक:** {date}

**मध्य:**
1. **खुलासा करने वाली पार्टी**
2. **{name}** ("प्राप्तकर्ता पार्टी")

**1. उद्देश्य**
पार्टियां एक व्यावसायिक अवसर का पता लगाना चाहती हैं: "{purpose}"।

**2. गोपनीय जानकारी**
"गोपनीय जानकारी" का अर्थ है खुलासा करने वाली पार्टी द्वारा बताई गई सभी गैर-सार्वजनिक जानकारी।

**3. दायित्व**
प्राप्तकर्ता पार्टी सहमत है:
क) जानकारी की गोपनीयता बनाए रखें।
ख) इसका उपयोग केवल उद्देश्य के लिए करें।
ग) पूर्व लिखित सहमति के बिना किसी तीसरे पक्ष को इसका खुलासा न करें।

**4. अवधि**
यह समझौता प्रकटीकरण की तारीख से 2 साल तक प्रभावी रहेगा।

**(हस्ताक्षर)**
_____________________
"""

def get_template(template_type, **kwargs):
    lang = kwargs.get('language', 'English')
    
    if lang == "Hindi":
        if template_type == "Employment Agreement":
            return get_hindi_employment_agreement(kwargs.get('name', '[Name]'), kwargs.get('date', '[Date]'), kwargs.get('amount', '[Amount]'))
        elif template_type == "Non-Disclosure Agreement (NDA)":
            return get_hindi_nda(kwargs.get('name', '[Name]'), kwargs.get('date', '[Date]'), kwargs.get('amount', '[Purpose]'))
        else:
             return "इस टेम्पलेट का हिंदी संस्करण उपलब्ध नहीं है। (Hindi version not available for this template type yet)."

    # Default English
    if template_type == "Employment Agreement":
        return get_employment_agreement(kwargs.get('name', '[Name]'), kwargs.get('date', '[Date]'), kwargs.get('amount', '[Amount]'))
    elif template_type == "Non-Disclosure Agreement (NDA)":
        return get_nda(kwargs.get('name', '[Name]'), kwargs.get('date', '[Date]'), kwargs.get('amount', '[Purpose]')) # Reusing amount field for purpose/generic
    elif template_type == "Vendor Service Agreement":
        return get_service_agreement(kwargs.get('name', '[Name]'), kwargs.get('date', '[Date]'), kwargs.get('amount', '[Fee]'))
    else:
        return "Template not found."
