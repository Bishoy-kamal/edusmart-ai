import streamlit as st
import PyPDF2
from transformers import pipeline
import pandas as pd
import os

@st.cache_resource
def load_ai():
    return pipeline("text-generation", model="facebook/bart-large-cnn")
    
ai = load_ai()

st.set_page_config(page_title="EduSmart AI", page_icon="📚", layout="wide")

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        color: #1f77b4;
    }
    .sub-title {
        text-align: center;
        font-size: 18px;
        color: gray;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<p class="main-title">📚 EduSmart AI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">منصة ذكية لتحليل وتلخيص الملفات التعليمية</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفع ملف PDF", type="pdf")

def read_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
        return text
    except Exception as e:
        st.error(f"تعذر قراءة الملف: {e}")
        return ""

def simple_summarize(text):
    sentences = text.split(".")
    return ". ".join(sentences[:5])

def save_data(filename, text):
    words = len(text.split())
    new_data = pd.DataFrame([{"file_name": filename, "word_count": words}])

    if os.path.exists("students.csv"):
        old_data = pd.read_csv("students.csv")
        all_data = pd.concat([old_data, new_data], ignore_index=True)
    else:
        all_data = new_data

    all_data.to_csv("students.csv", index=False)

if uploaded_file:
    text = read_pdf(uploaded_file)
    save_data(uploaded_file.name, text)

    st.success("تم رفع الملف وتحليله بنجاح ✅")

    tab1, tab2, tab3 = st.tabs(["📄 النص", "🧠 الملخص", "📊 الإحصائيات"])

    with tab1:
        st.text_area("محتوى الملف", text, height=350)

    with tab2:
        summary = simple_summarize(text)
        st.text_area("الملخص", summary, height=350)

    with tab3:
        data = pd.read_csv("students.csv")
        st.dataframe(data, use_container_width=True)

    def summarize(text):
    text = text[:800]  # مهم جدًا لتفادي overflow

    prompt = "Summarize this text in simple points:\n" + text

    result = ai(
        prompt,
        max_new_tokens=120,
        do_sample=False,
        truncation=True
    )

    return result[0]["generated_text"]


def generate_questions(text):
    prompt = f"اكتب 5 أسئلة تعليمية مع إجابات من النص التالي:\n{text[:1000]}"
    result = ai(prompt, max_length=250, do_sample=False)
    return result[0]["generated_text"]
if uploaded_file:
    text = read_pdf(uploaded_file)

    st.success("تم رفع الملف بنجاح ✅")

    col1, col2 = st.columns(2)

    # 🧠 الخطوة 3: تلخيص
    with col1:
        if st.button("🧠 تلخيص ذكي"):
            with st.spinner("جاري التحليل..."):
                st.write(summarize(text))

    # ❓ الخطوة 4: أسئلة
    with col2:
        if st.button("❓ توليد أسئلة"):
            with st.spinner("جاري إنشاء الأسئلة..."):
                st.write(generate_questions(text))
