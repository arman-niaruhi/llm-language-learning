"""Streamlit web app for the multi-agent language learning system."""

import os
import requests
import streamlit as st
from dotenv import load_dotenv
from src.agents.base_agent import DEFAULT_MODEL
from src.agents.coordinator_agent import CoordinatorAgent
from src.agents.vocabulary_agent import VocabularyAgent
from src.agents.grammar_agent import GrammarAgent
from src.agents.conversation_agent import ConversationAgent
from src.schemas.messages import AgentState, AgentType

load_dotenv(override=True)
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
USE_GROQ = os.getenv("LLM_PROVIDER", "ollama").lower() == "groq"

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
    "واژگان": AgentType.VOCABULARY,
    "گرامر": AgentType.GRAMMAR,
    "مکالمه": AgentType.CONVERSATION,
}
TUTOR_FA = {"vocabulary": "واژگان", "grammar": "گرامر", "conversation": "مکالمه"}
AGENT_ICONS = {"vocabulary": "📚", "grammar": "✏️", "conversation": "💬"}
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
        groq_model = os.getenv("GROQ_MODEL", "")
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


st.set_page_config(page_title="معلم زبان", page_icon="🎓")
st.markdown(
    """
    <style>
    .stApp, [data-testid="stSidebar"] { direction: rtl; }
    .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp li, .stApp label,
    [data-testid="stSidebar"] * { text-align: right; }
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
        st.markdown(msg["content"])

prompt = st.chat_input(f"هر سوالی دربارهٔ {LANGUAGE_FA[language]} بپرسید...")

if not st.session_state.messages and not prompt:
    st.markdown("**این‌ها را امتحان کنید:**")
    cols = st.columns(2)
    for i, text in enumerate(STARTERS.get(language, DEFAULT_STARTERS)):
        if cols[i % 2].button(text, use_container_width=True, key=f"starter_{i}"):
            prompt = text

if prompt:
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    coordinator = get_coordinator(tuple(models.items()), groq_api_key)
    state = AgentState(
        user_input=prompt,
        learning_language=language,
        difficulty_level=level,
        explanation_language=explain_in,
        history=history,
        current_agent=MODES[mode_label],
    )

    with st.chat_message("assistant"):
        try:
            with st.spinner("در حال انتخاب معلم..."):
                agent_type = coordinator.route(state)
            st.caption(f"{AGENT_ICONS.get(agent_type.value, '🤖')} معلم {TUTOR_FA[agent_type.value]}")
            answer = st.write_stream(coordinator.agents[agent_type].stream_response(state))
        except Exception as e:
            agent_type, answer = None, f"❌ خطا: {e}"
            st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "agent": agent_type.value if agent_type else None}
    )
    if len(st.session_state.messages) == 2:
        st.rerun()
