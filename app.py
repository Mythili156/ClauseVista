import streamlit as st
import os
import pandas as pd
from utils import text_processing, llm_analysis, risk_engine, auth, audit_logger
import json
import time

# --- Auth Check with Session Persistence ---
# 1. Check if already in session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 2. If not, check URL Token (Auto-Login)
if not st.session_state.authenticated:
    params = st.query_params
    token = params.get("auth_token", None)
    if token:
        user = auth.get_user_from_token(token)
        if user:
             st.session_state.authenticated = True
             st.session_state.username = user
             # Fetch display name
             u_db = auth._load_users()
             st.session_state.user_display_name = u_db.get(user, {}).get('name', user)
        else:
            # Invalid token, clear it
            st.query_params.clear()

if not st.session_state.authenticated:
    # --- LOGIN / REGISTER PAGE ---
    # --- Page Config ---
    st.set_page_config(
        page_title="Contract Analysis Bot",
        page_icon="⚖️",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # --- CSS Styling (Green Background & White Card) ---
    st.markdown("""
    <style>
        /* Global Font & Background */
        .stApp {
            background-color: #f0fdf4; /* global-green */
            font-family: 'Inter', sans-serif;
        }
        
        /* Headers */
        .main-header { 
            font-size: 2.5rem; 
            font-weight: 800; 
            color: #15803d; /* Green-700 */
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .sub-header { 
            font-size: 1.1rem; 
            color: #64748b;
            text-align: center; 
            margin-bottom: 2rem; 
        }

        /* Login Card Styling */
        div[data-testid="stVerticalBlock"] > div:has(div.login-card) {
            display: flex;
            justify-content: center;
        }
        
        # .login-container {
        #     max-width: 450px;
        #     margin: 0 auto;
        #     padding: 40px;
        #     background: #ffffff; /* White Card */
        #     border-radius: 20px;
        #     box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        #     border: 1px solid #bbf7d0; /* Green-200 */
        }
        
        /* Segmented Control / Radio Button Styling */
        .stRadio > div[role="radiogroup"] {
            display: flex;
            justify-content: center;
            background-color: #f8fafc; /* Slight contrast in white card */
            border-radius: 12px;
            padding: 5px;
            border: 1px solid #e2e8f0;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
            width: 100%;
        }
        
        .stRadio > div[role="radiogroup"] > label {
            flex: 1;
            text-align: center;
            background-color: transparent !important;
            border-radius: 8px;
            padding: 10px;
            margin: 0 2px;
            border: 1px solid transparent;
            cursor: pointer;
            transition: all 0.2s;
            color: #475569 !important;
            font-weight: 600;
            display: flex;
            justify-content: center;
        }
        
        /* Force Label Colors (Fix for Invisible Text in Dark Mode) */
        .stRadio p, .stRadio label, .stTextInput label, .stTextInput p {
            color: #1e293b !important; /* Force Dark Text */
            font-weight: 600;
        }

        .stRadio > div[role="radiogroup"] > label:hover {
            color: #15803d !important;
            background-color: white !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        /* Active Radio Button */
        .stRadio > div[role="radiogroup"] > label[data-checked="true"] {
            background-color: #15803d !important; /* Green-700 */
            color: white !important;
            box-shadow: 0 4px 6px -1px rgba(21, 128, 61, 0.3);
        }
        
        /* Input Fields */
        .stTextInput > div > div > input {
            border-radius: 10px;
            border: 1px solid #cbd5e1;
            padding: 10px 12px;
            font-size: 1rem;
            color: #1e293b !important; /* Force Dark Text */
            background-color: #ffffff !important; /* Force White Background */
            caret-color: #1e293b !important;
        }
        .stTextInput > div > div > input::placeholder {
            color: #94a3b8 !important; /* Force Visible Placeholder */
            opacity: 1;
        }
        .stTextInput > div > div > input:focus {
            border-color: #15803d; 
            box-shadow: 0 0 0 2px rgba(21, 128, 61, 0.2);
            color: #1e293b !important;
            background-color: #ffffff !important;
        }
        
        /* Buttons */
        .stButton > button {
            background-color: #15803d; /* Green-700 */
            color: white;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 600;
            border: none;
            width: 100%;
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            background-color: #166534; /* Green-800 */
            box-shadow: 0 4px 6px -1px rgba(21, 128, 61, 0.4);
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Centered Layout ---
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo Area
        # st.markdown("""
        # <div style="text-align: center; margin-bottom: 20px;">
        #     <img src="https://cdn-icons-png.flaticon.com/512/924/924915.png" width="80" style="margin-bottom: 15px;">
        # </div>
        # """, unsafe_allow_html=True)
        
        st.markdown('<div class="main-header">ClauseVista</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header" style="color:#64748b;">Intelligent & Secure Contract Protection</div>', unsafe_allow_html=True)
        
        # Login/Register Card using Container
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            
            # Use columns inside container for strict width control if needed, 
            # but standard flow is fine with the CSS wrapper
            
            # -- Auth Mode Selection (Styled as Buttons) --
            if "auth_mode" not in st.session_state:
                st.session_state.auth_mode = "Sign In"
                
            # Removed key="auth_nav" to allow programmatic reset via index
            selected_mode = st.radio("Auth Mode", ["Sign In", "Create Account"], 
                                   horizontal=True, 
                                   label_visibility="collapsed",
                                   index=0 if st.session_state.auth_mode == "Sign In" else 1)

            if selected_mode != st.session_state.auth_mode:
                st.session_state.auth_mode = selected_mode
                st.rerun()

            st.markdown("<hr style='margin: 15px 0 25px 0; border-color: #bbf7d0;'>", unsafe_allow_html=True)
            
            if st.session_state.auth_mode == "Sign In":
                st.markdown("<h3 style='text-align: center; color: #15803d; margin-top: 0;'>Welcome Back</h3>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9rem; margin-bottom: 25px;'>Sign in to your secure workspace.</p>", unsafe_allow_html=True)
                
                l_user = st.text_input("Username or Email", key="l_user", placeholder="Enter username or email")
                l_pass = st.text_input("Password", type="password", key="l_pass", placeholder="••••••••")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("Sign In", type="primary", use_container_width=True):
                    success, name, real_username = auth.login_user(l_user, l_pass)
                    if success:
                        # CREATE SESSION TOKEN
                        token = auth.create_session_token(real_username)
                        st.query_params["auth_token"] = token
                        
                        st.session_state.authenticated = True
                        st.session_state.user_display_name = name
                        st.session_state.username = real_username
                        
                        # LOG LOGIN
                        audit_logger.log_event(real_username, "User Login", {"source": "web"})
                        
                        st.success("Login Successful!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid Username/Email or Password")
            
            else: # Create Account
                st.markdown("<h3 style='text-align: center; color: #1e293b; margin-top: 0;'>Get Started</h3>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9rem; margin-bottom: 25px;'>Create a local secure account.</p>", unsafe_allow_html=True)
                
                r_name = st.text_input("Full Name", placeholder="John Doe")
                r_email = st.text_input("Email Address", placeholder="john@example.com")
                r_user = st.text_input("Choose Username", placeholder="john_legal")
                r_pass = st.text_input("Choose Password", type="password", placeholder="••••••••")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("Create Account", use_container_width=True):
                    if r_user and r_pass and r_email:
                        success, msg = auth.register_user(r_user, r_pass, r_name, r_email)
                        if success:
                            st.success("Account Created! Redirecting to Login...")
                            st.session_state.auth_mode = "Sign In"
                            # Removed conflicting state update
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Please fill all fields")
                        
            st.markdown('</div>', unsafe_allow_html=True) # End login-container

else:
    # --- AUTHENTICATED APP ---
    # --- Page Config ---
    st.set_page_config(
        page_title="ClauseVista",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # --- CSS Styling (Authenticated) ---
    st.markdown("""
    <style>
        .stApp { background-color: #f8fafc; }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0f766e; /* Dark Slate 900 */
            border-right: 1px solid #1e293b;
        }
        [data-testid="stSidebar"] * {
            color: #f8fafc !important; /* White text */
        }
        
        /* Sidebar Nav Buttons (Radio) */
        .stRadio > div[role="radiogroup"] > label {
            background-color: transparent;
            border-radius: 8px;
            padding-left: 10px;
            padding-right: 10px;
            margin-bottom: 4px;
            border: 1px solid transparent;
            transition: all 0.2s;
        }
        .stRadio > div[role="radiogroup"] > label:hover {
            background-color: #1e293b; /* Dark hover */
        }
        /* Active Selection via internal Streamlit classes (approximate) */
        .stRadio > div[role="radiogroup"] > label[data-checked="true"] {
            background-color: #bbf7d0 !important; /* Green-200 */
            border: 1px solid #86efac;
            color: #0f172a !important; /* Dark Text for Light Background */
            font-weight: 600;
        }
        
        /* Sidebar Button (Logout) */
        [data-testid="stSidebar"] .stButton > button {
            background-color: #04260F !important; /* Extremely Dark Green */
            color: #e2e8f0 !important; /* Light Text */
            border: 1px solid #1e293b;
            font-weight: 600;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background-color: #0f172a !important; 
            border-color: #334155;
            color: white !important;
        }

        /* Sidebar Download Buttons (Export) */
        [data-testid="stSidebar"] .stDownloadButton > button {
            background-color: #04260F !important; /* Extremely Dark Green */
            color: #e2e8f0 !important; /* Light Text */
            border: 1px solid #1e293b;
            font-weight: 600;
        }
        [data-testid="stSidebar"] .stDownloadButton > button:hover {
            background-color: #0f172a !important; 
            border-color: #334155;
            color: white !important;
        }
        
        /* content styling */
        .risk-high { color: #be123c; background: #fff1f2; padding: 2px 8px; border-radius: 4px; border: 1px solid #ffe4e6; }
        .risk-medium { color: #b45309; background: #fffbeb; padding: 2px 8px; border-radius: 4px; border: 1px solid #fef3c7; }
        .main-header { font-size: 2.5rem; color: #0f766e; font-weight: 800; }
        .card { padding: 15px; border-radius: 10px; background-color: white; border: 1px solid #e2e8f0; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

    # --- Session State Init ---
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'contract_text' not in st.session_state:
        st.session_state.contract_text = None
    if 'generated_template' not in st.session_state:
        st.session_state.generated_template = None

    # --- Sidebar Navigation ---
    with st.sidebar:
        # Logo Area
        # st.image("https://cdn-icons-png.flaticon.com/512/2237/2237505.png", width=40) 
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <img src="https://cdn-icons-png.flaticon.com/512/924/924915.png" width="40" style="filter: brightness(0) invert(1);">
            <div style="font-size: 1.5rem; font-weight: 800; color: white;">ClauseVista</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.caption(f"Logged in as: **{st.session_state.user_display_name}**")
        
        # Use simple radio but styled
        page = st.radio("Navigate", 
                        ["Analysis Dashboard", "Drafting Assistant", "Settings"], 
                        label_visibility="collapsed")
        
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.query_params.clear() 
            st.rerun()

    # ==========================================
    # PAGE 2: ANALYSIS DASHBOARD
    # ==========================================
    if page == "Analysis Dashboard":
        # --- Main Logic ---
        st.markdown('<div class="main-header">Contract Analysis & Risk Assessment Bot</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Your intelligent offline legal assistant for secure, instant contract review.</div>', unsafe_allow_html=True)

        # --- Main Layout ---
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 📊 Dashboard")
            st.markdown("Upload a legal contract to instantly identify potential risks, missing clauses, and unfavorable terms using our secure local engine.")
            
            if st.session_state.contract_text:
                c_type = text_processing.classify_contract(st.session_state.contract_text)
                st.info(f"📂 Detected Document Type: **{c_type}**")

        with col2:
            # Upload Section in a nice box
            st.markdown("""
            <div style="background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0;">
                <h4 style="margin-top:0;">📄 Upload Document</h4>
            </div>
            """, unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Select PDF, DOCX, or TXT", type=["pdf", "docx", "txt"], label_visibility="collapsed")
            
            # Options
            enable_hindi_norm = st.checkbox("🇮🇳 Enable Hindi + English Normalization", help="Translates common Hindi legal terms (e.g., 'Samapti', 'Muwavza') to English for analysis.")
            
            if uploaded_file:
                 process_btn = st.button(" Run Analysis", type="primary", use_container_width=True)
            else:
                 process_btn = st.button("Run Analysis", disabled=True, use_container_width=True)

        # Analysis Logic
        if process_btn and uploaded_file:
            with st.spinner("Reading and Analyzing Document..."):
                # 1. Extract Text
                try:
                    file_ext = uploaded_file.name.split('.')[-1].lower()
                    file_bytes = uploaded_file.read()
                    
                    if file_ext == 'pdf':
                        text = text_processing.extract_text_from_pdf(file_bytes)
                    elif file_ext in ['docx', 'doc']:
                        text = text_processing.extract_text_from_docx(file_bytes)
                    else:
                        text = text_processing.extract_text_from_txt(file_bytes)
                        
                    # --- Normalization Step ---
                    if enable_hindi_norm:
                        text = text_processing.normalize_hindi_text(text)
                        
                    st.session_state.contract_text = text
                except Exception as e:
                    st.error(f"Error reading file: {e}")
                    st.stop()
            
            if not st.session_state.contract_text or len(st.session_state.contract_text) < 50:
                 st.error("Could not extract enough text from the document.")
            else:
                # 2. Analyze
                raw_result = llm_analysis.analyze_contract_with_llm(
                    st.session_state.contract_text, 
                    "offline",
                    provider="Local Analysis"
                )
                processed_result = risk_engine.process_analysis_results(raw_result)
                st.session_state.analysis_result = processed_result
                st.session_state.contract_type = text_processing.classify_contract(st.session_state.contract_text)
                
                # LOG ANALYSIS
                audit_logger.log_event(
                    st.session_state.username, 
                    "Contract Analysis", 
                    {"filename": uploaded_file.name, "risk_score": processed_result.get('overall_risk_score')}
                )
                
                st.rerun()

        # Display Results (only if analysis exists)
        if st.session_state.analysis_result:
            res = st.session_state.analysis_result
            
            if "error" in res:
                st.error(f"Analysis Failed: {res['error']}")
            else:
                # Dashboard Cards
                st.divider()
                
                # --- 1. Primary Contract Details ---
                c_type = st.session_state.get('contract_type', 'General Contract')
                meta = res.get('meta', {})
                
                st.subheader("1. Contract Understanding Results")
                
                d1, d2, d3, d4 = st.columns(4)
                
                with d1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Contract Type</div>
                        <div class="metric-value" style="font-size: 1.2rem; color: #1e293b;">{c_type.split(' ')[0]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with d2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Parties</div>
                        <div class="metric-value" style="font-size: 1.2rem; color: #1e293b;">{len(meta.get('parties', []))}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with d3:
                    loc = meta.get('jurisdiction', [])
                    loc_val = loc[0] if loc else "Unknown"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Jurisdiction</div>
                        <div class="metric-value" style="font-size: 1.2rem; color: #1e293b;">{loc_val}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with d4:
                    fin = meta.get('financials', [])
                    fin_val = fin[0] if fin else "Not Detected"
                    if len(fin) > 1: fin_val = f"{fin_val} (+{len(fin)-1} more)"
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Financial Value</div>
                        <div class="metric-value" style="font-size: 1.2rem; color: #1e293b;">{fin_val}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Metadata Expander
                with st.expander("📋 Detailed Contract Metadata (Parties, Financials, Ambiguities)"):
                    mc1, mc2 = st.columns(2)
                    with mc1:
                        st.markdown("**Identified Parties:**")
                        for p in meta.get('parties', []):
                            st.write(f"- {p}")
                        if not meta.get('parties'): st.write("*No parties extracted.*")
                    
                    with mc2:
                        st.markdown("**Financial Terms:**")
                        for f in meta.get('financials', []):
                            st.write(f"- {f}")
                        if not meta.get('financials'): st.write("*No financial terms extracted.*")
                
                st.divider()
                
                st.subheader("2. Risk Analysis")

                # Top Metrics
                m1, m2, m3 = st.columns(3)
                
                score = res.get('overall_risk_score', 0)
                score_color = "#166534" # Green
                if score > 50: score_color = "#ca8a04" # Yellow
                if score > 75: score_color = "#991b1b" # Red
                
                with m1:
                    import plotly.graph_objects as go
                    
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = score,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Overall Risk Score", 'font': {'size': 16, 'color': "#1e293b"}},
                        gauge = {
                            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#334155"},
                            'bar': {'color': "#1e293b"},
                            'bgcolor': "white",
                            'borderwidth': 2,
                            'bordercolor': "#cbd5e1",
                            'steps': [
                                {'range': [0, 40], 'color': "#86efac"},  # Low Risk (Green)
                                {'range': [40, 75], 'color': "#fdba74"}, # Medium Risk (Orange)
                                {'range': [75, 100], 'color': "#fca5a5"} # High Risk (Red)
                            ],
                            'threshold': {
                                'line': {'color': score_color, 'width': 4},
                                'thickness': 0.75,
                                'value': score
                            }
                        }
                    ))
                    
                    fig_gauge.update_layout(
                        height=220, 
                        margin=dict(l=20, r=20, t=40, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        font={'family': "Inter, sans-serif"}
                    )
                    st.plotly_chart(fig_gauge, use_container_width=True)
                    
                with m2:
                     st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">HIGH RISK CLAUSES</div>
                        <div class="metric-value" style="color: #991b1b">{len([c for c in res.get('clauses', []) if c['risk_level'] == 'High'])}</div>
                    </div>
                    """, unsafe_allow_html=True)
                     
                with m3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">MISSING CLAUSES</div>
                        <div class="metric-value" style="color: #ea580c">{len(res.get('missing_clauses', []))}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Tabs for detailed view
                tab_risk, tab_doc = st.tabs(["⚠️ Risk Findings", "📄 Original Text"])
                
                with tab_risk:
                    st.subheader("Detailed Risk Assessment")
                    
                    # Display missing clauses first if any
                    if res.get('missing_clauses'):
                        st.warning(f"**Missing Protective Clauses:** {', '.join(res.get('missing_clauses'))}")
                        
                    # Clauses as Cards
                    for c in res.get('clauses', []):
                        risk_color = '#dc2626' if c['risk_level'] == 'High' else '#d97706'
                        bg_color = '#fef2f2' if c['risk_level'] == 'High' else '#fffbeb'
                        
                        st.markdown(f"""
                        <div style="
                            background-color: white; 
                            padding: 20px; 
                            border-radius: 12px; 
                            border-left: 6px solid {risk_color}; 
                            margin-bottom: 16px; 
                            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                            border: 1px solid #f1f5f9;
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                                <h4 style="margin: 0; color: #1e293b; font-size: 1.1rem; font-weight: 700;">{c.get('title')}</h4>
                                <span style="background-color: {bg_color}; color: {risk_color}; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; border: 1px solid {risk_color}20;">
                                    {c.get('risk_level').upper()} RISK
                                </span>
                            </div>
                            <div style="background-color: #f8fafc; padding: 12px; border-radius: 8px; margin-bottom: 12px; border: 1px solid #e2e8f0;">
                                <code style="color: #475569; font-size: 0.9rem; font-family: monospace;">"{c.get('text')}"</code>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 8px;">
                                <div>
                                    <strong style="color: #64748b; font-size: 0.8rem; text-transform: uppercase;">Analysis</strong>
                                    <p style="margin-top: 4px; color: #334155; font-size: 0.95rem;">{c.get('explanation')}</p>
                                </div>
                                <div>
                                    <strong style="color: #64748b; font-size: 0.8rem; text-transform: uppercase;">Recommendation</strong>
                                    <p style="margin-top: 4px; color: #334155; font-size: 0.95rem;">{c.get('recommendation')}</p>
                                </div>
                            </div>
                            
                            
                        </div>
                        """, unsafe_allow_html=True)

                with tab_doc:
                    st.text_area("Full Contract Text", st.session_state.contract_text, height=600)
                    
                # Export Tools (Floating in Sidebar for Dashboard)
                with st.sidebar:
                     if st.session_state.analysis_result:
                       st.subheader("Export Report")
                       c_type_print = st.session_state.get('contract_type', 'Unknown Contract')
                       
                       # JSON Export
                       st.download_button(
                           "📥 Export JSON",
                           data=json.dumps(st.session_state.analysis_result, indent=2),
                           file_name="risk_analysis.json",
                           mime="application/json"
                       )
                       
                       # PDF Export
                       from utils.export import create_pdf_report
                       pdf_bytes = create_pdf_report(st.session_state.analysis_result, c_type_print)
                       st.download_button(
                           "📄 Export PDF Report",
                           data=pdf_bytes,
                           file_name="contract_report.pdf",
                           mime="application/pdf"
                       )

    # ==========================================
    # PAGE 3: DRAFTING ASSISTANT
    # ==========================================
    elif page == "Drafting Assistant":
        st.markdown('<div class="main-header">Drafting Assistant</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Create standard, safe legal agreements in seconds.</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("""
            <div class="metric-card" style="text-align: left; align-items: start;">
                <h3 style="color: #1e293b; margin-top:0;">📝 Configuration</h3>
                <p style="color: #64748b; font-size: 0.9rem;">Select a template type and fill in the key details.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # LANGUAGE SELECTOR
            t_lang = st.radio("Language", ["English", "Hindi"], horizontal=True)
            
            t_type = st.selectbox("Document Type", ["Employment Agreement", "Non-Disclosure Agreement (NDA)", "Vendor Service Agreement"])
            t_name = st.text_input("Other Party Name", placeholder="e.g. John Doe / Acme Corp")
            t_date = st.date_input("Agreement Date")
            
            lbl = "Salary (INR)" if "Employment" in t_type else "Contract Value / Fee"
            if "NDA" in t_type: lbl = "Purpose of Disclosure"
            
            t_val = st.text_input(lbl, placeholder="e.g. 5,00,000 or Project Alpha")
            
            generate_btn = st.button(" Generate Document", type="primary", use_container_width=True)

        with col2:
            if generate_btn:
                 from utils import templates
                 draft = templates.get_template(
                     t_type, 
                     name=t_name, 
                     date=t_date.strftime("%Y-%m-%d"), 
                     amount=t_val,
                     language=t_lang 
                 )
                 st.session_state.generated_template = draft
                 
            if st.session_state.generated_template:
                st.markdown("""
                <div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                    <h3 style="margin-top:0; color: #1e293b;">📄 Draft Preview</h3>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(st.session_state.generated_template)
                
                st.download_button(
                    "⬇️ Download Contract (.md)", 
                    st.session_state.generated_template, 
                    file_name=f"{t_type.replace(' ', '_')}.md",
                    mime="text/markdown",
                    type="secondary"
                )
            else:
                # Placeholder State
                st.info("👈 Fill in the details on the left and click Generate to see your draft here.")

    # --- PAGE 4: SETTINGS ---
    elif page == "Settings":
        st.header("⚙️ Application Settings")
        st.info("Current Mode: **Local Offline Analysis**")
        st.write("All analysis runs locally on your machine using the `spaCy` NLP engine and rule-based heuristics.")
        st.write(f"Logged in as: **{st.session_state.user_display_name}** ({st.session_state.username})")
        
        st.markdown("---")
        
        st.subheader("🛡️ Compliance & Audit Trail")
        st.write("View the chronological log of all analysis and access activities.")
        
        from utils import audit_logger
        
        # Load Logs
        logs = audit_logger.get_logs()
        
        if logs:
            for log in logs:
                # Icon based on action
                icon = "📝"
                if "Login" in log['action']: icon = "🔐"
                elif "Analysis" in log['action']: icon = "🔍"
                elif "Export" in log['action']: icon = "📥"
                
                with st.expander(f"{icon} {log['action']} - {log['timestamp']}"):
                    st.json(log)
        else:
            st.info("No audit logs found.")
