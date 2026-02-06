# Contract Analysis & Drafting Bot 🤖⚖️

An intelligent, secure, and offline-capable legal assistant designed for Indian SMEs. This tool helps business owners analyze contracts for risks, understand legal jargon in plain English/Hindi, and draft standard legal agreements instantly.

## 🌟 Key Features

### 1. Risk Analysis Engine
-   **Automated Review**: Upload PDF, DOCX, or TXT files.
-   **Risk Scoring**: Visual Gauge Chart showing Low (Green), Medium (Orange), or High (Red) risk.
-   **Compliance Checks**: Automatically cites **Indian Contract Law** (e.g., Section 27 for Non-Compete).
-   **Metadata Extraction**: Extracts Parties, Financial Values, and Ambiguous Terms (e.g., "promptly").

### 2. 🇮🇳 Multilingual Support (Hindi)
-   **Analysis**: Normalizes Hindi legal terms (e.g., *Rozgar*, *Samapti*) for accurate risk detection.
-   **Drafting**: Generate standard agreements (Employment, NDA) in Hindi or English.
-   **UI**: Language toggle for the Drafting Assistant.

### 3. 📝 Drafting Assistant
-   **Templates**: Pre-loaded templates for Employment Agreements, NDAs, and Vendor Contracts.
-   **Customization**: fast-fill inputs for Names, Dates, and Amounts.

### 4. 🛡️ Security & Audit
-   **Local Processing**: All analysis runs locally using `spaCy` and Python rules (No data leaves your machine).
-   **Audit Trail**: Logs all login and analysis events to `audit_log.json`.
-   **Authentication**: Built-in Login/Registration system.

### 5. Export
-   **PDF Reports**: detailed risk assessment reports.
-   **JSON**: structured data export.

---

## 🚀 Getting Started

### Prerequisites
-   Python 3.9+
-   Recommended: Virtual Environment

### Installation

1.  **Clone the repository** (or download files):
    ```bash
    git clone <repo-url>
    cd contract-bot
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Download NLP Model**:
    ```bash
    python -m spacy download en_core_web_sm
    ```

---

## 🏃‍♂️ How to Run

Start the Streamlit application:
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

### Default Login
-   **Register**: Click "Create an Account" on the login page.
-   **Login**: Use your newly created credentials.

---

## 📂 Project Structure

-   `app.py`: Main application entry point (UI & Logic).
-   `utils/`:
    -   `risk_engine.py`: Core logic for scoring and Indian Law mapping.
    -   `llm_analysis.py`: Text extraction and heuristic analysis.
    -   `text_processing.py`: Hindi normalization and file reading.
    -   `templates.py`: Contract generation templates.
    -   `audit_logger.py`: JSON-based logging system.
    -   `auth.py`: User management.
-   `audit_log.json`: (Created at runtime) activity logs.
-   `users.json`: (Created at runtime) user credentials.

---

## 🛠️ Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for Docker and Streamlit Cloud instructions.

---

## ⚠️ Disclaimer
This tool provides **informational guidance only** and is not a substitute for professional legal advice. Always consult a qualified lawyer for binding agreements.
