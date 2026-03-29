import json
import time

import streamlit as st

from utils.orchestrator import WorkflowOrchestrator


st.set_page_config(
    page_title="TrustTrace AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_orchestrator():
    return WorkflowOrchestrator()


def inject_css():
    st.markdown(
        """
        <style>
            :root {
                --bg: #0d1117;
                --surface: #161b22;
                --surface-soft: #1f2630;
                --text: #e6edf3;
                --muted: #9da7b3;
                --border: rgba(255, 255, 255, 0.08);
                --ok: #2ea043;
                --warn: #d29922;
                --bad: #f85149;
                --accent: #58a6ff;
            }
            .stApp {
                background: radial-gradient(circle at top right, #101a2b 0%, var(--bg) 38%);
                color: var(--text);
            }
            .block-container {
                padding-top: 1.4rem;
                padding-bottom: 2rem;
                max-width: 1280px;
            }
            .hero-card, .panel-card, .metric-shell, .welcome-card, .mini-card {
                background: linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%);
                border: 1px solid var(--border);
                border-radius: 18px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
            }
            .hero-card {
                padding: 1.4rem 1.4rem 1.2rem 1.4rem;
                margin-bottom: 1rem;
            }
            .hero-title {
                font-size: 2rem;
                font-weight: 700;
                letter-spacing: 0.2px;
                margin: 0;
            }
            .hero-tagline {
                margin: 0.4rem 0 0.2rem 0;
                color: #c9d1d9;
                font-size: 1.05rem;
                font-weight: 500;
            }
            .hero-subtitle {
                margin: 0.15rem 0 0 0;
                color: var(--muted);
                font-size: 0.93rem;
            }
            .panel-card {
                padding: 1rem 1rem 1.2rem 1rem;
                margin-bottom: 1rem;
            }
            .section-title {
                font-size: 1.08rem;
                font-weight: 650;
                margin-bottom: 0.7rem;
                color: #ecf2f8;
            }
            .risk-banner {
                border-radius: 14px;
                padding: 0.85rem 1rem;
                font-weight: 540;
                margin: 0.3rem 0 1rem 0;
                border: 1px solid var(--border);
            }
            .risk-high {
                background: rgba(248, 81, 73, 0.13);
                border-color: rgba(248, 81, 73, 0.45);
                color: #ffd5d2;
            }
            .risk-medium {
                background: rgba(210, 153, 34, 0.16);
                border-color: rgba(210, 153, 34, 0.45);
                color: #ffedc4;
            }
            .risk-low {
                background: rgba(46, 160, 67, 0.14);
                border-color: rgba(46, 160, 67, 0.45);
                color: #d3f4dc;
            }
            .badge {
                display: inline-block;
                border-radius: 999px;
                padding: 0.22rem 0.62rem;
                font-size: 0.76rem;
                margin-right: 0.35rem;
                margin-bottom: 0.35rem;
                border: 1px solid var(--border);
            }
            .badge-high { background: rgba(248,81,73,0.14); color: #ffd5d2; border-color: rgba(248,81,73,0.42); }
            .badge-medium { background: rgba(210,153,34,0.16); color: #ffedc4; border-color: rgba(210,153,34,0.42); }
            .badge-low { background: rgba(46,160,67,0.14); color: #d3f4dc; border-color: rgba(46,160,67,0.42); }
            .stTextArea textarea {
                min-height: 180px;
                border-radius: 12px;
                background-color: var(--surface);
                border: 1px solid var(--border);
                color: var(--text);
                font-size: 0.95rem;
            }
            .stButton > button {
                border-radius: 11px;
                border: 1px solid rgba(88,166,255,0.35);
                font-weight: 600;
                padding: 0.45rem 0.95rem;
            }
            .sample-title {
                color: var(--muted);
                font-size: 0.86rem;
                margin: 0.2rem 0 0.45rem 0;
            }
            .mini-card {
                padding: 0.8rem 0.9rem;
                margin-bottom: 0.55rem;
            }
            .mini-title {
                margin: 0;
                font-size: 0.93rem;
                font-weight: 640;
                color: #eaf2fb;
            }
            .mini-desc {
                margin-top: 0.25rem;
                color: var(--muted);
                font-size: 0.86rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_risk_level(result):
    decision = result.get("decision", {})
    risk = str(decision.get("final_risk_category", "Unknown")).strip().lower()
    if "high" in risk:
        return "High"
    if "medium" in risk:
        return "Medium"
    if "low" in risk:
        return "Low"
    return "Unknown"


def fallback_safety_score(result):
    score = result.get("user_safety_score")
    if isinstance(score, (int, float)):
        return int(max(0, min(100, score)))
    risk_level = get_risk_level(result)
    if risk_level == "High":
        return 25
    if risk_level == "Medium":
        return 62
    if risk_level == "Low":
        return 92
    return 50


def risk_banner(level):
    if level == "High":
        return "risk-high", "High risk detected. Avoid replying, clicking links, or sharing OTP/bank details."
    if level == "Medium":
        return "risk-medium", "Medium risk detected. Verify identity through official channels before any action."
    return "risk-low", "Low risk detected. Message appears safer, but continue normal verification hygiene."


def risk_badge_class(level):
    return {"High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}.get(level, "badge-medium")


SAMPLE_MESSAGES = {
    "Bank KYC Scam": "Dear customer, your KYC is pending. Your account will be blocked in 2 hours. Verify now: http://secure-kyc-update.in",
    "UPI Collect Scam": "You have received a collect request of Rs 25,000 from SBI Rewards. Approve UPI PIN immediately to claim cashback.",
    "Lottery Scam": "Congratulations! You won Rs 12,50,000 in the National Lucky Draw. Pay processing fee today to release funds.",
    "Fake Job Offer": "We are hiring for remote data entry with Rs 45,000 salary. Pay Rs 1,999 registration to confirm your seat.",
    "Safe Bank Alert": "Your transaction of Rs 1,250 on card ending 4482 was successful. If not you, call official helpline on bank website.",
}


if "message_input" not in st.session_state:
    st.session_state["message_input"] = ""
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None

inject_css()
orchestrator = get_orchestrator()


with st.sidebar:
    st.markdown("### 🛡️ TrustTrace AI")
    st.caption("Enterprise Fraud Intelligence")
    st.markdown("---")
    st.markdown("#### How it works")
    for step in ["1. Detect", "2. Retrieve", "3. Analyze", "4. Decide", "5. Act", "6. Audit"]:
        st.markdown(f"- {step}")
    st.markdown("---")
    sample_pick = st.selectbox("Optional sample test message", ["None"] + list(SAMPLE_MESSAGES.keys()))
    if sample_pick != "None" and st.button("Use selected sample", use_container_width=True):
        st.session_state["message_input"] = SAMPLE_MESSAGES[sample_pick]
    st.markdown("---")
    st.caption("Built for ET Hackathon")


st.markdown(
    """
    <div class="hero-card">
        <p class="hero-title">TrustTrace AI Fraud Command Center</p>
        <p class="hero-tagline">Autonomous AI agent for scam detection, explanation, and response.</p>
        <p class="hero-subtitle">Analyze suspicious SMS, email, UPI, and phishing messages using multi-agent AI + RAG.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown('<div class="panel-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Analyze a Suspicious Message</div>', unsafe_allow_html=True)

sample_cols = st.columns(5)
for idx, label in enumerate(SAMPLE_MESSAGES.keys()):
    if sample_cols[idx].button(label, use_container_width=True):
        st.session_state["message_input"] = SAMPLE_MESSAGES[label]
st.markdown('<div class="sample-title">Quick sample scenarios</div>', unsafe_allow_html=True)

message = st.text_area(
    "Message Input",
    key="message_input",
    label_visibility="collapsed",
    placeholder="Paste an SMS, email, UPI request, or suspicious message here...",
)

analyze_clicked = st.button("Analyze Message", type="primary", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

if analyze_clicked:
    if not message.strip():
        st.warning("Please enter a suspicious message or choose a sample message first.")
    else:
        with st.status("AI agents are processing your message...", expanded=True) as status:
            for step in [
                "Detection Agent running...",
                "Retrieval Agent searching similar fraud cases...",
                "Analysis Agent evaluating scam indicators...",
                "Decision Agent calculating final risk...",
                "Audit Agent generating trace...",
            ]:
                st.write(step)
                time.sleep(0.15)
            result = orchestrator.process_message(message)
            status.update(label="Analysis completed.", state="complete")
        st.session_state["last_result"] = result

if not st.session_state["last_result"]:
    st.markdown(
        """
        <div class="welcome-card" style="padding: 1.15rem 1.2rem;">
            <div class="section-title" style="margin-bottom: 0.4rem;">Welcome to the Fraud Analysis Dashboard</div>
            <div style="color:#9da7b3; font-size: 0.92rem;">
                Paste suspicious content such as:
                <ul>
                    <li>SMS claiming urgent KYC/account block</li>
                    <li>UPI collect requests asking PIN approval</li>
                    <li>Lottery or prize messages requiring fee payment</li>
                    <li>Fake job offers demanding registration money</li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

result = st.session_state["last_result"]

if result.get("status") == "error":
    st.error("Workflow Error / Escalation Triggered")
    st.write(result.get("message", "An unexpected error occurred in agent orchestration."))
    st.code(str(result.get("error_details", "No details available.")))
    with st.expander("Audit Trail"):
        st.json(result.get("audit_trail", {}))
    st.stop()

risk_level = get_risk_level(result)
safety_score = fallback_safety_score(result)
decision = result.get("decision", {})
detection = result.get("detection", {})
analysis = result.get("analysis") or {}
action = result.get("action") or {}

classification = decision.get("final_risk_category", "N/A")
confidence = detection.get("confidence", detection.get("risk_score", "N/A"))
risk_css, risk_text = risk_banner(risk_level)

metric_cols = st.columns(4)
metric_cols[0].metric("Classification", str(classification))
metric_cols[1].metric("Confidence", str(confidence))
metric_cols[2].metric("Risk Level", risk_level)
metric_cols[3].metric("Safety Score", f"{safety_score}/100", delta=safety_score - 50)

st.progress(safety_score / 100, text=f"Safety Score Meter: {safety_score}/100")
st.markdown(
    f'<div class="risk-banner {risk_css}"><span class="badge {risk_badge_class(risk_level)}">{risk_level} Risk</span> {risk_text}</div>',
    unsafe_allow_html=True,
)

tabs = st.tabs(
    [
        "Detection Result",
        "Scam Indicators",
        "Similar Fraud Cases",
        "Suggested Actions",
        "Audit Trail",
        "Complaint Draft",
    ]
)

with tabs[0]:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Detection Result</div>', unsafe_allow_html=True)
    st.write(f"**Classification:** {classification}")
    st.write(f"**Confidence:** {confidence}")
    st.write(f"**Reason:** {decision.get('justification', 'No justification provided.')}")
    final_expl = decision.get("justification", "")
    if final_expl:
        st.text_area("Final Explanation (copy-friendly)", value=final_expl, height=120)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Scam Indicators</div>', unsafe_allow_html=True)
    urgency = str(analysis.get("urgency_level", "Unknown"))
    impersonation = "Yes" if analysis.get("impersonation_detected") else "No"
    manipulation = str(analysis.get("malicious_intent", "Unknown"))
    phish = "Yes" if analysis.get("suspicious_links") else "No"
    st.markdown(
        f"""
        <span class="badge {risk_badge_class(risk_level)}">Urgency: {urgency}</span>
        <span class="badge {risk_badge_class(risk_level)}">Impersonation: {impersonation}</span>
        <span class="badge {risk_badge_class(risk_level)}">Financial Manipulation: {manipulation}</span>
        <span class="badge {risk_badge_class(risk_level)}">Phishing / Social Engineering: {phish}</span>
        """,
        unsafe_allow_html=True,
    )
    links = analysis.get("suspicious_links", []) or []
    if links:
        st.write("**Suspicious Links**")
        for link in links:
            st.code(link, language=None)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[2]:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Similar Fraud Cases (RAG)</div>', unsafe_allow_html=True)
    rag_cases = result.get("rag_context") or []
    if rag_cases:
        for i, case in enumerate(rag_cases, start=1):
            title = f"Case {i} | Similarity Distance: {case.get('distance', 'N/A')}"
            snippet = case.get("text", "No case text available.")
            explanation = case.get("explanation", "No explanation available.")
            st.markdown(
                f"""
                <div class="mini-card">
                    <p class="mini-title">{title}</p>
                    <div class="mini-desc">{snippet}</div>
                    <div class="mini-desc"><strong>Why it matches:</strong> {explanation}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No similar fraud cases retrieved for this message.")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[3]:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Suggested Actions</div>', unsafe_allow_html=True)
    actions = action.get("suggested_actions", []) or []
    if actions:
        for act in actions:
            icon = "🚨" if risk_level in ["High", "Medium"] else "✅"
            st.markdown(
                f"""
                <div class="mini-card">
                    <p class="mini-title">{icon} Recommended Action</p>
                    <div class="mini-desc">{act}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No additional actions suggested for this message.")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[4]:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Audit Trail</div>', unsafe_allow_html=True)
    audit_data = result.get("audit_trail", {})
    audit_text = json.dumps(audit_data, indent=2)
    st.text_area("Audit Trail (copy-friendly)", value=audit_text, height=220)
    with st.expander("View structured JSON"):
        st.json(audit_data)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[5]:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Complaint Draft</div>', unsafe_allow_html=True)
    complaint = action.get("complaint_template", "")
    if complaint and risk_level in ["High", "Medium"]:
        st.text_area("Complaint Draft (copy-friendly)", value=complaint, height=220)
    else:
        st.info("Complaint draft is not applicable for the current risk level.")
    st.markdown("</div>", unsafe_allow_html=True)
