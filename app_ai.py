import os
import streamlit as st
import requests

# 1. CẤU HÌNH TRANG VÀ CSS CAO CẤP
st.set_page_config(page_title="Premier Fencing & Pavers", page_icon="🌿", layout="wide")

custom_theme = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');

/* 1. NỀN TỔNG THỂ: Gradient giao thoa giữa Đá Xám lạnh (Slate) và Gỗ Nâu ấm (Walnut) */
.stApp { 
    background: linear-gradient(135deg, #29323C 0%, #4E342E 100%) !important; 
    font-family: 'Plus Jakarta Sans', sans-serif; 
}

/* 2. KHUNG CANVAS TRUNG TÂM: Bề mặt vân đá xám đen, bọc viền gỗ */
[data-testid="block-container"] {
    background: linear-gradient(145deg, #2D3134 0%, #1F2224 100%) !important;
    border-radius: 16px;
    padding: 40px 50px !important;
    margin-top: 30px;
    margin-bottom: 30px;
    box-shadow: 0 20px 50px rgba(0,0,0, 0.6) !important;
    border: 2px solid #5D4037 !important; /* Viền màu Nâu Gỗ */
}

/* 3. ÉP BUỘC 100% CHỮ NỘI DUNG THÀNH MÀU TRẮNG - Khắc phục triệt để lỗi tàng hình */
.stMarkdown p, .stMarkdown span, .stMarkdown li, .stMarkdown div, 
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] {
    color: #FFFFFF !important;
    font-weight: 300 !important;
    line-height: 1.7 !important;
    font-size: 1.05rem !important;
}

/* 4. TIÊU ĐỀ: Màu Gỗ Sồi Sáng (Light Oak) để bắt sáng trên nền đá đen */
h1, h2, h3, h1 *, h2 *, h3 * { 
    font-family: 'Playfair Display', serif !important; 
    color: #E6C287 !important; 
    letter-spacing: 0.5px !important;
}

/* Sidebar: Màu gỗ tối nguyên bản */
[data-testid="stSidebar"] { 
    background: #2C1E16 !important; 
    border-right: 1px solid #4A3525 !important;
}
[data-testid="stSidebar"] * { color: #E8EDE9 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #E6C287 !important; }

/* Khung ảnh: Viền nâu gỗ mỏng, bo viền sáng khi di chuột vào */
img { 
    border-radius: 10px !important; 
    border: 2px solid #5D4037 !important; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important; 
    transition: all 0.4s ease !important; 
}
img:hover { 
    transform: translateY(-5px) scale(1.02); 
    box-shadow: 0 15px 40px rgba(0,0,0,0.7) !important; 
    border-color: #E6C287 !important;
}

/* Nút bấm (Button): Gradient màu Gỗ Sồi, chữ trắng */
div.stButton > button {
    background: linear-gradient(90deg, #8B5A2B 0%, #5C4033 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    box-shadow: 0 4px 15px rgba(139, 90, 43, 0.3) !important;
    transition: all 0.3s ease !important;
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(139, 90, 43, 0.5) !important;
}

/* Bảng giá: Nền kính mờ viền gỗ */
table { 
    background: rgba(255,255,255,0.03) !important; 
    border-radius: 10px; 
    border: 1px solid #5D4037 !important; 
    width: 100%; 
}
th { 
    background: rgba(139, 90, 43, 0.2) !important; 
    color: #E6C287 !important; 
    font-family: 'Playfair Display', serif !important; 
    font-size: 1.1rem; 
    border-bottom: 1px solid #5D4037 !important;
}
td { 
    color: #FFFFFF !important; 
    border-bottom: 1px solid #3E2723 !important;
}

/* Hộp thông tin 4 bước (Quy trình) */
div[data-testid="stAlert"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid #5D4037 !important;
}
div[data-testid="stAlert"] div[data-testid="stMarkdownContainer"] p {
    color: #FFFFFF !important;
}
</style>
"""
st.markdown(custom_theme, unsafe_allow_html=True)


# ĐỊNH VỊ ĐƯỜNG DẪN ẢNH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FENCES_DIR = os.path.join(BASE_DIR, "kho_anh", "fences")
PAVERS_DIR = os.path.join(BASE_DIR, "kho_anh", "pavers")

# ==========================================
# 2. THANH MENU BÊN TRÁI
# ==========================================
st.sidebar.title("⚜️ Navigation")
menu = st.sidebar.radio(
    "",
    [
        "📜 About & Pricing",     # 👉 Đã được đưa lên dòng số 1 (Mặc định hiển thị)
        "🖼️ Projects Gallery",    # 👉 Đẩy xuống dòng số 2
        "✉️ Free Estimate & AI"
    ]
)
st.sidebar.markdown("---")
st.sidebar.write("📞 **(123) 456-7890**\n\n📫 **info@premieroutdoor.com**\n\n📍 **Seattle, WA**")
# ==========================================
# TRANG 1: THƯ VIỆN HÌNH ẢNH
# ==========================================
if menu == "🖼️ Projects Gallery":
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if os.path.exists(os.path.join(BASE_DIR, "logo.png")):
            st.image(os.path.join(BASE_DIR, "logo.png"), width=240)

    st.title("Transforming Backyards with Precision 🌿")
    st.write("✨ *Browse through our premium fencing and hardscaping projects.*")

    tab_fences, tab_pavers = st.tabs(["🪵 Premium Fences", "🧱 Luxury Pavers"])

    with tab_fences:
        if os.path.exists(FENCES_DIR) and len(os.listdir(FENCES_DIR)) > 0:
            fence_images = [f for f in os.listdir(FENCES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            cols = st.columns(2)
            for idx, img_name in enumerate(fence_images):
                with cols[idx % 2]:
                    st.image(os.path.join(FENCES_DIR, img_name), use_container_width=True)

    with tab_pavers:
        if os.path.exists(PAVERS_DIR) and len(os.listdir(PAVERS_DIR)) > 0:
            paver_images = [f for f in os.listdir(PAVERS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            cols = st.columns(2)
            for idx, img_name in enumerate(paver_images):
                with cols[idx % 2]:
                    st.image(os.path.join(PAVERS_DIR, img_name), use_container_width=True)

# ==========================================
# TRANG 2: GIỚI THIỆU & BẢNG GIÁ
# ==========================================
elif menu == "📜 About & Pricing":
    bg_img = os.path.join(BASE_DIR, "bg_about.jpg")
    if os.path.exists(bg_img):
        st.image(bg_img, use_container_width=True)

    st.title("More Than Just Contractors 🏛️")
    st.markdown("""
    🏡 **A structurally sound fence** doesn't just mark a boundary; it frames your family's memories and keeps your loved ones safe.  
    ☕ **A perfectly leveled paver patio** isn't just concrete; it's the foundation for your weekend barbecues and slow mornings.

    We are locally owned and operated, which means we treat every property as if it were our neighbor's. When you hire us, you aren't just getting a construction crew. You get:
    * 💎 **Uncompromising Quality**
    * 📐 **Master Craftsmanship** 
    * 🤝 **Radical Transparency**
    """)

    st.divider()

    st.header("⚙️ Our 4-Step Process")
    b1, b2, b3, b4 = st.columns(4)
    b1.success("📍 **01. Site Evaluation**\n\nPrecise on-site survey & layout consultation.")
    b2.info("📑 **02. Firm Estimate**\n\nClear material & labor pricing with no hidden fees.")
    b3.warning("🏗️ **03. Installation**\n\nBuilt to code using structural-grade materials.")
    b4.error("🏆 **04. Final Walkthrough**\n\nQuality check and warranty handover.")

    st.divider()

    st.header("💼 2026 Average Market Estimates")
    st.markdown("*Reference guide only. Custom site factors, terrain, and soil grading determine final proposals.*")
    
    pricing_table = """
    | Project Type | Est. Cost | Duration | Warranty |
    | :--- | :--- | :--- | :--- |
    | 🪵 **Wood Privacy Fence** | $15 – $45 / ft. | 2 – 4 Days | 1 Year |
    | 🛡️ **Premium Vinyl Fence** | $20 – $50 / ft. | 2 – 3 Days | 5 Years |
    | 🧱 **Concrete Pavers** | $10 – $25 / sq.ft. | 3 – 6 Days | 3 Years |
    """
    st.markdown(pricing_table)

# ==========================================
# TRANG 3: FORM LIÊN HỆ & CHATBOT
# ==========================================
elif menu == "✉️ Free Estimate & AI":
    st.title("Ready for a Free On-Site Estimate? 🤝")
    st.write("Fill out the form below or chat with our Virtual Assistant for instant answers.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📝 Request a Quote")
        with st.form("contact_form", clear_on_submit=True):
            name = st.text_input("👤 Full Name *", placeholder="John Doe")
            phone = st.text_input("📞 Phone Number *", placeholder="(123) 456-7890")
            project_type = st.selectbox("🏗️ Project Interest", ["Wood Fencing", "Vinyl Fencing", "Pavers", "Other"])
            message = st.text_area("💬 Project Details", placeholder="Tell us about your yard...")
            submitted = st.form_submit_button("Submit Request 🚀")

            if submitted:
                if not name or not phone:
                    st.error("⚠️ Please fill in your Name and Phone Number.")
                else:
                    st.success("✅ Thank you! Your request has been sent successfully.")

    with col2:
        st.header("🤖 AI Assistant")
        st.info("Have questions about permits or materials? Ask our AI!")
        
        user_msg = st.chat_input("Type your question here...")
        if user_msg:
            st.chat_message("user").write(user_msg)
            st.chat_message("assistant").write("This is a placeholder for AI. Add your GenAI logic here.")