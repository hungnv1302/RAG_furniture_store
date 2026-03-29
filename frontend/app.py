import streamlit as st
import requests
import uuid

# ── Config ──────────────────────────────────────────────────────────────
API_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{API_URL}/api/chat"
HEALTH_ENDPOINT = f"{API_URL}/health"

# ── Page config ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NMK Chatbot",
    page_icon="🏗️",
    layout="centered",
)

# ── Custom CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Chat container */
    .stChatMessage {
        border-radius: 12px;
    }

    /* Source card */
    .source-card {
        background-color: #f0f2f6;
        border-left: 4px solid #4A90D9;
        padding: 10px 14px;
        margin: 6px 0;
        border-radius: 6px;
        font-size: 0.85em;
        line-height: 1.5;
    }
    .source-card strong {
        color: #4A90D9;
    }

    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75em;
        font-weight: 600;
    }
    .status-healthy  { background: #d4edda; color: #155724; }
    .status-degraded  { background: #fff3cd; color: #856404; }
    .status-unhealthy { background: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ──────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Sidebar ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🏗️ NMK Chatbot")
    st.caption("Chatbot tư vấn kiến trúc NMK")

    st.divider()

    # New conversation button
    if st.button("🔄 Cuộc trò chuyện mới", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    st.divider()

    # Health check
    with st.expander("⚙️ Trạng thái hệ thống"):
        if st.button("Kiểm tra", use_container_width=True):
            try:
                resp = requests.get(HEALTH_ENDPOINT, timeout=5)
                data = resp.json()
                status = data.get("status", "unknown")
                css_class = {
                    "healthy": "status-healthy",
                    "degraded": "status-degraded",
                }.get(status, "status-unhealthy")

                st.markdown(
                    f'Trạng thái: <span class="status-badge {css_class}">{status}</span>',
                    unsafe_allow_html=True,
                )

                for svc, info in data.get("services", {}).items():
                    svc_status = info.get("status", None)
                    # rag_components uses "initialized" boolean instead of "status"
                    if svc_status is None:
                        is_init = info.get("initialized", False)
                        svc_status = "ready" if is_init else "not initialized"
                    icon = "🟢" if svc_status in ("up", "ready", "configured") else "🔴"
                    st.markdown(f"{icon} **{svc}**: {svc_status}")
            except requests.exceptions.ConnectionError:
                st.error("Không thể kết nối đến API server.")
            except Exception as e:
                st.error(f"Lỗi: {e}")

    st.divider()
    st.caption(f"Session: `{st.session_state.session_id[:8]}...`")

# ── Chat area ───────────────────────────────────────────────────────────
st.header("💬 Chat")

# Render existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])


# Chat input
if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    # Call API and display response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Đang xử lý..."):
            try:
                resp = requests.post(
                    CHAT_ENDPOINT,
                    json={
                        "query": prompt,
                        "session_id": st.session_state.session_id,
                    },
                    timeout=120,
                )

                if resp.status_code == 200:
                    data = resp.json()
                    answer = data.get("answer", "Không có phản hồi.")
                    sources = data.get("sources", [])
                    st.session_state.session_id = data.get(
                        "session_id", st.session_state.session_id
                    )

                    st.markdown(answer)



                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                        }
                    )

                elif resp.status_code == 429:
                    err = "⚠️ Bạn gửi quá nhiều yêu cầu. Vui lòng chờ một chút."
                    st.warning(err)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": err}
                    )
                else:
                    detail = resp.json().get("detail", resp.text)
                    err = f"❌ Lỗi ({resp.status_code}): {detail}"
                    st.error(err)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": err}
                    )

            except requests.exceptions.ConnectionError:
                err = "❌ Không thể kết nối đến API server. Hãy đảm bảo server đang chạy tại `http://localhost:8000`."
                st.error(err)
                st.session_state.messages.append(
                    {"role": "assistant", "content": err}
                )
            except requests.exceptions.Timeout:
                err = "⏳ Yêu cầu bị timeout. Vui lòng thử lại."
                st.error(err)
                st.session_state.messages.append(
                    {"role": "assistant", "content": err}
                )
            except Exception as e:
                err = f"❌ Lỗi không xác định: {e}"
                st.error(err)
                st.session_state.messages.append(
                    {"role": "assistant", "content": err}
                )
