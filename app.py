"""
app.py
Samsung Fire & Marine Insurance AI Agent - Streamlit Integrated Dashboard
Run: streamlit run app.py
"""

import streamlit as st
import sys, json, os, tempfile, csv
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="Samsung Fire & Marine AI Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
* { font-family: 'Noto Sans', sans-serif; }

.stApp { background-color: #f4f6f9; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #003876 0%, #0057b8 100%);
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] input { color: #333 !important; }

.stButton > button {
    background-color: white !important;
    color: #0057b8 !important;
    border: 2px solid #0057b8 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
}
.stButton > button:hover {
    background-color: #0057b8 !important;
    color: white !important;
}
[data-testid="stSidebar"] .stButton > button {
    background-color: white !important;
    color: #003876 !important;
    border: 2px solid white !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] .stButton > button p,
[data-testid="stSidebar"] .stButton > button span,
[data-testid="stSidebar"] .stButton > button div {
    color: #003876 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #003876 !important;
    color: white !important;
    border-color: #003876 !important;
}
[data-testid="stSidebar"] .stButton > button:hover p,
[data-testid="stSidebar"] .stButton > button:hover span,
[data-testid="stSidebar"] .stButton > button:hover div {
    color: white !important;
}

.stTabs [data-baseweb="tab-list"] {
    background-color: white;
    border-radius: 12px;
    padding: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 500;
    color: #666;
    padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    background-color: #0057b8 !important;
    color: white !important;
}

.chat-user {
    background: #0057b8;
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 16px;
    margin: 8px 0;
    margin-left: 20%;
    font-size: 0.95rem;
    line-height: 1.7;
    word-break: keep-all;
}
.chat-bot {
    background: white;
    color: #1a1a2e;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 16px;
    margin: 8px 0;
    margin-right: 20%;
    font-size: 0.95rem;
    line-height: 1.7;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border-left: 3px solid #0057b8;
    word-break: keep-all;
}
.chat-bot ul, .chat-bot ol { padding-left: 1.5em; margin: 4px 0; }
.chat-bot li { margin: 2px 0; line-height: 1.7; }

.chat-label-user { text-align:right; font-size:0.75rem; color:#999; margin-bottom:2px; }
.chat-label-bot  { font-size:0.75rem; color:#999; margin-bottom:2px; }

[data-testid="stVerticalBlockBorderWrapper"] {
    height: 500px !important;
    overflow-y: auto !important;
}

.policy-card {
    background: rgba(255,255,255,0.15);
    border-radius: 10px;
    padding: 12px;
    margin: 8px 0;
    border: 1px solid rgba(255,255,255,0.3);
}
.policy-card p { margin: 3px 0; font-size: 0.85rem; }

.log-row {
    background: white;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    font-size: 0.88rem;
    border-left: 4px solid #e0e0e0;
}
.log-row.complaint { border-left-color: #ff9800; }
.log-row.handoff   { border-left-color: #f44336; }
.log-row.claim     { border-left-color: #2196f3; }
.log-row.normal    { border-left-color: #4caf50; }

.badge { border-radius:20px; padding:2px 10px; font-size:0.78rem; font-weight:600; }
.badge-complaint { background:#fff3e0; color:#e65100; }
.badge-handoff   { background:#fce4ec; color:#c62828; }
.badge-claim     { background:#e3f2fd; color:#1565c0; }
.badge-normal    { background:#e8f5e9; color:#2e7d32; }
.badge-intent    { background:#f3e5f5; color:#6a1b9a; }
.badge-blue   { background:#e8f0fe; color:#0057b8; border-radius:20px; padding:2px 10px; font-size:0.8rem; font-weight:500; }
.badge-green  { background:#e8f5e9; color:#2e7d32; border-radius:20px; padding:2px 10px; font-size:0.8rem; font-weight:500; }
.badge-orange { background:#fff3e0; color:#e65100; border-radius:20px; padding:2px 10px; font-size:0.8rem; font-weight:500; }
.badge-red    { background:#fce4ec; color:#c62828; border-radius:20px; padding:2px 10px; font-size:0.8rem; font-weight:500; }

.complaint-row {
    background: white;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    font-size: 0.88rem;
}
[data-testid="stFileUploader"] {
    background: #f0f4ff;
    border: 2px dashed #0057b8;
    border-radius: 10px;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)


def init_session():
    defaults = {
        "mode":            "user",
        "logged_in":       False,
        "admin_logged_in": False,
        "customer_info":   None,
        "chat_history":    [],
        "claim_step":      None,
        "claim_domain":    None,
        "complaint_id":    None,
        "handoff_done":    False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

BASE_PATH    = Path(__file__).parent
AUDIT_LOG    = BASE_PATH / "audit_log.csv"
COMPLAINT_DB = BASE_PATH / "complaint_db.csv"
HANDOFF_DB   = BASE_PATH / "handoff_db.csv"
CUSTOMER_DB  = BASE_PATH / "customers.csv"

AUDIT_HEADERS = [
    "log_id", "timestamp", "customer_id", "customer_name",
    "query", "intent", "domains", "answer_preview",
    "claim_status", "is_complaint", "is_handoff"
]

ADMIN_ID  = "admin"
ADMIN_PWD = "1234"


@st.cache_resource(show_spinner="🔄 Initializing AI Engine...")
def load_agents():
    from utils.llm_setup import llm, PRODUCT_TO_DOMAIN
    from agents.customer_agent import login, format_customer_info
    from agents.rag_agent import search_and_answer
    from agents.claim_agent import handle_claim
    from agents.complaint_agent import check_and_record
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    return {
        "llm":                  llm,
        "PRODUCT_TO_DOMAIN":    PRODUCT_TO_DOMAIN,
        "login":                login,
        "format_customer_info": format_customer_info,
        "search_and_answer":    search_and_answer,
        "handle_claim":         handle_claim,
        "check_and_record":     check_and_record,
        "PromptTemplate":       PromptTemplate,
        "StrOutputParser":      StrOutputParser,
    }

try:
    agents = load_agents()
except Exception as e:
    import traceback
    st.error(f"❌ Agent load failed: {e}")
    st.code(traceback.format_exc())
    st.stop()


BLOCKED_KEYWORDS = ["씨발", "개새끼", "병신", "존나", "ㅅㅂ", "ㅂㅅ", "fuck", "shit", "asshole", "bastard"]

INTENT_ROUTER_PROMPT = """
You are a question classifier AI for Samsung Fire & Marine Insurance customer center.

[Logged-in Customer Information]
{customer_info}

[Customer Question]
{query}

Respond in the following JSON format only. No other text allowed.

{{
  "intent": "coverage_inquiry or policy_inquiry or non_enrolled_inquiry or claim or general_inquiry or out_of_scope",
  "subscribed_domains": ["only domains related to customer's actual enrolled products"],
  "unsubscribed_domains": ["domains related to the question but customer is not enrolled"],
  "needs_document_guide": true or false,
  "sub_queries": ["key questions to use for policy search"]
}}

Classification criteria:
- policy_inquiry: Customer asking about their current insurance enrollment status
- coverage_inquiry: Questions about coverage scope, payment eligibility of enrolled insurance
- non_enrolled_inquiry: Questions or enrollment inquiries about insurance not yet enrolled in
- claim: Actual accident occurrence or intention to file insurance claim
- general_inquiry: General questions related to insurance
- out_of_scope: Questions completely unrelated to insurance

Domain classification rules:
- subscribed_domains: Cross-reference customer enrollment info with question content, include only actually enrolled ones
- unsubscribed_domains: Domains related to question but customer is not enrolled in
- auto/vehicle/accident/driving → auto
- cancer/tumor/diagnosis/chemotherapy → cancer
- dental/implant/scaling/cavity → teeth
- precedent/ruling/court/dispute → precedent
- Include all relevant domains if multiple products are involved
"""

OUT_OF_SCOPE_PROMPT = """
The customer asked a question unrelated to insurance.
Respond naturally and briefly, then end with a message encouraging insurance-related questions.
Example: "If you have any insurance-related questions, feel free to ask anytime 😊"
Always respond in English.

Customer Question: {query}
Answer:"""

POLICY_INFO_PROMPT = """
Check the customer's insurance enrollment information below and kindly provide only the list of enrolled insurance products.
Do NOT explain policy details. Just share the enrollment information and ask if there's anything else needed.
Always respond in English.

[Customer Policy Information]
{customer_info}

Answer:"""


def log_conversation(customer_info, query, intent, domains, answer,
                     claim_status="-", is_complaint=False, is_handoff=False):
    file_exists = AUDIT_LOG.exists()
    with open(AUDIT_LOG, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=AUDIT_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "log_id":         f"LOG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "customer_id":    customer_info.get("customer_id", ""),
            "customer_name":  customer_info.get("name", ""),
            "query":          query,
            "intent":         intent,
            "domains":        ", ".join(domains) if domains else "-",
            "answer_preview": answer[:100],
            "claim_status":   claim_status,
            "is_complaint":   is_complaint,
            "is_handoff":     is_handoff,
        })


def router_agent(user_query: str) -> dict:
    a = agents
    customer_info_str = a["format_customer_info"](st.session_state["customer_info"])
    prompt = a["PromptTemplate"].from_template(INTENT_ROUTER_PROMPT)
    chain  = prompt | a["llm"] | a["StrOutputParser"]()
    result = chain.invoke({"customer_info": customer_info_str, "query": user_query})
    result = result.strip().replace("```json", "").replace("```", "")
    return json.loads(result)


def execute(user_query: str, image_paths: list = None) -> str:
    a = agents
    customer_info    = st.session_state["customer_info"]
    customer_context = a["format_customer_info"](customer_info)

    history = st.session_state.get("chat_history", [])
    recent  = history[-6:] if len(history) > 6 else history
    conversation_history = "\n".join([
        f"{'Customer' if m['role'] == 'user' else 'AI'}: {m['content'][:200]}"
        for m in recent
    ])

    if any(k in user_query.lower() for k in BLOCKED_KEYWORDS):
        return "⚠️ Your message contains inappropriate language.\nPlease rephrase your question and we'll be happy to assist you."

    try:
        routing = router_agent(user_query)
    except Exception as e:
        return f"❌ Router error: {e}"

    intent               = routing["intent"]
    subscribed_domains   = routing.get("subscribed_domains", [])
    unsubscribed_domains = routing.get("unsubscribed_domains", [])

    domain_to_product = {"auto": "P-C", "cancer": "P-B", "teeth": "P-D"}
    riders_list = []
    for p in customer_info.get("policies", []):
        pid = p.get("product_id", "")
        if any(domain_to_product.get(d) == pid for d in subscribed_domains):
            riders_list.append(p.get("riders", ""))
    riders = ";".join([r for r in riders_list if r])

    if intent == "out_of_scope":
        prompt = a["PromptTemplate"].from_template(OUT_OF_SCOPE_PROMPT)
        chain  = prompt | a["llm"] | a["StrOutputParser"]()
        answer = chain.invoke({"query": user_query})

    elif intent == "policy_inquiry":
        prompt = a["PromptTemplate"].from_template(POLICY_INFO_PROMPT)
        chain  = prompt | a["llm"] | a["StrOutputParser"]()
        answer = chain.invoke({"customer_info": customer_context})

    elif intent == "coverage_inquiry":
        answer = a["search_and_answer"](
            user_query, subscribed_domains, customer_context,
            conversation_history=conversation_history, riders=riders
        )
        if unsubscribed_domains:
            domain_en = {"auto": "Auto Insurance", "cancer": "Cancer Insurance", "teeth": "Dental Insurance"}
            names = [domain_en.get(d, d) for d in unsubscribed_domains]
            answer += f"\n\n💡 {', '.join(names)} is not currently enrolled. Visit www.samsungfire.com to learn more."

    elif intent == "non_enrolled_inquiry":
        all_domains = subscribed_domains + unsubscribed_domains
        answer = a["search_and_answer"](
            user_query, all_domains, "",
            conversation_history=conversation_history
        )
        answer += "\n\n📌 To enroll, please visit www.samsungfire.com"

    elif intent == "claim":
        domain = subscribed_domains[0] if subscribed_domains else "auto"
        st.session_state["claim_step"]   = "waiting_docs"
        st.session_state["claim_domain"] = domain
        coverage = a["search_and_answer"](
            user_query, subscribed_domains, customer_context,
            conversation_history=conversation_history, riders=riders
        )
        claim  = a["handle_claim"](customer_info, domain, user_query)
        answer = f"{coverage}\n\n{claim}"
        answer += "\n\n※ Final payment is subject to actual review results."
        if len(subscribed_domains) > 1:
            domain_en = {"auto": "Auto Insurance", "cancer": "Cancer Insurance", "teeth": "Dental Insurance"}
            names = [domain_en.get(d, d) for d in subscribed_domains]
            answer += f"\n\n💡 {', '.join(names)} may all be relevant. Each can be filed separately in the Claims tab."

    else:
        answer = a["search_and_answer"](
            user_query, subscribed_domains or unsubscribed_domains, "",
            conversation_history=conversation_history
        )

    is_complaint = False
    is_handoff   = False
    if intent != "out_of_scope":
        try:
            if st.session_state.get("handoff_done"):
                complaint_msg = None
            else:
                complaint_msg = a["check_and_record"](customer_info, user_query, answer)

            if complaint_msg:
                is_complaint = True
                if "Specialist Agent" in complaint_msg or "전문 상담원" in complaint_msg:
                    is_handoff = True
                    st.session_state["handoff_done"] = True
                answer += complaint_msg
        except Exception:
            pass

    log_conversation(
        customer_info=customer_info, query=user_query, intent=intent,
        domains=subscribed_domains + unsubscribed_domains, answer=answer,
        claim_status=st.session_state.get("claim_step") or "-",
        is_complaint=is_complaint, is_handoff=is_handoff,
    )
    return answer


def add_message(role: str, content: str):
    st.session_state["chat_history"].append({
        "role": role, "content": content,
        "time": datetime.now().strftime("%H:%M"),
    })


def render_chat():
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-label-user">{msg["time"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-label-bot">🛡️ AI Assistant · {msg["time"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-bot">{msg["content"]}</div>', unsafe_allow_html=True)


def load_csv(path):
    if path.exists():
        return pd.read_csv(path, encoding="utf-8-sig")
    return pd.DataFrame()


def make_bar_chart(series):
    df = series.reset_index()
    df.columns = ["label", "count"]
    fig = px.bar(df, x="label", y="count", color_discrete_sequence=["#0057b8"])
    fig.update_layout(
        xaxis=dict(tickangle=0),
        xaxis_title="", yaxis_title="Count",
        margin=dict(t=20, b=40), height=300
    )
    return fig


# ==========================================
# Sidebar
# ==========================================
with st.sidebar:
    st.markdown("## 🛡️ Samsung Fire & Marine AI")
    st.markdown("---")
    mode = st.radio("Mode", ["👤 Customer", "🔐 Admin"], key="mode_radio", horizontal=True)
    st.session_state["mode"] = "admin" if "Admin" in mode else "user"
    st.markdown("---")

    if st.session_state["mode"] == "user":
        if not st.session_state["logged_in"]:
            st.markdown("### Login")
            cid = st.text_input("Customer ID", placeholder="CUST-0001", key="input_cid")
            pwd = st.text_input("Password", type="password", placeholder="****", key="input_pwd")
            if st.button("Login", key="btn_login"):
                if cid and pwd:
                    info = agents["login"](cid, pwd)
                    if info:
                        st.session_state["logged_in"]     = True
                        st.session_state["customer_info"] = info
                        add_message("bot", f"Hello, {info['name']}! 😊\nI'm Samsung Fire & Marine AI Assistant.\nFeel free to ask any insurance-related questions.")
                        st.rerun()
                    else:
                        st.error("Please check your ID or password.")
                else:
                    st.warning("Please enter your ID and password.")
        else:
            info = st.session_state["customer_info"]
            st.markdown(f"### 👤 {info['name']}")
            st.markdown("---")
            st.markdown("**📋 Enrolled Insurance**")
            for p in info["policies"]:
                years = datetime.now().year - int(p["joined_year"])
                st.markdown(f"""
<div class="policy-card">
  <p>🔵 <b>{p['product_name']}</b></p>
  <p>📅 Enrolled: {p['joined_year']} ({years} years)</p>
  <p>💰 Coverage: {p['coverage_limit']}</p>
  <p>➕ {p['riders']}</p>
</div>
""", unsafe_allow_html=True)
            st.markdown("---")
            if st.button("Logout", key="btn_logout"):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()
    else:
        if not st.session_state["admin_logged_in"]:
            st.markdown("### Admin Login")
            aid = st.text_input("Admin ID", key="admin_id")
            apw = st.text_input("Password", type="password", key="admin_pw")
            if st.button("Login", key="btn_admin_login"):
                if aid == ADMIN_ID and apw == ADMIN_PWD:
                    st.session_state["admin_logged_in"] = True
                    st.rerun()
                else:
                    st.error("Invalid ID or password.")
        else:
            st.markdown("### ✅ Admin Mode")
            st.markdown("---")
            st.markdown("**📁 Data Status**")
            st.markdown(f"- audit_log: {'✅' if AUDIT_LOG.exists() else '❌'}")
            st.markdown(f"- complaint_db: {'✅' if COMPLAINT_DB.exists() else '❌'}")
            st.markdown(f"- handoff_db: {'✅' if HANDOFF_DB.exists() else '❌'}")
            st.markdown("---")
            st.markdown("**📅 Date Filter**")
            date_from = st.date_input("From", value=datetime.now().date() - timedelta(days=7))
            date_to   = st.date_input("To",   value=datetime.now().date())
            st.markdown("---")
            if st.button("Logout", key="btn_admin_logout"):
                st.session_state["admin_logged_in"] = False
                st.rerun()


# ==========================================
# Main Content
# ==========================================
if st.session_state["mode"] == "user":
    if not st.session_state["logged_in"]:
        st.markdown("""
        <div style="text-align:center; padding:80px 0;">
            <div style="font-size:4rem;">🛡️</div>
            <h1 style="color:#0057b8; font-weight:700; margin:16px 0 8px;">Samsung Fire & Marine AI Assistant</h1>
            <p style="color:#666; font-size:1.1rem;">From policy inquiries to claims, AI will assist you.</p>
            <br>
            <div style="display:inline-block; background:white; border-radius:12px; padding:20px 36px; box-shadow:0 2px 12px rgba(0,0,0,0.08); text-align:left;">
                <p style="color:#333; font-weight:600; margin:0 0 12px; font-size:0.95rem;">🔐 Test Account Information</p>
                <p style="color:#555; margin:4px 0; font-size:0.9rem;">Customer ID : CUST-0001 ~ CUST-0050</p>
                <p style="color:#555; margin:4px 0; font-size:0.9rem;">Admin ID : admin</p>
                <p style="color:#555; margin:4px 0; font-size:0.9rem;">Password : 1234 (common)</p>
            </div>
            <br><br>
            <p style="color:#999;">← Please login on the left</p>
            <br>
            <p style="color:#bbb; font-size:0.85rem;">
                For more information, visit our 
                <a href="https://github.com/wjdgudwns/22.5_insurance_agent_eng" 
                   target="_blank" style="color:#0057b8;">GitHub Repository</a>
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        tab_chat, tab_claim = st.tabs(["💬 Chat", "📋 File a Claim"])

        with tab_chat:
            st.markdown("### 💬 AI Insurance Consultation")

            chat_box = st.container(height=500)
            with chat_box:
                render_chat()

            if (st.session_state["chat_history"] and
                    st.session_state["chat_history"][-1]["role"] == "user"):
                last_query = st.session_state["chat_history"][-1]["content"]
                with st.spinner("🤔 Generating response..."):
                    response = execute(last_query)
                add_message("bot", response)
                st.rerun()

            st.markdown("---")

            with st.form(key="chat_form", clear_on_submit=True):
                col_input, col_btn = st.columns([5, 1])
                with col_input:
                    user_input = st.text_input(
                        "Question",
                        placeholder="Ask any insurance-related question...",
                        label_visibility="collapsed",
                    )
                with col_btn:
                    submitted = st.form_submit_button("Send", use_container_width=True)

            if submitted and user_input.strip():
                add_message("user", user_input.strip())
                st.rerun()

            if st.session_state.get("claim_step") == "waiting_docs":
                st.markdown("---")
                st.markdown("#### 📎 Attach Documents")
                st.info("Please attach claim documents as images. (JPG, PNG, PDF)")
                uploaded_files = st.file_uploader(
                    "Upload document images",
                    type=["jpg", "jpeg", "png", "pdf"],
                    accept_multiple_files=True,
                    label_visibility="collapsed",
                    key="doc_uploader"
                )
                if uploaded_files:
                    cols = st.columns(min(len(uploaded_files), 4))
                    for i, f in enumerate(uploaded_files):
                        with cols[i % 4]:
                            if f.type.startswith("image"):
                                st.image(f, caption=f.name, use_container_width=True)
                            else:
                                st.markdown(f"📄 {f.name}")
                    if st.button("📤 Submit & Verify Documents", key="btn_submit_docs"):
                        with tempfile.TemporaryDirectory() as tmpdir:
                            tmp_paths = []
                            for f in uploaded_files:
                                tmp_path = os.path.join(tmpdir, f.name)
                                with open(tmp_path, "wb") as fp:
                                    fp.write(f.read())
                                tmp_paths.append(tmp_path)
                            with st.spinner("🔍 Analyzing documents..."):
                                from agents.claim_agent import handle_claim
                                result = handle_claim(
                                    customer_info=st.session_state["customer_info"],
                                    domain=st.session_state["claim_domain"],
                                    query="document submission",
                                    image_paths=tmp_paths
                                )
                        add_message("bot", result)
                        st.session_state["claim_step"] = "submitted"
                        st.rerun()

        with tab_claim:
            st.markdown("### 📋 File a Claim")
            info = st.session_state["customer_info"]
            domain_map = {
                "P-C": ("Auto Insurance",   "auto"),
                "P-B": ("Cancer Insurance", "cancer"),
                "P-D": ("Dental Insurance", "teeth")
            }
            options = {}
            for p in info["policies"]:
                if p["product_id"] in domain_map:
                    label, domain = domain_map[p["product_id"]]
                    options[label] = domain
            if not options:
                st.warning("No claimable insurance found.")
            else:
                selected_label  = st.selectbox("Select Insurance", list(options.keys()), key="claim_select")
                selected_domain = options[selected_label]
                st.markdown("---")
                st.markdown("#### 📎 Upload Documents")
                st.info(f"Please upload the required documents for **{selected_label}**.")
                uploaded = st.file_uploader(
                    "Document images",
                    type=["jpg", "jpeg", "png", "pdf"],
                    accept_multiple_files=True,
                    key="claim_tab_uploader"
                )
                if uploaded:
                    cols = st.columns(min(len(uploaded), 4))
                    for i, f in enumerate(uploaded):
                        with cols[i % 4]:
                            if f.type.startswith("image"):
                                st.image(f, caption=f.name, use_container_width=True)
                            else:
                                st.markdown(f"📄 {f.name}")
                if st.button("📤 Submit Claim", disabled=not uploaded, key="btn_claim"):
                    with tempfile.TemporaryDirectory() as tmpdir:
                        tmp_paths = []
                        for f in uploaded:
                            tmp_path = os.path.join(tmpdir, f.name)
                            with open(tmp_path, "wb") as fp:
                                fp.write(f.read())
                            tmp_paths.append(tmp_path)
                        with st.spinner("🔍 Analyzing documents and reviewing..."):
                            from agents.claim_agent import handle_claim
                            result = handle_claim(
                                customer_info=info,
                                domain=selected_domain,
                                query="insurance claim",
                                image_paths=tmp_paths
                            )
                    if "✅" in result:
                        st.success(result)
                    elif "⚠️" in result:
                        st.warning(result)
                    else:
                        st.info(result)
                    add_message("bot", f"[Claims Tab] {result}")


else:
    if not st.session_state["admin_logged_in"]:
        st.markdown("""
        <div style="text-align:center; padding:80px 0;">
            <div style="font-size:4rem;">🔐</div>
            <h1 style="color:#1a1a2e; font-weight:700;">Admin Dashboard</h1>
            <p style="color:#666;">← Please login on the left</p>
            <p style="color:#999; font-size:0.9rem;">ID: admin / PW: 1234</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        def filter_by_date(df, col="timestamp"):
            if df.empty or col not in df.columns:
                return df
            df[col] = pd.to_datetime(df[col])
            return df[(df[col].dt.date >= date_from) & (df[col].dt.date <= date_to)]

        audit_df     = filter_by_date(load_csv(AUDIT_LOG))
        complaint_df = filter_by_date(load_csv(COMPLAINT_DB))
        handoff_df   = filter_by_date(load_csv(HANDOFF_DB))
        customer_df  = load_csv(CUSTOMER_DB)

        tab_ov, tab_log, tab_comp, tab_hand, tab_cust = st.tabs([
            "📊 Overview", "📋 Conversation Log", "🚨 Complaint Management",
            "👤 Handoff Status", "👥 Customer Overview"
        ])

        with tab_ov:
            st.markdown("### 📊 Overview")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1: st.metric("Total Chats", f"{len(audit_df)}")
            with col2: st.metric("Complaints", f"{len(complaint_df)}")
            with col3: st.metric("Handoffs", f"{len(handoff_df)}")
            with col4:
                claim_count = len(audit_df[audit_df["claim_status"] != "-"]) if not audit_df.empty and "claim_status" in audit_df.columns else 0
                st.metric("Claims Filed", f"{claim_count}")
            with col5:
                rate = round(len(complaint_df) / len(audit_df) * 100, 1) if len(audit_df) > 0 else 0
                st.metric("Complaint Rate", f"{rate}%")

            st.markdown("---")
            if not audit_df.empty and "intent" in audit_df.columns:
                col_l, col_r = st.columns(2)
                with col_l:
                    st.markdown("#### 📌 Intent Distribution")
                    st.plotly_chart(make_bar_chart(audit_df["intent"].value_counts()), use_container_width=True)
                with col_r:
                    st.markdown("#### 📌 Domain Distribution")
                    if "domains" in audit_df.columns:
                        domain_counts = {}
                        for d in audit_df["domains"].dropna():
                            for item in str(d).split(","):
                                item = item.strip()
                                if item and item != "-":
                                    domain_counts[item] = domain_counts.get(item, 0) + 1
                        if domain_counts:
                            st.plotly_chart(make_bar_chart(pd.Series(domain_counts)), use_container_width=True)

            st.markdown("---")
            st.markdown("#### 🕐 Recent 10 Conversations")
            if not audit_df.empty:
                for _, row in audit_df.sort_values("timestamp", ascending=False).head(10).iterrows():
                    is_c = str(row.get("is_complaint","")).lower() == "true"
                    is_h = str(row.get("is_handoff","")).lower() == "true"
                    if is_h:
                        rc, badge = "handoff",   '<span class="badge badge-handoff">Handoff</span>'
                    elif is_c:
                        rc, badge = "complaint", '<span class="badge badge-complaint">Complaint</span>'
                    elif str(row.get("claim_status","-")) != "-":
                        rc, badge = "claim",     '<span class="badge badge-claim">Claim</span>'
                    else:
                        rc, badge = "normal",    '<span class="badge badge-normal">Normal</span>'
                    intent_badge = f'<span class="badge badge-intent">{row.get("intent","-")}</span>'
                    st.markdown(f"""
<div class="log-row {rc}">
    <b>{row.get('customer_name','-')}</b> ({row.get('customer_id','-')}) · {row.get('timestamp','-')} · {badge} · {intent_badge}
    <br><span style="color:#333;">"{row.get('query','-')}"</span>
    <br><span style="color:#999;font-size:0.82rem;">{row.get('answer_preview','-')}</span>
</div>""", unsafe_allow_html=True)
            else:
                st.info("No conversation data recorded.")

        with tab_log:
            st.markdown("### 📋 Conversation Log")
            if audit_df.empty:
                st.info("No conversation log recorded.")
            else:
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    intent_filter = st.selectbox("Intent Filter", ["All"] + list(audit_df["intent"].dropna().unique()))
                with col_f2:
                    complaint_filter = st.selectbox("Complaint Filter", ["All", "Complaints Only", "Normal Only"])
                with col_f3:
                    customer_filter = st.text_input("Search Customer ID")
                filtered = audit_df.copy()
                if intent_filter != "All":
                    filtered = filtered[filtered["intent"] == intent_filter]
                if complaint_filter == "Complaints Only":
                    filtered = filtered[filtered["is_complaint"] == True]
                elif complaint_filter == "Normal Only":
                    filtered = filtered[filtered["is_complaint"] != True]
                if customer_filter:
                    filtered = filtered[filtered["customer_id"].str.contains(customer_filter, na=False)]
                st.markdown(f"**Total: {len(filtered)}**")
                display_cols = [c for c in ["timestamp","customer_name","customer_id","intent","domains","query","answer_preview","is_complaint","is_handoff"] if c in filtered.columns]
                st.dataframe(filtered[display_cols].sort_values("timestamp", ascending=False), use_container_width=True, height=500)
                st.download_button(
                    "📥 Download CSV",
                    data=filtered.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
                    file_name=f"audit_log_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

        with tab_comp:
            st.markdown("### 🚨 Complaint Management")
            if complaint_df.empty:
                st.info("No complaints received.")
            else:
                col1, col2, col3 = st.columns(3)
                with col1: st.metric("Total Complaints", len(complaint_df))
                with col2: st.metric("Pending", len(complaint_df[complaint_df["status"]=="Received"]) if "status" in complaint_df.columns else 0)
                with col3:
                    avg = round(complaint_df["sentiment_score"].mean(),1) if "sentiment_score" in complaint_df.columns else "-"
                    st.metric("Avg Sentiment Score", f"{avg} / 10")
                st.markdown("---")
                for _, row in complaint_df.sort_values("timestamp", ascending=False).iterrows():
                    score = row.get("sentiment_score", 5)
                    badge = (
                        '<span class="badge badge-handoff">Very Dissatisfied</span>' if score <= 3 else
                        '<span class="badge badge-complaint">Dissatisfied</span>'     if score <= 5 else
                        '<span class="badge badge-normal">Neutral</span>'
                    )
                    st.markdown(f"""
<div class="log-row complaint">
    <b>{row.get('complaint_id','-')}</b> · {row.get('timestamp','-')} · {badge}
    <br><b>{row.get('customer_name','-')}</b> ({row.get('customer_id','-')}) | Type: {row.get('complaint_type','-')} | Status: {row.get('status','-')}
    <br><span style="color:#333;">"{row.get('customer_query','-')}"</span>
</div>""", unsafe_allow_html=True)

        with tab_hand:
            st.markdown("### 👤 Handoff Status")
            if handoff_df.empty:
                st.info("No handoff cases.")
            else:
                col1, col2 = st.columns(2)
                with col1: st.metric("Total Handoffs", len(handoff_df))
                with col2: st.metric("Pending", len(handoff_df[handoff_df["status"]=="Pending"]) if "status" in handoff_df.columns else 0)
                st.markdown("---")
                for _, row in handoff_df.sort_values("timestamp", ascending=False).iterrows():
                    st.markdown(f"""
<div class="log-row handoff">
    <b>{row.get('handoff_id','-')}</b> · {row.get('timestamp','-')}
    <br><b>{row.get('customer_name','-')}</b> ({row.get('customer_id','-')}) | Status: {row.get('status','-')}
    <br>⚠️ Reason: {row.get('reason','-')}
    <br><span style="color:#333;">"{row.get('query','-')}"</span>
</div>""", unsafe_allow_html=True)

        with tab_cust:
            st.markdown("### 👥 Customer Overview")
            if customer_df.empty:
                st.info("No customer data.")
            else:
                col1, col2, col3 = st.columns(3)
                with col1: st.metric("Total Customers", customer_df["customer_id"].nunique() if "customer_id" in customer_df.columns else 0)
                with col2: st.metric("Total Contracts", len(customer_df))
                with col3:
                    if "product_name" in customer_df.columns:
                        st.metric("Most Popular Product", customer_df["product_name"].value_counts().index[0])
                st.markdown("---")
                if "product_name" in customer_df.columns:
                    st.markdown("#### 📌 Enrollment by Product")
                    st.plotly_chart(make_bar_chart(customer_df["product_name"].value_counts()), use_container_width=True)
                st.markdown("---")
                display_df = customer_df.drop(columns=[c for c in ["password"] if c in customer_df.columns])
                st.dataframe(display_df, use_container_width=True, height=400)
