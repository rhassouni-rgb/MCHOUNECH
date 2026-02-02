import streamlit as st
from groq import Groq
import pandas as pd
import plotly.express as px
import time
import PyPDF2   # 📚 مكتبة قراءة ملفات الدروس
import os       # 📂 مكتبة التعامل مع ملفات النظام
import json     # 💾 للتعامل مع تحميل البيانات

# ========================================================
# 🔑 إعدادات النظام
# ========================================================
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.3-70b-versatile"

st.set_page_config(
    page_title="M'chouneche AI",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================================
# ⚙️ المحرك الخلفي (Backend Logic)
# ========================================================
try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error("❌ فشل الاتصال بالسيرفر الرئيسي.")
    st.stop()

# تهيئة متغيرات الجلسة
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "code_history" not in st.session_state: st.session_state.code_history = []
if "tokens_used" not in st.session_state: st.session_state.tokens_used = 0
if "ai_mode" not in st.session_state: st.session_state.ai_mode = "🚀 Rapide"
if "pdf_context" not in st.session_state: st.session_state.pdf_context = ""
if "db_context" not in st.session_state: st.session_state.db_context = ""
if "generated_code" not in st.session_state: st.session_state.generated_code = ""

# ========================================================
# 🛠️ دوال استخراج البيانات (PDF + Database)
# ========================================================
def load_local_database():
    file_path = "data.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

st.session_state.db_context = load_local_database()

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return None

# ========================================================
# 🎨 (CSS) التصميم والواجهة - التحديث الخرافي (Apple-like)
# ========================================================
st.markdown("""
<style>
    /* استيراد الخطوط */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    /* إعدادات عامة */
    * { font-family: 'Tajawal', sans-serif; box-sizing: border-box; }
    
    /* الخلفية الرئيسية - عمق كوني */
    .stApp {
        background: radial-gradient(ellipse at top, #0f172a 0%, #000000 100%),
                    radial-gradient(circle at 80% 20%, rgba(0, 242, 96, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 20% 80%, rgba(30, 60, 114, 0.2) 0%, transparent 50%);
        color: #ffffff;
        font-weight: 400;
    }

    /* تحسين القائمة الجانبية - تأثير الزجاج */
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 10, 15, 0.6) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(25px) saturate(180%);
        -webkit-backdrop-filter: blur(25px) saturate(180%);
        box-shadow: 5px 0 30px rgba(0,0,0,0.2);
    }

    /* تحسين منطقة رفع الملفات */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.03);
        padding: 20px;
        border-radius: 16px;
        border: 2px dashed rgba(0, 242, 96, 0.4);
        transition: all 0.3s ease;
        text-align: center;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #00f260;
        background-color: rgba(0, 242, 96, 0.05);
        box-shadow: 0 0 20px rgba(0, 242, 96, 0.1);
    }
    
    /* تحسين الأزرار - توهج ناعم */
    .stButton > button {
        background: linear-gradient(135deg, rgba(30, 60, 114, 0.8), rgba(42, 82, 152, 0.8));
        border: none;
        color: white;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2), inset 0 1px 1px rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 25px rgba(42, 82, 152, 0.4), 0 0 15px rgba(0, 242, 96, 0.3);
        background: linear-gradient(135deg, rgba(30, 60, 114, 1), rgba(42, 82, 152, 1));
    }

    /* =================================================================
       🔥 تصميم الـ HERO SECTION الفاخر 🔥
    ================================================================= */
    .hero-wrapper {
        position: relative;
        width: 100%;
        height: 420px; 
        border-radius: 24px;
        overflow: hidden;
        margin-bottom: 40px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: left;
        isolation: isolate;
    }

    .hero-bg {
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-size: cover;
        background-position: center;
        z-index: 1;
        transition: transform 1.2s cubic-bezier(0.22, 1, 0.36, 1);
        filter: saturate(0.9) brightness(0.8);
    }
    
    .hero-wrapper:hover .hero-bg {
        transform: scale(1.08);
        filter: saturate(1.1) brightness(0.9);
    }

    .hero-content {
        position: relative;
        z-index: 2;
        padding: 50px;
        width: 100%;
        /* تدرج لوني سينمائي فاخر */
        background: linear-gradient(to right, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.6) 50%, rgba(0,0,0,0.2) 100%);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        backdrop-filter: blur(2px);
    }

    .hero-welcome {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.1rem;
        color: #00f260;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-bottom: 10px;
        text-shadow: 0 0 10px rgba(0, 242, 96, 0.6);
        font-weight: 700;
    }

    .hero-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 4rem;
        font-weight: 900;
        color: #ffffff;
        margin: 0;
        line-height: 1.05;
        /* نص متدرج معدني فاخر */
        background: linear-gradient(to right bottom, #ffffff 20%, #b0b0b0 50%, #e0e0e0 80%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 10px 25px rgba(0,0,0,0.5));
    }

    .hero-subtitle {
        font-family: 'Tajawal', sans-serif;
        color: #e0e0e0;
        font-size: 1.25rem;
        margin-top: 25px;
        border-left: 4px solid #00f260;
        padding-left: 20px;
        line-height: 1.6;
        font-weight: 500;
        background: linear-gradient(90deg, rgba(0, 242, 96, 0.08) 0%, transparent 100%);
        border-radius: 0 12px 12px 0;
        padding-top: 10px; padding-bottom: 10px;
    }
    
    /* تحسين النصوص العادية */
    b { color: #fff; font-weight: 700; }

    /* ================================================================= */

    /* بطاقات المعلومات - Glassmorphism */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(15px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    }
    .metric-card:hover { 
        transform: translateY(-5px); 
        border-color: rgba(0, 242, 96, 0.4);
        box-shadow: 0 15px 40px 0 rgba(0, 242, 96, 0.15);
    }
    .metric-card h3 { color: #00f260; margin-bottom: 10px; letter-spacing: 1px; }
    .metric-card p { color: #aaa; font-size: 1.1rem; }

    /* تحسين جداول البيانات */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* تحسين رسائل التنبيه */
    .stAlert {
        background-color: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px);
    }
    
    /* تحسين حقول الإدخال (Selectbox, Textarea) */
    .stSelectbox > div > div, .stTextArea > div > div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #fff !important;
    }
    .stSelectbox > div > div:hover, .stTextArea > div > div:hover {
        border-color: rgba(0, 242, 96, 0.5) !important;
    }
    
    /* تحسين منطقة الكود */
    .stCode {
        border-radius: 16px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    /* 📱 تحسينات للهاتف */
    @media only screen and (max-width: 600px) {
        .hero-title { font-size: 2.5rem !important; }
        .hero-wrapper { height: 300px !important; }
        .hero-content { padding: 25px !important; }
        .hero-subtitle { font-size: 1rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# ========================================================
# 📱 القائمة الجانبية
# ========================================================
with st.sidebar:
    logo_url_sidebar = "https://i.ytimg.com/vi/F7xbvIjaSxo/maxresdefault.jpg?sqp=-oaymwEmCIAKENAF8quKqQMa8AEB-AH-CYAC0AWKAgwIABABGGUgWShMMA8=&rs=AOn4CLA93JOcGvVuvrfild4Qr88EPbMBhQ"
    
    st.markdown(f"""
    <style>
        .logo-container {{
            display: flex;
            justify-content: center;
            margin-bottom: 25px;
            position: relative;
        }}
        .logo-img-side {{
            width: 140px; height: 140px;
            border-radius: 50%;
            border: 3px solid rgba(0, 242, 96, 0.8);
            box-shadow: 0 0 40px rgba(0, 242, 96, 0.3);
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            background: rgba(255,255,255,0.05);
            padding: 6px;
            object-fit: cover;
            backdrop-filter: blur(5px);
        }}
        .logo-img-side:hover {{
            transform: scale(1.05) rotate(5deg);
            box-shadow: 0 0 60px rgba(0, 198, 255, 0.6);
            border-color: rgba(0, 198, 255, 0.8);
        }}
    </style>
    <div class="logo-container"><img src="{logo_url_sidebar}" class="logo-img-side"></div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: center; color: white; font-family: Orbitron; letter-spacing: 2px; text-shadow: 0 0 15px rgba(0,242,96,0.4);'>M'CHOUNECHE AI</h2>", unsafe_allow_html=True)
    st.caption("Dev: Hassouni Raed | ESTA Student")
    st.markdown("---")
    
    mode = st.radio("القائمة:", 
        ["💬 المحادثة الذكية", "💻 استوديو الأكواد", "📊 تحليل البيانات", "⚙️ الإعدادات"],
        index=0
    )
    
    st.markdown("---")

    # 🔥 قسم حالة قاعدة البيانات 🔥
    if st.session_state.db_context:
        st.success("✅ قاعدة البيانات (data.txt): متصلة")
    else:
        st.warning("⚠️ قاعدة البيانات (data.txt): غير موجودة")
    
    st.markdown("---")
    
    # 🔥 قسم رفع ملفات الدروس 🔥
    st.markdown("### 📚 ملفات الدروس (PDF)")
    uploaded_pdf = st.file_uploader("ارفع الدرس هنا", type="pdf", key="pdf_uploader")
    
    if uploaded_pdf:
        with st.spinner("📥 جاري تحليل الملف..."):
            extracted_text = extract_text_from_pdf(uploaded_pdf)
            if extracted_text:
                st.session_state.pdf_context = extracted_text
                st.success("✅ تم حفظ المحتوى في الذاكرة!")
            else:
                st.error("❌ ملف غير صالح")
    
    if st.session_state.pdf_context:
        char_count = len(st.session_state.pdf_context)
        if char_count > 20000:
            st.warning(f"⚠️ ملف كبير ({char_count} حرف). سيتم استخدام أول 20 ألف حرف.")
        else:
            st.info(f"💡 المحتوى النشط: {char_count} حرف")

    st.markdown("---")
    col_a, col_b = st.columns(2)
    col_a.metric("Ping", "12ms", "-2ms")
    col_b.metric("Chats", len(st.session_state.chat_history), "Active")

# ========================================================
# 1️⃣ وحدة المحادثة الذكية
# ========================================================
if mode == "💬 المحادثة الذكية":
    
    # الرابط الخاص بك للبانر
    banner_image_url = "https://scontent.falg4-1.fna.fbcdn.net/v/t39.30808-6/617462444_1290177182886204_3419228806314042802_n.jpg?_nc_cat=110&ccb=1-7&_nc_sid=aa7b47&_nc_eui2=AeF1b-6-EYFKDLejb4gp-eLNU3S7x9Fco_pTdLvH0Vyj-qCMW4F3fao-z_uerYF2ZhRgEDxq2nvI6A2T7UxjoeUO&_nc_ohc=1G23haZEeY8Q7kNvwGzSFyV&_nc_oc=AdmTadT3fR9Yr0AuYaWg5ib8b2aNA_fJzhZ2mvwc0ddxFf6juA9W9sCWb8I0qcDrap8&_nc_zt=23&_nc_ht=scontent.falg4-1.fna&_nc_gid=UXi1zrPr-nc0YzNSVZ6SNQ&oh=00_Afu2yPXWMydy1dCoNmmp86pybMzg1ROT-1XVzMsvv8S7Sg&oe=6985691D"

    st.markdown(f"""
    <div class="hero-wrapper">
        <div class="hero-bg" style="background-image: url('{banner_image_url}');"></div>
        <div class="hero-content">
            <div class="hero-welcome">SMART CITY GUIDE</div>
            <div class="hero-title">WELCOME TO<br>M'CHOUNECHE</div>
            <div class="hero-subtitle">
                <b>المطور: حسوني رائد</b><br>
                طالب المدرسة العليا لتكنولوجيا متقدمة (ESTA)<br>
                مقيم في: ميوري & وهران
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # زر تحميل المحادثة
    if st.session_state.chat_history:
        chat_str = "\n".join([f"[{m['role'].upper()}]: {m['content']}" for m in st.session_state.chat_history])
        st.download_button("💾 تحميل سجل المحادثة", chat_str, file_name="chat_history.txt", mime="text/plain")

    # عرض الشات
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # تحديد الألوان والأيقونة
    if st.session_state.ai_mode == "🚀 Rapide":
        theme_color = "#ffffff"
        btn_icon = "🚀"
        sys_suffix = " أجب بسرعة فائقة واختصار. استخدم النقاط."
    elif st.session_state.ai_mode == "💠 Pro":
        theme_color = "#00f260"
        btn_icon = "💠"
        sys_suffix = " أجب بتفصيل هندسي متوازن ودقيق."
    else: # Pro Max
        theme_color = "#ff2a2a"
        btn_icon = "🧠"
        sys_suffix = " وضع التفكير العميق. حلل كل الجوانب."

    # CSS للأزرار وقائمة المود - تصميم فاخر (مصحح)
    st.markdown(f"""
    <style>
        div[data-testid="stPopover"] {{
            position: fixed !important; bottom: 40px !important; right: 90px !important;
            z-index: 1000000 !important; display: block !important; width: auto !important;
        }}
        div[data-testid="stPopover"] button {{
            background-color: rgba(20, 20, 30, 0.9) !important;
            border: 2px solid {theme_color} !important; color: {theme_color} !important;
            border-radius: 50% !important; width: 55px !important; height: 55px !important;
            box-shadow: 0 0 25px {theme_color}60 !important;
            backdrop-filter: blur(10px) !important;
            transition: all 0.3s ease !important;
            font-size: 1.5rem !important;
        }}
        div[data-testid="stPopover"] button:hover {{
            transform: scale(1.1) !important;
            box-shadow: 0 0 40px {theme_color} !important;
        }}
        
        div[data-testid="stChatInput"] {{
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 30px !important;
            background-color: rgba(255,255,255,0.05) !important;
            backdrop-filter: blur(20px) !important;
            box-shadow: 0 -10px 30px rgba(0,0,0,0.3) !important;
            padding: 5px !important;
        }}
        textarea[data-testid="stChatInputTextArea"] {{ 
            padding-right: 60px !important; caret-color: {theme_color} !important; color: #fff !important;
            background: transparent !important;
        }}
        button[data-testid="stChatInputSubmitButton"] {{ 
            color: {theme_color} !important; 
            background: rgba(255,255,255,0.05) !important;
            border-radius: 50% !important; height: 45px !important; width: 45px !important;
            border: 1px solid {theme_color}40 !important;
        }}
        button[data-testid="stChatInputSubmitButton"]:hover {{
            background: {theme_color}20 !important;
            box-shadow: 0 0 15px {theme_color} !important;
        }}
        
        .stChatMessage {{
            background: rgba(255,255,255,0.03) !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
            border-radius: 16px !important;
            backdrop-filter: blur(10px) !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
            transition: transform 0.2s;
        }}
        .stChatMessage:hover {{ transform: translateY(-2px); }}
        
        div[data-testid="chatAvatarIcon"] {{
            background: rgba(255,255,255,0.1) !important;
            border: 1px solid {theme_color}60 !important;
        }}
        
        /* 📱 تحسينات للهاتف */
        @media only screen and (max-width: 600px) {{
             div[data-testid="stPopover"] {{
                bottom: 80px !important; right: 20px !important;
                width: 45px !important; height: 45px !important; font-size: 1.2rem !important;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)

    with st.popover(btn_icon, use_container_width=False):
        st.markdown(f"### Current Mode: {st.session_state.ai_mode}")
        st.session_state.ai_mode = st.radio("Select Level:", ["🚀 Rapide", "💠 Pro", "🧠 Pro Max"], index=["🚀 Rapide", "💠 Pro", "🧠 Pro Max"].index(st.session_state.ai_mode))

    # --------------------------------------------------------
    # إعداد الـ Prompt (تم تحديث الهوية هنا)
    # --------------------------------------------------------
    # تم تحديث المعلومات الخاصة بالمبرمج حسوني رائد ومكان إقامته
    programmer_info = " ملاحظة هامة جداً: إذا سألك المستخدم 'من برمجك؟' أو 'من رئيسك؟' أو 'من صنعك؟' يجب أن تجيب حرفياً بهذه الجملة فقط: 'رئيسي هو حسوني رائد، طالب بالمدرسة العليا لتكنولوجيات متقدمة، ومقيم في ميوري ووهران'."
    
    # تجهيز سياق البيانات
    context_instruction = ""
    if st.session_state.db_context:
        context_instruction += f"\n[PERMANENT DATABASE INFO]:\n{st.session_state.db_context}\n(Use this as primary source for M'chouneche info.)"
    if st.session_state.pdf_context:
        context_instruction += f"\n[CURRENT LESSON CONTEXT (PDF)]: \n{st.session_state.pdf_context[:20000]}\n(Use this for academic questions.)"
    
    # تحديث البرومبت الأساسي ليكون خبيراً في مشونش
    base_prompt = "أنت مساعد ذكي ومرشد سياحي وتقني لمدينة مشونش، وأيضاً خبير في الأنظمة المدمجة." + programmer_info + context_instruction
    sys_prompt = base_prompt + sys_suffix

    # خانة الكتابة
    prompt = st.chat_input("اسأل عن مدينة مشونش أو الأنظمة المدمجة...")
    
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        if st.session_state.ai_mode == "🧠 Pro Max":
            # تحسين مظهر الـ status
            st.markdown("""<style>.stStatusWidget { background: rgba(255,255,255,0.05) !important; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; }</style>""", unsafe_allow_html=True)
            with st.status("🧠 جارٍ التفكير العميق...", expanded=True) as status:
                st.write("🔍 تحليل السؤال...")
                time.sleep(0.5)
                if st.session_state.db_context: st.write("📂 البحث في بيانات مشونش (DB)...")
                if st.session_state.pdf_context: st.write("📚 البحث في الملفات (PDF)...")
                time.sleep(0.5)
                st.write("💡 صياغة الإجابة...")
                status.update(label="✅ تم التحليل", state="complete", expanded=False)

        messages = [{"role": "system", "content": sys_prompt}] + [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history
        ]

        with st.chat_message("assistant"):
            resp_container = st.empty()
            full_resp = ""
            completion = client.chat.completions.create(model=MODEL_ID, messages=messages, temperature=0.7, stream=True)
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_resp += chunk.choices[0].delta.content
                    resp_container.markdown(full_resp + "▌")
            resp_container.markdown(full_resp)
        
        st.session_state.chat_history.append({"role": "assistant", "content": full_resp})

# ========================================================
# بقية الأقسام (Code Studio, Analytics, Settings)
# ========================================================
elif mode == "💻 استوديو الأكواد":
    st.title("💻 معماري البرمجيات (Code Architect)")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("📝 المتطلبات")
        lang = st.selectbox("اللغة:", ["C (Embedded)", "Assembly", "Python", "C++", "VHDL"])
        code_req = st.text_area("اشرح الكود المطلوب:", height=200)
        generate_btn = st.button("⚡ توليد الكود")
    
    with col2:
        st.subheader("🖥️ النتيجة")
        if generate_btn and code_req:
            with st.spinner("جاري الكتابة..."):
                prompt_code = f"Write professional {lang} code for: {code_req}. Only code, no explanation."
                resp = client.chat.completions.create(model=MODEL_ID, messages=[{"role": "user", "content": prompt_code}])
                generated_code = resp.choices[0].message.content
                st.session_state.generated_code = generated_code # حفظ الكود
                st.code(generated_code, language=lang.lower().split()[0])
        elif st.session_state.generated_code:
             st.code(st.session_state.generated_code, language=lang.lower().split()[0])
        else:
            st.info("النتيجة ستظهر هنا...")
        
        # زر تحميل الكود
        if st.session_state.generated_code:
            ext_map = {"C (Embedded)": "c", "Assembly": "s", "Python": "py", "C++": "cpp", "VHDL": "vhd"}
            file_ext = ext_map.get(lang, "txt")
            st.download_button(
                label="💾 تحميل الكود (Download)",
                data=st.session_state.generated_code,
                file_name=f"generated_code.{file_ext}",
                mime="text/plain"
            )

elif mode == "📊 تحليل البيانات":
    st.title("📊 مركز البيانات البصري")
    uploaded_file = st.file_uploader("ارفع ملف CSV", type=['csv'])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head())
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 تحليل AI"):
                res = client.chat.completions.create(model=MODEL_ID, messages=[{"role": "user", "content": f"Analyze: {list(df.columns)}" }])
                st.write(res.choices[0].message.content)
            
            # إحصائيات سريعة
            with st.expander("📈 إحصائيات سريعة"):
                st.write(df.describe())

        with col2:
            x_axis = st.selectbox("X", df.columns)
            y_axis = st.selectbox("Y", df.columns)
            st.plotly_chart(px.bar(df, x=x_axis, y=y_axis), use_container_width=True)
    else:
        st.warning("وضع العرض التجريبي (Demo Mode)")
        st.plotly_chart(px.bar(x=['A','B','C'], y=[10,20,30]), use_container_width=True)

elif mode == "⚙️ الإعدادات":
    st.title("⚙️ النظام")
    # تحديث معلومات الطالب في الإعدادات - تصميم بطاقة فاخر
    st.markdown("""
    <div class="metric-card" style="text-align: left; display: flex; align-items: center; gap: 20px;">
        <div style="font-size: 3rem;">👨‍💻</div>
        <div>
            <h3 style="margin: 0; color: #ffffff;">Hassouni Raed</h3>
            <p style="margin: 5px 0 0 0; color: #00f260;">ESTA Student - ACCESS GRANTED</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_x, col_y = st.columns(2)
    with col_x:
        if st.session_state.pdf_context:
            st.success("📚 PDF Context: Loaded")
            st.text(f"Size: {len(st.session_state.pdf_context)} chars")
        else:
            st.error("📚 PDF Context: Empty")
            
    with col_y:
        if st.session_state.db_context:
            st.success("💾 Database (data.txt): Loaded")
        else:
            st.error("💾 Database (data.txt): Missing")
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧹 مسح المحادثة فقط"):
            st.session_state.chat_history = []
            st.rerun()
            
    with c2:
        if st.button("🗑️ Reset All Memory (Format)"):
            st.session_state.chat_history = []
            st.session_state.pdf_context = ""
            st.session_state.generated_code = ""
            st.session_state.db_context = load_local_database() # إعادة تحميل قاعدة البيانات
            st.rerun()
