# Deployment Guide

This guide covers two methods to deploy the Contract Analysis Bot: **Streamlit Cloud** (Best for testing) and **Docker** (Best for persistence/production).

## Important Note on Persistence
This app uses **local JSON files** (`audit_log.json`, `users.json`, `sessions.json`) to store data.
- **Streamlit Cloud**: These files will likely reset when the app sleeps/reboots.
- **Docker**: You can mount a volume to persist these files.

---

## Option 1: Streamlit Cloud (Fastest)

1.  **Push to GitHub**: Upload this entire code repository to GitHub.
2.  **Sign in to Streamlit**: Go to [share.streamlit.io](https://share.streamlit.io/).
3.  **Deploy**:
    - Click "New App".
    - Select your GitHub repository.
    - Set Main File path to `app.py`.
    - Click **Deploy**.

**Requirements**: Ensure `requirements.txt` is in the root (already done).

---

## Option 2: Docker (Recommended for Persistence)

We have included a `Dockerfile`.

### 1. Build the Image
Open a terminal in the project folder:
```bash
docker build -t contract-bot .
```

### 2. Run the Container
Run the container, binding port 8501:
```bash
docker run -p 8501:8501 contract-bot
```
The app will be available at `http://localhost:8501`.

### 3. Run with Persistence (Volumes)
To save your Audit Logs and User Accounts even if the container stops:
```bash
# Windows (PowerShell)
docker run -p 8501:8501 -v ${PWD}/utils:/app/utils contract-bot
```
*(Note: This mounts the `utils` folder where the JSON files live, or you can adjust paths if you move JSONs to a `data/` folder).*

---

## Option 3: Local Network (Share in Office)

To let others on your WiFi/LAN verify your app:
```bash
streamlit run app.py --server.address=0.0.0.0
```
Then share your computer's IP address (e.g., `http://192.168.1.5:8501`) with colleagues.
