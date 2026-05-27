import streamlit as st
# Importing core functions seamlessly from the isolated backend file
from backend_engine import generate_election_response, get_audit_logs_count

# High-end layout page properties injection
st.set_page_config(
    page_title="DemocracyAI Dashboard", 
    page_icon="🗳️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Injection to enhance UI polish and depth
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stChatInputContainer { padding-bottom: 20px; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #00ffcc; font-weight: bold; }
    .stAlert { border-left: 5px solid #00ffcc; background-color: #161b22; }
    h1 { color: #ffffff; font-weight: 800; letter-spacing: -0.5px; }
    h3 { color: #8b949e; }
    .sidebar .sidebar-content { background-image: linear-gradient(#161b22, #0e1117); }
    </style>
""", unsafe_allow_html=True)

# 1. Premium Left Control Panel Sidebar Layout
with st.sidebar:
    st.title("⚙️ Workspace Engine")
    st.markdown("---")
    
    # Capture slider state values to pass down to backend functions smoothly
    sidebar_temperature = st.slider(
        label="Model Variance (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1,
        help="Lower values yield strictly precise, predictable, and factual auditing answers."
    )
    
    st.markdown("---")
    st.subheader("📊 Session Status Metrics")
    
    # Dynamic live interface counters connecting directly to backend DB analytics
    total_logs = get_audit_logs_count()
    st.metric(label="Total Audited Logs Saved", value=f"{total_logs} Rows")
    
    st.markdown("---")
    st.success("🔒 SQLite Integration Stable")
    st.info("Core Engine: `gemini-1.5-flash` via Unified Client Platform.")

# 2. Main Dashboard Headers Rendering
st.title("🗳️ DemocracyAI Verification System")
st.subheader("Data-Driven Election Transparency & Policy Verification Engine")
st.markdown("---")

# Setup persistent global browser session data buffers
if "messages" not in st.session_state:
    st.session_state.messages = []

# Stream historic interaction tracks elegantly to the UI viewport
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Interactive Input Tracking Interface Window
user_input = st.chat_input("Enter policy verification prompts, verification claims, or auditing parameters...")

if user_input:
    # Render and save user message tracks instantaneously
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Trigger styled visual loader block during computation runtime processing
    with st.spinner("Decoding dataset patterns & generating cryptographically logged trace..."):
        ai_output = generate_election_response(user_input, sidebar_temperature)
        
    # Render and store premium formatted system output
    with st.chat_message("assistant"):
        st.markdown(ai_output)
    st.session_state.messages.append({"role": "assistant", "content": ai_output})
    
    # Force immediate layout refresh to synchronize the sidebar counter numbers instantly
    st.rerun()