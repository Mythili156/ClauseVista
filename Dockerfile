FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (if any)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy app code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
