import streamlit as st
from groq import Groq
import pandas as pd
import plotly.express as px
import time
import PyPDF2   # 📚 مكتبة قراءة ملفات الدروس
import os       # 📂 مكتبة التعامل مع ملفات النظام
import json     # 💾 للتعامل مع تحميل البيانات
USER_IMG = "https://cdn-icons-png.flaticon.com/512/9374/9374918.png"  # صورة المستخدم
BOT_IMG  = "https://cdn-icons-png.flaticon.com/512/8943/8943377.png"  # صورة الروبوت
# ========================================================
# 🔑 إعدادات النظام
# ========================================================
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"

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
# متغير الثيم
if "theme_mode" not in st.session_state: st.session_state.theme_mode = "🌑 ليلي"

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
# 🎨 (CSS) التصميم والواجهة - التحديث الجديد (Gemini Glass Style)
# ========================================================

# تحديد الألوان بناءً على الوضع المختار
if st.session_state.theme_mode == "🌑 ليلي":
    # --- الألوان الليلية ---
    main_bg = "radial-gradient(ellipse at top, #0f172a 0%, #000000 100%), radial-gradient(circle at 80% 20%, rgba(0, 242, 96, 0.1) 0%, transparent 50%), radial-gradient(circle at 20% 80%, rgba(30, 60, 114, 0.2) 0%, transparent 50%)"
    text_color = "#ffffff"
    input_text_color = "#ffffff"
    input_bg = "rgba(255, 255, 255, 0.05)"
    sidebar_bg = "rgba(10, 10, 15, 0.6)"
    card_bg = "rgba(255, 255, 255, 0.03)"
    border_color = "rgba(255, 255, 255, 0.08)"
    shadow_color = "rgba(0,0,0,0.2)"
    radio_bg = "rgba(255, 255, 255, 0.1)" # خلفية زر الثيم
    
    # 🔥 ألوان الشريط السفلي (ليلي - زجاجي داكن)
    chat_bar_bg = "rgba(20, 20, 25, 0.6)" # زيادة الشفافية
    chat_bar_border = "rgba(255, 255, 255, 0.15)"
    
else:
    # --- الألوان النهارية ---
    main_bg = "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
    text_color = "#1e293b" 
    input_text_color = "#000000"
    input_bg = "rgba(255, 255, 255, 0.8)"
    sidebar_bg = "rgba(255, 255, 255, 0.7)"
    card_bg = "rgba(255, 255, 255, 0.6)"
    border_color = "rgba(0, 0, 0, 0.1)"
    shadow_color = "rgba(0,0,0,0.05)"
    radio_bg = "rgba(0, 0, 0, 0.05)" # خلفية زر الثيم
    
    # 🔥 ألوان الشريط السفلي (نهاري - زجاجي فاتح)
    chat_bar_bg = "rgba(255, 255, 255, 0.5)" # زيادة الشفافية
    chat_bar_border = "rgba(0, 0, 0, 0.1)"

st.markdown(f"""
<style>
    /* استيراد الخطوط */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    /* إعدادات عامة */
    * {{ font-family: 'Tajawal', sans-serif; box-sizing: border-box; }}
    
    /* الخلفية الرئيسية */
    .stApp {{
        background: {main_bg};
        background-attachment: fixed;
        color: {text_color};
    }}

    /* 🔥🔥🔥 الشريط العلوي (Header) 🔥🔥🔥 */
    header[data-testid="stHeader"] {{
        background-color: transparent !important;
        backdrop-filter: blur(5px);
    }}
    header[data-testid="stHeader"] button, header[data-testid="stHeader"] svg {{
        color: {text_color} !important; 
    }}
    
    /* 🔥🔥🔥 الشريط السفلي (Footer & Bottom Container) - الحل الجذري 🔥🔥🔥 */
    footer {{
        visibility: hidden;
        height: 0px;
    }}
    
    /* جعل الحاوية الكبيرة السفلية شفافة تماماً لإظهار خلفية الموقع */
    div[data-testid="stBottom"] {{
        background-color: transparent !important;
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        backdrop-filter: none !important;
    }}
    
    div[data-testid="stBottom"] > div {{
        background-color: transparent !important;
    }}

    /* 🔥🔥🔥 تصميم خانة الكتابة السفلية (Gemini Glass Style) 🔥🔥🔥 */
    /* التعديل: شكل مستطيل بحواف ناعمة بدلاً من الشكل الدائري */
    div[data-testid="stChatInput"] {{
        background-color: {chat_bar_bg} !important; 
        backdrop-filter: blur(20px) saturate(180%) !important; /* تأثير زجاجي قوي */
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border-radius: 12px !important; /* 🔥 تحويله إلى مستطيل بحواف ناعمة (Gemini Style) */
        border: 1px solid {chat_bar_border} !important;
        padding: 10px 15px !important; /* مساحة داخلية مريحة */
        box-shadow: 0 8px 32px rgba(0,0,0,0.2) !important;
        margin-bottom: 30px !important; /* يطفو أعلى من الحافة السفلية */
        transition: all 0.3s ease;
    }}
    
    div[data-testid="stChatInput"]:hover {{
        box-shadow: 0 12px 40px rgba(0,0,0,0.3) !important;
        border-color: rgba(0, 242, 96, 0.3) !important;
    }}
    
    /* 🔥🔥🔥 تصميم زر الثيم (Apple Segmented Control) 🔥🔥🔥 */
    /* إخفاء الدوائر التقليدية */
    div[role="radiogroup"] label > div:first-child {{
        display: none !important;
    }}
    
    /* حاوية الزر */
    div[role="radiogroup"] {{
        background-color: {radio_bg};
        padding: 4px;
        border-radius: 12px;
        border: 1px solid {border_color};
        display: flex;
        gap: 5px;
    }}
    
    /* الأزرار الداخلية */
    div[role="radiogroup"] label {{
        flex: 1;
        background-color: transparent;
        border-radius: 8px;
        text-align: center;
        padding: 8px 10px !important;
        margin: 0 !important;
        border: 1px solid transparent;
        cursor: pointer;
        transition: all 0.3s ease;
        justify-content: center;
    }}
    
    /* تأثير التحويم */
    div[role="radiogroup"] label:hover {{
        background-color: rgba(128, 128, 128, 0.1);
    }}
    
    /* ------------------------------------------------ */
    
    /* إصلاح منطقة المحتوى الرئيسي */
    .block-container {{
        padding-top: 3rem;
        padding-bottom: 9rem; /* مسافة كافية للأسفل لعدم تغطية المحتوى */
    }}

    /* تصحيح ألوان النصوص في الحقول */
    .stTextInput input, .stTextArea textarea, .stSelectbox div, .stNumberInput input, input, textarea {{
        color: {input_text_color} !important;
        -webkit-text-fill-color: {input_text_color} !important;
        caret-color: #00f260 !important;
        background-color: {input_bg} !important;
    }}
    
    /* لون النصوص العامة */
    p, h1, h2, h3, h4, h5, h6, li, span, div {{
        color: {text_color};
    }}

    /* تحسين القائمة الجانبية */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {border_color};
        backdrop-filter: blur(25px) saturate(180%);
        -webkit-backdrop-filter: blur(25px) saturate(180%);
        box-shadow: 5px 0 30px {shadow_color};
    }}
    
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span {{
        color: {text_color} !important;
    }}

    /* تحسين منطقة رفع الملفات */
    [data-testid="stFileUploader"] {{
        background-color: {card_bg};
        padding: 20px;
        border-radius: 16px;
        border: 2px dashed rgba(0, 242, 96, 0.4);
        transition: all 0.3s ease;
        text-align: center;
    }}
    [data-testid="stFileUploader"]:hover {{
        border-color: #00f260;
        background-color: rgba(0, 242, 96, 0.05);
        box-shadow: 0 0 20px rgba(0, 242, 96, 0.1);
    }}
    
    /* تحسين الأزرار العامة (غير زر الثيم) */
    .stButton > button {{
        background: linear-gradient(135deg, rgba(30, 60, 114, 0.8), rgba(42, 82, 152, 0.8));
        border: none;
        color: white !important;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2), inset 0 1px 1px rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }}
    .stButton > button:hover {{
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 25px rgba(42, 82, 152, 0.4), 0 0 15px rgba(0, 242, 96, 0.3);
        background: linear-gradient(135deg, rgba(30, 60, 114, 1), rgba(42, 82, 152, 1));
    }}
    .stButton > button p {{ color: white !important; }}

    /* Hero Section */
    .hero-wrapper {{
        position: relative;
        width: 100%;
        height: 420px; 
        border-radius: 24px;
        overflow: hidden;
        margin-bottom: 40px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
        border: 1px solid {border_color};
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: left;
        isolation: isolate;
    }}

    .hero-bg {{
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-size: cover;
        background-position: center;
        z-index: 1;
        transition: transform 1.2s cubic-bezier(0.22, 1, 0.36, 1);
        filter: saturate(0.9) brightness(0.8);
    }}
    
    .hero-wrapper:hover .hero-bg {{
        transform: scale(1.08);
        filter: saturate(1.1) brightness(0.9);
    }}

    .hero-content {{
        position: relative;
        z-index: 2;
        padding: 50px;
        width: 100%;
        background: linear-gradient(to right, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.6) 50%, rgba(0,0,0,0.2) 100%);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        backdrop-filter: blur(2px);
    }}

    .hero-welcome {{
        font-family: 'Orbitron', sans-serif;
        font-size: 1.1rem;
        color: #00f260 !important;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-bottom: 10px;
        text-shadow: 0 0 10px rgba(0, 242, 96, 0.6);
        font-weight: 700;
    }}

    .hero-title {{
        font-family: 'Orbitron', sans-serif;
        font-size: 4rem;
        font-weight: 900;
        color: #ffffff !important;
        margin: 0;
        line-height: 1.05;
        background: linear-gradient(to right bottom, #ffffff 20%, #b0b0b0 50%, #e0e0e0 80%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 10px 25px rgba(0,0,0,0.5));
    }}

    .hero-subtitle {{
        font-family: 'Tajawal', sans-serif;
        color: #e0e0e0 !important;
        font-size: 1.25rem;
        margin-top: 25px;
        border-left: 4px solid #00f260;
        padding-left: 20px;
        line-height: 1.6;
        font-weight: 500;
        background: linear-gradient(90deg, rgba(0, 242, 96, 0.08) 0%, transparent 100%);
        border-radius: 0 12px 12px 0;
        padding-top: 10px; padding-bottom: 10px;
    }}
    
    .hero-subtitle b {{ color: #fff !important; }}

    /* Cards */
    .metric-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(15px);
        box-shadow: 0 8px 32px 0 {shadow_color};
    }}
    .metric-card:hover {{ 
        transform: translateY(-5px); 
        border-color: rgba(0, 242, 96, 0.4);
        box-shadow: 0 15px 40px 0 rgba(0, 242, 96, 0.15);
    }}
    .metric-card h3 {{ color: #00f260 !important; margin-bottom: 10px; letter-spacing: 1px; }}
    .metric-card p {{ color: {text_color} !important; font-size: 1.1rem; opacity: 0.8; }}

    [data-testid="stDataFrame"] {{
        border: 1px solid {border_color};
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 10px 30px {shadow_color};
    }}
    
    .stAlert {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px);
    }}
    .stAlert div {{ color: {text_color} !important; }}
    
    .stSelectbox > div > div, .stTextArea > div > div {{
        background-color: {input_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 12px !important;
        color: {input_text_color} !important;
    }}
    .stSelectbox > div > div:hover, .stTextArea > div > div:hover {{
        border-color: rgba(0, 242, 96, 0.5) !important;
    }}
    
    .stCode {{
        border-radius: 16px !important;
        box-shadow: 0 10px 30px {shadow_color} !important;
        border: 1px solid {border_color} !important;
    }}
    
    /* 📱 تحسينات للهاتف */
    @media only screen and (max-width: 600px) {{
        .hero-title {{ font-size: 2.5rem !important; }}
        .hero-wrapper {{ height: 300px !important; }}
        .hero-content {{ padding: 25px !important; }}
        .hero-subtitle {{ font-size: 1rem !important; }}
        div[role="radiogroup"] {{ width: 100% !important; }}
    }}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
    /* ========================================== */
    /* 🔥 تفكيك اللون الأبيض (Nuclear Fix) 🔥 */
    /* ========================================== */
div[data-testid="stChatMessage"] + div[style*="background-color: rgb(255, 255, 255)"] {
        display: none !important;
    }
            div[data-testid="stChatMessage"] + div {
    display: none !important;
}

/* 2. استهداف أي زر تحميل (Download) قد يظهر تحت الرسائل */
.stDownloadButton {
    display: none !important;
}

/* 3. تنظيف أي خلفية بيضاء متبقية في أسفل الصفحة */
div.block-container {
    padding-bottom: 5rem !important;
}
    /* 1. تلوين الإطار الخارجي الأساسي (الحاوية الأم) */
    div[data-testid="stChatInput"] {
        background-color: #1A1A1A !important; /* لون داكن جداً */
        background: linear-gradient(135deg, #1A1A1A 0%, #2D2D2D 100%) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
        color: white !important;
    }

    /* 2. الهجوم الشامل: جعل كل الطبقات الداخلية شفافة */
    /* هذا السطر هو السر: يستهدف أي عنصر داخل الشات ويجبره أن يكون شفافاً */
    div[data-testid="stChatInput"] * {
        background-color: transparent !important;
        background: transparent !important;
    }

    /* 3. إعادة تنسيق حقل الكتابة ليظهر النص بالأبيض */
    textarea[data-testid="stChatInputTextArea"] {
        color: #FFFFFF !important; /* نص أبيض ناصع */
        caret-color: #00F260 !important; /* مؤشر أخضر */
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* 4. تلوين النص "شبه المختفي" (Placeholder) */
    textarea[data-testid="stChatInputTextArea"]::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
        -webkit-text-fill-color: rgba(255, 255, 255, 0.7) !important;
    }

    /* 5. إصلاح زر الإرسال (لأنه أصبح شفافاً بسبب الخطوة 2) */
    button[data-testid="stChatInputSubmitButton"] {
        background: transparent !important;
        border: none !important;
    }
    
    /* تلوين أيقونة الزر */
    button[data-testid="stChatInputSubmitButton"] svg {
        fill: #00F260 !important; /* لون أخضر للأيقونة */
        color: #00F260 !important;
    }

    /* تأثير التحويم على الزر */
    button[data-testid="stChatInputSubmitButton"]:hover svg {
        fill: #FFFFFF !important;
        transform: scale(1.1);
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

    st.markdown("<h2 style='text-align: center; color: #00f260; font-family: Orbitron; letter-spacing: 2px; text-shadow: 0 0 15px rgba(0,242,96,0.4);'>M'CHOUNECHE AI</h2>", unsafe_allow_html=True)
    st.caption("Dev: Hassouni Raed | ESTA Student")
    st.markdown("---")
    
    # 🔥🔥🔥 مفتاح تغيير المظهر (تصميم Apple الجديد) 🔥🔥🔥
    st.markdown("### 🌗 المظهر (Theme)")
    # تم إضافة horizontal=True لجعله أفقياً
    theme_selection = st.radio(
        "اختر الوضع:",
        ["🌑 ليلي", "☀️ نهاري"],
        index=0 if st.session_state.theme_mode == "🌑 ليلي" else 1,
        key="theme_toggle_radio",
        horizontal=True,
        label_visibility="collapsed" # إخفاء العنوان الصغير لأنه مكتوب فوق
    )
    if theme_selection != st.session_state.theme_mode:
        st.session_state.theme_mode = theme_selection
        st.rerun()

    st.markdown("---")
    
    mode = st.radio("القائمة:", 
        ["💬 المحادثة الذكية", "💻 استوديو الأكواد", "📊 تحليل البيانات", "⚙️ الإعدادات"],
        index=0
    )
    
    st.markdown("---")

    if st.session_state.db_context:
        st.success("✅ قاعدة البيانات (data.txt): متصلة")
    else:
        st.warning("⚠️ قاعدة البيانات (data.txt): غير موجودة")
    
    st.markdown("---")
    
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
    
    if st.session_state.chat_history:
        chat_str = "\n".join([f"[{m['role'].upper()}]: {m['content']}" for m in st.session_state.chat_history])
        st.download_button("💾 تحميل سجل المحادثة", chat_str, file_name="chat_history.txt", mime="text/plain")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if st.session_state.ai_mode == "🚀 Rapide":
        theme_color = "#ffffff" if st.session_state.theme_mode == "🌑 ليلي" else "#000000"
        btn_icon = "🚀"
        sys_suffix = " أجب بسرعة فائقة واختصار. استخدم النقاط."
    elif st.session_state.ai_mode == "💠 Pro":
        theme_color = "#00f260"
        btn_icon = "💠"
        sys_suffix = " أجب بتفصيل هندسي متوازن ودقيق."
    else:
        theme_color = "#ff2a2a"
        btn_icon = "🧠"
        sys_suffix = " وضع التفكير العميق. حلل كل الجوانب."

    popover_bg = "rgba(20, 20, 30, 0.9)" if st.session_state.theme_mode == "🌑 ليلي" else "rgba(255, 255, 255, 0.9)"
    chat_input_bg = "rgba(255,255,255,0.05)" if st.session_state.theme_mode == "🌑 ليلي" else "rgba(0,0,0,0.05)"
    message_bg = "rgba(255,255,255,0.03)" if st.session_state.theme_mode == "🌑 ليلي" else "rgba(255,255,255,0.6)"

    st.markdown(f"""
    <style>
        div[data-testid="stPopover"] {{
            position: fixed !important; bottom: 40px !important; right: 90px !important;
            z-index: 1000000 !important; display: block !important; width: auto !important;
        }}
        div[data-testid="stPopover"] button {{
            background-color: {popover_bg} !important;
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
        
        /* تعديلات داخل خانة الدردشة */
        textarea[data-testid="stChatInputTextArea"] {{ 
            padding-right: 60px !important; 
            caret-color: {theme_color} !important; 
            color: {input_text_color} !important;
            -webkit-text-fill-color: {input_text_color} !important;
            background: transparent !important;
        }}
        
        button[data-testid="stChatInputSubmitButton"] {{ 
            color: {theme_color} !important; 
            background: {chat_input_bg} !important;
            border-radius: 50% !important; height: 45px !important; width: 45px !important;
            border: 1px solid {theme_color}40 !important;
        }}
        button[data-testid="stChatInputSubmitButton"]:hover {{
            background: {theme_color}20 !important;
            box-shadow: 0 0 15px {theme_color} !important;
        }}
        
        .stChatMessage {{
            background: {message_bg} !important;
            border: 1px solid {border_color} !important;
            border-radius: 16px !important;
            backdrop-filter: blur(10px) !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
            transition: transform 0.2s;
        }}
        .stChatMessage:hover {{ transform: translateY(-2px); }}
        
        div[data-testid="chatAvatarIcon"] {{
            background: rgba(128,128,128,0.1) !important;
            border: 1px solid {theme_color}60 !important;
        }}
        
        @media only screen and (max-width: 600px) {{
             div[data-testid="stPopover"] {{
                bottom: 160px !important;
                right: 20px !important;
                width: 45px !important; height: 45px !important; font-size: 1.2rem !important;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)

    with st.popover(btn_icon, use_container_width=False):
        st.markdown(f"### Current Mode: {st.session_state.ai_mode}")
        st.session_state.ai_mode = st.radio("Select Level:", ["🚀 Rapide", "💠 Pro", "🧠 Pro Max"], index=["🚀 Rapide", "💠 Pro", "🧠 Pro Max"].index(st.session_state.ai_mode))

    programmer_info = " ملاحظة هامة جداً: إذا سألك المستخدم 'من برمجك؟' أو 'من رئيسك؟' أو 'من صنعك؟' يجب أن تجيب حرفياً بهذه الجملة فقط: 'رئيسي هو حسوني رائد، طالب بالمدرسة العليا لتكنولوجيات متقدمة، ومقيم في ميوري ووهران'."
    
    context_instruction = ""
    if st.session_state.db_context:
        context_instruction += f"\n[PERMANENT DATABASE INFO]:\n{st.session_state.db_context}\n(Use this as primary source for M'chouneche info.)"
    if st.session_state.pdf_context:
        context_instruction += f"\n[CURRENT LESSON CONTEXT (PDF)]: \n{st.session_state.pdf_context[:20000]}\n(Use this for academic questions.)"
    
    base_prompt = "أنت مساعد ذكي ومرشد سياحي وتقني لمدينة مشونش، وأيضاً خبير في الأنظمة المدمجة." + programmer_info + context_instruction
    sys_prompt = base_prompt + sys_suffix

    prompt = st.chat_input("اسأل عن مدينة مشونش ...")
    
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        if st.session_state.ai_mode == "🧠 Pro Max":
            st.markdown(f"""<style>.stStatusWidget {{ background: {card_bg} !important; backdrop-filter: blur(10px); border: 1px solid {border_color}; border-radius: 12px; }}</style>""", unsafe_allow_html=True)
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
# بقية الأقسام
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
                st.session_state.generated_code = generated_code
                st.code(generated_code, language=lang.lower().split()[0])
        elif st.session_state.generated_code:
             st.code(st.session_state.generated_code, language=lang.lower().split()[0])
        else:
            st.info("النتيجة ستظهر هنا...")
        
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
    st.markdown(f"""
    <div class="metric-card" style="text-align: left; display: flex; align-items: center; gap: 20px;">
        <div style="font-size: 3rem;">👨‍💻</div>
        <div>
            <h3 style="margin: 0; color: #ffffff !important;">Hassouni Raed</h3>
            <p style="margin: 5px 0 0 0; color: #00f260 !important;">ESTA Student - ACCESS GRANTED</p>
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
            st.session_state.db_context = load_local_database()
            st.rerun()
