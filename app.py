"""Streamlit web app for the multi-agent language learning system."""

import base64
import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv
from src.agents.base_agent import DEFAULT_MODEL
from src.agents.coordinator_agent import CoordinatorAgent
from src.agents.vocabulary_agent import VocabularyAgent
from src.agents.grammar_agent import GrammarAgent
from src.agents.conversation_agent import ConversationAgent
from src.agents.web_search_agent import WebSearchAgent
from src.schemas.messages import AgentState, AgentType

load_dotenv(override=True)
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
USE_GROQ = True
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"

LANGUAGES = ["German", "English", "Spanish", "French", "Italian", "Portuguese", "Dutch", "Persian"]
LANGUAGE_FA = {
    "German": "آلمانی", "English": "انگلیسی", "Spanish": "اسپانیایی", "French": "فرانسوی",
    "Italian": "ایتالیایی", "Portuguese": "پرتغالی", "Dutch": "هلندی", "Persian": "فارسی",
}
LEVELS = ["beginner", "intermediate", "advanced"]
LEVEL_FA = {"beginner": "مبتدی", "intermediate": "متوسط", "advanced": "پیشرفته"}
EXPLAIN_LANGUAGES = ["Persian", "English", "German"]
MODES = {
    "خودکار (هماهنگ‌کننده تصمیم می‌گیرد)": AgentType.COORDINATOR,
    "جستجو در اینترنت": AgentType.WEB_SEARCH,
    "واژگان": AgentType.VOCABULARY,
    "گرامر": AgentType.GRAMMAR,
    "مکالمه": AgentType.CONVERSATION,
}
TUTOR_FA = {"vocabulary": "واژگان", "grammar": "گرامر", "conversation": "مکالمه", "web_search": "جستجو در اینترنت"}
AGENT_ICONS = {"vocabulary": "📚", "grammar": "✏️", "conversation": "💬", "web_search": "🌐"}
STARTERS = {
    "German": [
        "۱۰ کلمهٔ آلمانی روزمرهٔ مربوط به غذا یاد بده",
        "کی از der، die و das استفاده می‌کنیم؟",
        "بیا به زبان آلمانی ساده دربارهٔ آخر هفته‌ام گفتگو کنیم",
        "حالت Akkusativ در آلمانی را با مثال توضیح بده",
    ],
}
DEFAULT_STARTERS = [
    "۱۰ کلمهٔ پایهٔ روزمره یاد بده",
    "مهم‌ترین زمان‌های فعل را توضیح بده",
    "بیا یک گفتگوی ساده داشته باشیم",
]


def agent_models() -> dict[AgentType, str]:
    """Model per agent: GROQ_MODEL for all agents with Groq, else per-agent .env values falling back to OLLAMA_MODEL."""
    agents = [AgentType.COORDINATOR, AgentType.VOCABULARY, AgentType.GRAMMAR, AgentType.CONVERSATION]
    if USE_GROQ:
        groq_model = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)
        return {t: groq_model for t in agents}
    default = os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)
    return {t: os.getenv(f"{t.value.upper()}_MODEL") or default for t in agents}


@st.cache_resource(show_spinner="در حال راه‌اندازی عامل‌ها...")
def get_coordinator(models: tuple[tuple[AgentType, str], ...], api_key: str) -> CoordinatorAgent:
    m = dict(models)
    key = api_key or None
    coordinator = CoordinatorAgent(model=m[AgentType.COORDINATOR], api_key=key)
    coordinator.register_agent(VocabularyAgent(model=m[AgentType.VOCABULARY], api_key=key))
    coordinator.register_agent(GrammarAgent(model=m[AgentType.GRAMMAR], api_key=key))
    coordinator.register_agent(ConversationAgent(model=m[AgentType.CONVERSATION], api_key=key))
    coordinator.register_agent(WebSearchAgent(api_key=key))
    return coordinator


@st.cache_data(ttl=10, show_spinner=False)
def installed_models() -> set[str] | None:
    try:
        tags = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2).json()["models"]
    except Exception:
        return None
    return {m["name"] for m in tags}


def with_tag(name: str) -> str:
    return name if ":" in name else f"{name}:latest"


VISION_MODEL = "qwen/qwen3.8-27b"
# Groq's free tier allows this model 8K tokens/minute. An image costs 2,048 tokens and
# max_completion_tokens is reserved up front, so history and output are kept small.
VISION_HISTORY_TURNS = 4
VISION_HISTORY_CHARS = 600
VISION_MAX_OUTPUT = 1500


def post_groq(api_key: str, payload: dict, retries: int = 1) -> dict:
    """POST to Groq; on 429 wait for retry-after (if short) and try again, else raise a readable error."""
    for attempt in range(retries + 1):
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=120,
        )
        if response.status_code != 429:
            response.raise_for_status()
            return response.json()
        wait = float(response.headers.get("retry-after", 0) or 0)
        if attempt < retries and wait <= 15:
            time.sleep(wait or 3)
    raise RuntimeError(
        f"محدودیت درخواست گروک پر شده است. حدود {int(wait) or 'چند'} ثانیه صبر کنید و دوباره امتحان کنید."
    )


def answer_image_question(prompt: str, history: list[dict], api_key: str, image) -> str:
    """Answer a question about an uploaded image with Groq's vision model."""
    image_data = base64.b64encode(image.getvalue()).decode("ascii")
    mime_type = image.type or "image/jpeg"
    messages = [
        {
            "role": "system",
            "content": "Answer the user's question about the supplied image in the user's language.",
        },
        *[
            {"role": m["role"], "content": m["content"][:VISION_HISTORY_CHARS]}
            for m in history[-VISION_HISTORY_TURNS:]
        ],
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt or "Describe this image."},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{image_data}"},
                },
            ],
        },
    ]
    data = post_groq(api_key, {
        "model": VISION_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "max_completion_tokens": VISION_MAX_OUTPUT,
    })
    return data["choices"][0]["message"]["content"]


st.set_page_config(
    page_title="معلم زبان",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)
st.markdown(
    """
    <style>
    /* RTL only for the content, never for Streamlit's layout containers:
       flipping .stApp / stSidebar breaks sidebar positioning on mobile. */
    [data-testid="stMainBlockContainer"], [data-testid="stSidebarUserContent"],
    [data-testid="stChatInput"] { direction: rtl; text-align: right; }
    [data-testid="stMarkdownContainer"], [data-testid="stChatMessageContent"] {
        word-break: normal;
        overflow-wrap: anywhere;
    }
    /* Wide markdown tables scroll inside the message instead of overflowing the page. */
    [data-testid="stMarkdownContainer"] table {
        display: block;
        max-width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        border-collapse: collapse;
        direction: rtl;
    }
    [data-testid="stMarkdownContainer"] th,
    [data-testid="stMarkdownContainer"] td {
        padding: 0.4rem 0.6rem;
        min-width: 5rem;
        overflow-wrap: normal;
        word-break: normal;
        text-align: right;
        vertical-align: top;
    }
    [data-testid="stMarkdownContainer"] th { white-space: nowrap; }
    [data-testid="stChatMessageContent"] { min-width: 0; max-width: 100%; }
    @media (max-width: 640px) {
        [data-testid="stMarkdownContainer"] table { font-size: 0.85rem; }
        [data-testid="stMainBlockContainer"] {
            padding: 1rem 0.8rem 5rem;
        }
        [data-testid="stSidebarUserContent"] p,
        [data-testid="stSidebarUserContent"] label,
        [data-testid="stMainBlockContainer"] p,
        [data-testid="stMainBlockContainer"] label,
        [data-testid="stMainBlockContainer"] button {
            white-space: normal;
            overflow-wrap: anywhere;
        }
        [data-testid="stChatMessage"] {
            padding: 0.75rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

models = agent_models()
groq_api_key = ""  # set from the sidebar field when using Groq
# Ollama's installed-model list only matters when running locally.
available = None if USE_GROQ else installed_models()

with st.sidebar:
    st.header("⚙️ تنظیمات")
    language = st.selectbox("زبانی که یاد می‌گیرید", LANGUAGES, index=0, format_func=LANGUAGE_FA.get)
    level = st.radio("سطح", LEVELS, horizontal=True, format_func=LEVEL_FA.get)
    explain_in = st.selectbox("توضیحات به زبان", EXPLAIN_LANGUAGES, index=0, format_func=LANGUAGE_FA.get)
    mode_label = st.selectbox("معلم", list(MODES))

    st.divider()
    st.subheader("مدل‌ها")
    if USE_GROQ:
        # The key is typed here every time; it is never read from .env.
        groq_api_key = st.text_input("کلید API گروک (Groq)", type="password", placeholder="gsk_...").strip()
        if not models[AgentType.COORDINATOR]:
            st.error("مقدار `GROQ_MODEL` را در `.env` تنظیم کنید.")
        for agent_type, model in models.items():
            st.markdown(f"⚡ **{agent_type.value.capitalize()}**: `{model}`")
        st.caption("ارائه‌دهنده: Groq. مدل را با `GROQ_MODEL` در فایل `.env` تنظیم کنید و صفحه را دوباره باز کنید.")
    else:
        if available is None:
            st.error(f"Ollama در آدرس {OLLAMA_URL} در دسترس نیست.")
        for agent_type, model in models.items():
            ok = available is not None and with_tag(model) in available
            st.markdown(f"{'✅' if ok else '❌'} **{agent_type.value.capitalize()}**: `{model}`")
        st.caption("مدل هر عامل را در فایل `.env` تنظیم کنید (مثلاً `GRAMMAR_MODEL=llama3.2`) و صفحه را دوباره باز کنید.")

    st.divider()
    if st.button("🗑️ پاک کردن گفتگو", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.title("🎓 معلم زبان")
st.caption(f"یادگیری **{LANGUAGE_FA[language]}** · سطح {LEVEL_FA[level]} · {mode_label}")

missing = sorted({m for m in models.values() if available is not None and with_tag(m) not in available})
# Groq is hosted, so there is no local Ollama to start or models to pull.
if not USE_GROQ:
    if available is None:
        st.warning("ابتدا Ollama را راه‌اندازی کنید (`sudo snap start ollama` یا `ollama serve`).")
    elif missing:
        st.warning("مدل‌های زیر نصب نیستند. این دستورها را اجرا کنید:\n\n" + "\n\n".join(f"`ollama pull {m}`" for m in missing))

if USE_GROQ and not groq_api_key:
    st.info("🔑 کلید API گروک را در نوار کناری وارد کنید تا گفتگو شروع شود.")
    st.stop()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("agent"):
            st.caption(f"{AGENT_ICONS.get(msg['agent'], '🤖')} معلم {TUTOR_FA[msg['agent']]}")
        if msg.get("image"):
            st.image(msg["image"], use_container_width=True)
        st.markdown(msg["content"])

MAX_IMAGE_BYTES = 20 * 1024 * 1024

# Image attachment lives inside the chat box (📎), like ChatGPT.
submission = st.chat_input(
    f"هر سوالی دربارهٔ {LANGUAGE_FA[language]} بپرسید...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp"],
)
prompt, uploaded_image = None, None
if submission:
    prompt = submission.text or ""
    uploaded_image = submission.files[0] if submission.files else None
    if uploaded_image and uploaded_image.size > MAX_IMAGE_BYTES:
        st.error("اندازه تصویر باید کمتر از 20 مگابایت باشد.")
        prompt, uploaded_image = None, None
    elif uploaded_image and not prompt:
        prompt = "این تصویر را توضیح بده."

if not st.session_state.messages and not prompt:
    st.markdown("**این‌ها را امتحان کنید:**")
    for i, text in enumerate(STARTERS.get(language, DEFAULT_STARTERS)):
        if st.button(text, use_container_width=True, key=f"starter_{i}"):
            prompt = text

if prompt:
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    image_bytes = uploaded_image.getvalue() if uploaded_image else None
    st.session_state.messages.append({"role": "user", "content": prompt, "image": image_bytes})
    with st.chat_message("user"):
        if image_bytes:
            st.image(image_bytes, use_container_width=True)
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            if uploaded_image:
                agent_type = None
                st.caption("🖼️ پاسخ دربارهٔ تصویر")
                with st.spinner("در حال بررسی تصویر..."):
                    answer = answer_image_question(prompt, history, groq_api_key, uploaded_image)
                st.markdown(answer)
            else:
                coordinator = get_coordinator(tuple(models.items()), groq_api_key)
                state = AgentState(
                    user_input=prompt,
                    learning_language=language,
                    difficulty_level=level,
                    explanation_language=explain_in,
                    history=history,
                    current_agent=MODES[mode_label],
                )
                with st.spinner("در حال انتخاب معلم..."):
                    agent_type = coordinator.route(state)
                st.caption(f"{AGENT_ICONS.get(agent_type.value, '🤖')} معلم {TUTOR_FA[agent_type.value]}")
                if agent_type == AgentType.WEB_SEARCH:
                    with st.spinner("در حال جستجو در اینترنت..."):
                        answer = coordinator.agents[agent_type].search(state)
                    st.markdown(answer)
                else:
                    answer = st.write_stream(coordinator.agents[agent_type].stream_response(state))
        except Exception as e:
            agent_type, answer = None, f"❌ خطا: {e}"
            st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "agent": agent_type.value if isinstance(agent_type, AgentType) else None}
    )
    if len(st.session_state.messages) == 2:
        st.rerun()
