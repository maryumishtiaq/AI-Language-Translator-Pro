import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
from fpdf import FPDF
import tempfile
import pyperclip
import time

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="AI Language Translator Pro",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# SESSION STATE
# ==========================================================

if "translated" not in st.session_state:
    st.session_state.translated = ""

if "history" not in st.session_state:
    st.session_state.history = []

if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ==========================================================
# LANGUAGE LIST
# ==========================================================

languages = GoogleTranslator().get_supported_languages(as_dict=True)
language_names = sorted(languages.keys())

# ==========================================================
# THEME
# ==========================================================

theme = st.sidebar.radio(
    "🌗 Theme",
    ["Light", "Dark"],
    index=0
)

if theme == "Dark":
    bg = "#0E1117"
    card = "#1E1E1E"
    text_color = "white"
else:
    bg = "#667eea"
    card = "rgba(255,255,255,0.15)"
    text_color = "black"

# ==========================================================
# CSS
# ==========================================================

st.markdown(f"""
<style>

.stApp {{
    background: {bg};
}}

.main-card {{
    background: {card};
    padding:25px;
    border-radius:20px;
    box-shadow:0px 10px 25px rgba(0,0,0,.30);
}}

.title {{
    text-align:center;
    font-size:45px;
    color:{text_color};
    font-weight:bold;
}}

.subtitle {{
    text-align:center;
    color:{text_color};
    margin-bottom:25px;
}}

.stButton > button {{
    width:100%;
    border-radius:10px;
    height:50px;
    font-size:18px;
}}

footer {{
    visibility:hidden;
}}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================

st.markdown(
"""
<div class="title">
🌍 AI Language Translator Pro
</div>

<div class="subtitle">
Translate into 100+ Languages Instantly
</div>
""",
unsafe_allow_html=True
)

st.markdown("<div class='main-card'>", unsafe_allow_html=True)

# ==========================================================
# TEXT INPUT
# ==========================================================

text = st.text_area(
    "✍ Enter Text",
    placeholder="Type your text here...",
    height=180
)

# ==========================================================
# CHARACTER & WORD COUNTER
# ==========================================================

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "📊 Characters",
        len(text)
    )

with col2:
    words = len(text.split()) if text.strip() else 0

    st.metric(
        "📝 Words",
        words
    )

st.markdown("---")

# ==========================================================
# LANGUAGE SELECTION
# ==========================================================

left, right = st.columns(2)

with left:

    source = st.selectbox(
        "🌐 Source Language",
        ["auto"] + language_names,
        index=0,
        key="source_lang"
    )

with right:

    target = st.selectbox(
        "🎯 Target Language",
        language_names,
        index=language_names.index("english"),
        key="target_lang"
    )

# ==========================================================
# SWAP BUTTON
# ==========================================================

colA, colB, colC = st.columns([1, 1, 1])

with colB:

    if st.button("🔄 Swap Languages"):

        if source != "auto":

            source, target = target, source

            st.success("✅ Languages Swapped!")

st.markdown("---")

# ==========================================================
# TRANSLATE BUTTON
# ==========================================================

if st.button("🌍 Translate", use_container_width=True):

    if text.strip() == "":
        st.warning("⚠ Please enter some text.")

    else:

        try:

            with st.spinner("🔄 Translating..."):
                time.sleep(1)

                translated = GoogleTranslator(
                    source=source,
                    target=target
                ).translate(text)

            st.session_state.translated = translated

            st.session_state.history.append({
                "input": text,
                "output": translated,
                "source": source,
                "target": target
            })

            st.success("✅ Translation Completed Successfully!")

        except Exception as e:

            st.error(f"Translation Failed: {e}")

# ==========================================================
# OUTPUT
# ==========================================================

if st.session_state.translated:

    st.text_area(
        "📄 Translated Text",
        value=st.session_state.translated,
        height=180
    )

# ==========================================================
# QUICK ACTIONS
# ==========================================================

if st.session_state.translated:

    col1, col2, col3 = st.columns(3)

    # ---------- COPY ----------

    with col1:

        if st.button("📋 Copy"):

            pyperclip.copy(st.session_state.translated)

            st.success("Copied!")

    # ---------- CLEAR ----------

    with col2:

        if st.button("🗑 Clear"):

            st.session_state.translated = ""

            st.rerun()

    # ---------- DOWNLOAD TXT ----------

    with col3:

        st.download_button(
            label="📥 Download TXT",
            data=st.session_state.translated,
            file_name="translation.txt",
            mime="text/plain"
        )

st.markdown("---")

# ==========================================================
# PDF DOWNLOAD
# ==========================================================

if st.session_state.translated:

    st.subheader("📄 Export Options")

    if st.button("📄 Prepare PDF"):

        try:

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=14)

            pdf.multi_cell(
                0,
                10,
                txt=st.session_state.translated
            )

            pdf_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            )

            pdf.output(pdf_file.name)

            with open(pdf_file.name, "rb") as file:

                st.download_button(
                    "⬇ Download PDF",
                    data=file,
                    file_name="translation.pdf",
                    mime="application/pdf"
                )

        except Exception:

            st.warning(
                "PDF supports English text only. Unicode languages need a Unicode font."
            )

# ==========================================================
# TEXT TO SPEECH
# ==========================================================

if st.session_state.translated:

    show_voice = st.checkbox(
        "🔊 Enable Voice",
        value=True
    )

    if show_voice:

        try:

            tts = gTTS(
                text=st.session_state.translated,
                lang="en"
            )

            audio_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp3"
            )

            tts.save(audio_file.name)

            st.audio(audio_file.name)

        except Exception:

            st.warning(
                "Voice is not available for this language."
            )

# ==========================================================
# FAVORITE LANGUAGES
# ==========================================================

st.subheader("⭐ Favorite Languages")

favorite = st.selectbox(
    "Choose Language",
    language_names,
    key="favorite_language"
)

if st.button("⭐ Add Favorite"):

    if favorite not in st.session_state.favorites:

        st.session_state.favorites.append(favorite)

        st.success(f"{favorite.title()} added successfully!")

    else:

        st.info("Already added.")

if st.session_state.favorites:

    st.write("### ⭐ Saved Languages")

    for lang in st.session_state.favorites:

        st.success(lang.title())

# ==========================================================
# HISTORY
# ==========================================================

st.markdown("---")

st.subheader("📜 Translation History")

if len(st.session_state.history) == 0:

    st.info("No translations yet.")

else:

    for item in reversed(st.session_state.history):

        with st.expander(item["input"][:40]):

            st.write("**Input:**")
            st.write(item["input"])

            st.write("**Translation:**")
            st.success(item["output"])

            st.caption(
                f"{item['source']} ➜ {item['target']}"
            )

st.markdown("---")

# ==========================================================
# TRANSLATION STATISTICS
# ==========================================================

if st.session_state.translated:

    st.subheader("📊 Translation Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Characters",
            len(st.session_state.translated)
        )

    with col2:
        st.metric(
            "Words",
            len(st.session_state.translated.split())
        )

    with col3:
        st.metric(
            "Total Translations",
            len(st.session_state.history)
        )

# ==========================================================
# SHARE TIP
# ==========================================================

st.markdown("---")

st.info("""
💡 **Tip**

Use the **Copy** button to quickly share your translation on:

• WhatsApp
• Gmail
• Facebook
• Instagram
• Notes
""")

# ==========================================================
# SUCCESS ANIMATION
# ==========================================================

if st.session_state.translated:
    st.balloons()

# ==========================================================
# CLOSE MAIN CARD
# ==========================================================

st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("""
<style>

.footer{
margin-top:40px;
padding:25px;
border-radius:20px;
text-align:center;
background:rgba(255,255,255,0.10);
backdrop-filter:blur(12px);
color:white;
font-size:16px;
}

.footer h2{
margin-bottom:10px;
}

</style>

<div class="footer">

<h2>🌍 AI Language Translator Pro</h2>

<p>Made with ❤️ using Python, Streamlit & Deep Translator</p>

<p><b>CodeAlpha AI Internship Project</b></p>

<hr>

<p>

🌗 Dark / Light Theme &nbsp; | &nbsp;
🌍 100+ Languages &nbsp; | &nbsp;
📄 PDF Export &nbsp; | &nbsp;
🔊 Voice &nbsp; | &nbsp;
📋 Copy &nbsp; | &nbsp;
⭐ Favorites &nbsp; | &nbsp;
📜 History

</p>

</div>

""", unsafe_allow_html=True)
