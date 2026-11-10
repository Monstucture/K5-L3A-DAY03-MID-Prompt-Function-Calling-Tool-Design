from datetime import datetime
from pathlib import Path

import streamlit as st

from chat import (
    now_iso,
    run_model_tool_loop,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


# ==================== CẤU HÌNH ====================

ROOT = Path(__file__).resolve().parent
PROMPT_PATH = ROOT / "artifacts" / "system_prompt.md"
TOOLS_PATH = ROOT / "artifacts" / "tools.yaml"

VERSION = "v5"
PROVIDER = "openrouter"

st.set_page_config(
    page_title="ORBIT — Trợ lý nghiên cứu",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================== GIAO DIỆN ====================

st.markdown(
    """
    <style>
    @import url(
      'https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap'
    );

    :root {
        color-scheme: dark;
        --cyan: #67e8f9;
        --purple: #a78bfa;
        --text: #e6edf7;
        --muted: #9aabc3;
    }

    html, body, [class*="st-"] {
        font-family: "Be Vietnam Pro", sans-serif;
    }

    .stApp {
        color: var(--text);
        background-color: #070b16;
        background-image:
            radial-gradient(
                ellipse at 12% 5%,
                rgba(25, 123, 155, 0.20),
                transparent 45%
            ),
            radial-gradient(
                ellipse at 95% 30%,
                rgba(105, 66, 175, 0.17),
                transparent 45%
            ),
            radial-gradient(
                circle at 20% 35%,
                #9ac9e7 1px,
                transparent 1.5px
            ),
            radial-gradient(
                circle at 80% 65%,
                #7480a5 1px,
                transparent 1.5px
            ),
            linear-gradient(
                rgba(115, 180, 220, 0.035) 1px,
                transparent 1px
            ),
            linear-gradient(
                90deg,
                rgba(115, 180, 220, 0.035) 1px,
                transparent 1px
            );
        background-size:
            auto, auto, 237px 227px, 319px 293px,
            48px 48px, 48px 48px;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background: rgba(8, 15, 28, 0.97);
        border-right: 1px solid rgba(103, 232, 249, 0.15);
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #b5c4d9;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 12px 0 24px;
    }

    .brand-icon {
        display: grid;
        place-items: center;
        width: 44px;
        height: 44px;
        color: #67e8f9;
        font-size: 28px;
        border: 1px solid rgba(103, 232, 249, 0.4);
        background: rgba(103, 232, 249, 0.06);
        border-radius: 12px;
        box-shadow: inset 0 0 18px rgba(103, 232, 249, 0.08);
    }

    .brand-name {
        color: #edf7ff;
        font-size: 22px;
        font-weight: 800;
        letter-spacing: 5px;
    }

    .brand-sub {
        margin-top: 4px;
        color: #8296b3;
        font-size: 11px;
    }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 34px;
        margin-bottom: 26px;
        border: 1px solid rgba(103, 232, 249, 0.22);
        border-radius: 8px 28px 8px 28px;
        background: linear-gradient(
            115deg,
            rgba(16, 35, 55, 0.92),
            rgba(18, 18, 42, 0.88)
        );
        box-shadow: 0 16px 60px rgba(0, 0, 0, 0.2);
    }

    .hero::before {
        content: "";
        position: absolute;
        top: 0;
        left: 34px;
        width: 100px;
        height: 3px;
        background: #67e8f9;
        box-shadow: 0 0 22px rgba(103, 232, 249, 0.65);
    }

    .hero::after {
        content: "◎";
        position: absolute;
        right: 25px;
        top: -65px;
        font-size: 260px;
        color: rgba(103, 232, 249, 0.055);
        pointer-events: none;
    }

    .eyebrow {
        color: #67e8f9;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 3px;
        margin-bottom: 15px;
    }

    .hero h1 {
        color: #f0f6ff;
        font-size: clamp(28px, 4vw, 42px);
        font-weight: 800;
        letter-spacing: -1.5px;
        line-height: 1.25;
        margin: 0 0 14px;
        padding: 0;
    }

    .hero h1 span {
        color: #67e8f9;
    }

    .hero p {
        color: #a7b8ce;
        max-width: 620px;
        line-height: 1.8;
        font-size: 14px;
        margin: 0;
    }

    .capabilities {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 24px;
    }

    .capabilities span {
        padding: 7px 12px;
        border: 1px solid rgba(151, 178, 218, 0.18);
        border-radius: 6px;
        background: rgba(255, 255, 255, 0.025);
        color: #b9cce2;
        font-size: 11px;
    }

    .section-label {
        color: #8ba3bf;
        font-size: 11px;
        letter-spacing: 2px;
        margin: 24px 0 16px;
    }

    [data-testid="stChatMessage"] {
        padding: 20px;
        margin-bottom: 14px;
        border: 1px solid rgba(133, 169, 212, 0.16);
        border-radius: 14px;
        background: rgba(12, 23, 40, 0.88);
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li {
        color: #dce7f5;
        line-height: 1.85;
    }

    [data-testid="stChatMessage"] a {
        color: #67e8f9;
    }

    [data-testid="stBottom"] > div {
        background: transparent;
    }

    [data-testid="stChatInput"] {
        background: #101b2d;
        border: 1px solid rgba(103, 232, 249, 0.4);
        border-radius: 14px;
        box-shadow: 0 0 25px rgba(103, 232, 249, 0.06);
    }

    [data-testid="stChatInput"] textarea {
        color: #eff6ff;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #93a8c2;
    }

    .stButton > button,
    .stDownloadButton > button {
        color: #d5f8ff;
        background: rgba(103, 232, 249, 0.07);
        border: 1px solid rgba(103, 232, 249, 0.3);
        border-radius: 8px;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        color: #ffffff;
        border-color: #67e8f9;
        background: rgba(103, 232, 249, 0.14);
    }

    [data-testid="stExpander"] {
        background: rgba(10, 19, 34, 0.8);
        border: 1px solid rgba(133, 169, 212, 0.16);
        border-radius: 10px;
    }

    [data-testid="stCaptionContainer"] {
        color: #94a8c2;
    }

    @media (max-width: 640px) {
        .hero {
            padding: 26px 20px;
        }

        .hero::after {
            right: -55px;
        }

        [data-testid="stChatMessage"] {
            padding: 14px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================== THANH BÊN ====================

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">◎</div>
            <div>
                <div class="brand-name">ORBIT</div>
                <div class="brand-sub">KHÔNG GIAN NGHIÊN CỨU</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    new_chat = st.button(
        "＋ Cuộc trò chuyện mới",
        use_container_width=True,
    )

    st.divider()
    st.markdown("**Bạn có thể yêu cầu**")
    st.markdown(
        """
        - Tìm thông tin trên web.
        - Đọc nội dung một đường dẫn.
        - Lọc danh sách tin theo từ khóa.
        - Tổng hợp thông tin đã tìm được.
        """
    )

    st.divider()
    st.caption(
        "Hội thoại được lưu trên máy sau mỗi lượt. "
        "Mỗi yêu cầu sử dụng API OpenRouter."
    )

if new_chat:
    for key in (
        "history",
        "system_prompt",
        "tools",
        "transcript",
        "transcript_path",
    ):
        st.session_state.pop(key, None)
    st.rerun()


# ==================== KHỞI TẠO CHATBOT ====================

if "transcript" not in st.session_state:
    try:
        provider = make_provider(PROVIDER)

        system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        tools = to_openai_tools(
            load_tool_declarations(TOOLS_PATH)
        )

        artifact = build_artifact_version(
            VERSION,
            PROMPT_PATH,
            TOOLS_PATH,
        )

        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        transcript_id = f"{VERSION}_ui_{timestamp}"

        st.session_state.history = []
        st.session_state.system_prompt = system_prompt
        st.session_state.tools = tools
        st.session_state.transcript_path = (
            ROOT
            / "transcripts"
            / f"{transcript_id}.transcript.json"
        )
        st.session_state.transcript = {
            "transcript_id": transcript_id,
            **artifact_version_dict(artifact),
            "provider": PROVIDER,
            "model": getattr(provider, "default_model", None),
            "system_prompt": str(PROMPT_PATH),
            "tools": str(TOOLS_PATH),
            "history_window": 5,
            "max_tool_rounds": 4,
            "created_at": now_iso(),
            "turns": [],
        }

    except Exception:
        st.error(
            "Chưa khởi tạo được trợ lý. "
            "Kiểm tra file prompt, khai báo công cụ và môi trường."
        )
        st.stop()


# ==================== KHU VỰC TRÒ CHUYỆN ====================

st.markdown(
    """
    <section class="hero">
        <div class="eyebrow">ORBIT / TRỢ LÝ NGHIÊN CỨU</div>
        <h1>Khám phá thông tin.<br><span>Kết nối tri thức.</span></h1>
        <p>
            Đặt câu hỏi, gửi đường dẫn hoặc cung cấp danh sách tin.
            Trợ lý sẽ chọn công cụ phù hợp để hỗ trợ bạn.
        </p>
        <div class="capabilities">
            <span>⌕ Tìm kiếm web</span>
            <span>↗ Đọc đường dẫn</span>
            <span>≡ Lọc theo từ khóa</span>
        </div>
    </section>
    <div class="section-label">HỘI THOẠI / KHÔNG GIAN LÀM VIỆC</div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.history:
    st.info(
        "Bắt đầu bằng một câu hỏi hoặc yêu cầu lọc danh sách tin."
    )

for message in st.session_state.history:
    avatar = "🧑‍🚀" if message["role"] == "user" else "🛰️"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

user_text = st.chat_input("Nhập câu hỏi hoặc gửi đường dẫn...")


# ==================== XỬ LÝ YÊU CẦU ====================

if user_text:
    with st.chat_message("user", avatar="🧑‍🚀"):
        st.markdown(user_text)

    turn = {
        "turn_index": len(st.session_state.transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.chat_message("assistant", avatar="🛰️"):
        try:
            messages = [
                {
                    "role": "system",
                    "content": st.session_state.system_prompt,
                },
                *trim_history(st.session_state.history, 5),
                {"role": "user", "content": user_text},
            ]

            with st.spinner("Đang phân tích và xử lý yêu cầu..."):
                result = run_model_tool_loop(
                    provider=make_provider(PROVIDER),
                    messages=messages,
                    tools=st.session_state.tools,
                    model=st.session_state.transcript["model"],
                    max_tool_rounds=4,
                )

            turn.update(result)

            if result["status"] == "max_tool_rounds":
                answer = (
                    "Đã đạt giới hạn xử lý của lượt này. "
                    "Bạn có thể chia yêu cầu thành phần nhỏ hơn."
                )
            else:
                answer = (
                    result["assistant_text"]
                    or "Lượt xử lý đã kết thúc nhưng chưa có câu trả lời."
                )

            turn["assistant_text"] = answer
            st.markdown(answer)

            st.session_state.history.extend([
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": answer},
            ])

        except Exception as error:
            turn.update({
                "status": "provider_error",
                "error": f"{type(error).__name__}: {error}",
            })
            st.error(
                "Chưa xử lý được yêu cầu. "
                "Hãy kiểm tra kết nối và cấu hình OpenRouter."
            )

    turn["ended_at"] = now_iso()
    st.session_state.transcript["turns"].append(turn)

    try:
        write_transcript(
            st.session_state.transcript_path,
            st.session_state.transcript,
        )
    except Exception:
        st.warning(
            "Chưa lưu được hội thoại vào máy. "
            "Hãy kiểm tra quyền ghi thư mục transcripts."
        )


# ==================== BẰNG CHỨNG HỘI THOẠI ====================

if st.session_state.transcript["turns"]:
    latest = st.session_state.transcript["turns"][-1]

    with st.expander("Chi tiết xử lý lượt gần nhất"):
        st.write("Trạng thái:", latest.get("status"))
        st.json(latest.get("tool_events", []))

    with st.sidebar:
        st.divider()
        st.markdown("**Bản ghi hội thoại**")

        # Tạo bản tải xuống ngay từ nội dung đang có trong bộ nhớ.
        import json

        st.download_button(
            label="↓ Tải hội thoại JSON",
            data=json.dumps(
                st.session_state.transcript,
                ensure_ascii=False,
                indent=2,
                default=str,
            ),
            file_name=st.session_state.transcript_path.name,
            mime="application/json",
            use_container_width=True,
        )