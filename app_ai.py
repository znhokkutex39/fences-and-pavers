import streamlit as st
import os
import requests
from google import genai
from google.genai import types
from google.genai import errors

# ================= 1. CÀI ĐẶT TRANG =================
st.set_page_config(page_title="Premier Landscaping & Fencing", page_icon="🌿", layout="wide")

# ================= HÀM HỖ TRỢ CHUNG =================

def gui_thong_tin_ve_sheets(name, email, phone, note=""):
    APPS_SCRIPT_WEBHOOK = st.secrets["SHEETS_WEBHOOK"]
    
    du_lieu = {
        "name": name,
        "email": email,
        "phone": phone,
        "note": note
    }
    
    try:
        # Bổ sung lệnh allow_redirects=True để chạy theo cơ chế bảo mật của Google
        response = requests.post(APPS_SCRIPT_WEBHOOK, json=du_lieu, allow_redirects=True)
        
        if response.status_code == 200:
            return True
        else:
            # IN THẲNG MÃ LỖI VÀ LÝ DO RA MÀN HÌNH WEB
            st.error(f"⚠️ Google từ chối nhận! Mã lỗi: {response.status_code}")
            st.info(f"Chi tiết từ Google: {response.text}")
            return False
    except Exception as e:
        st.error(f"⚠️ Lỗi mạng (Cấu hình st.secrets sai): {e}")
        return False

# 2. HÀM GỬI SLACK
def gui_thong_bao_slack(name, email, phone, note=""):
    try:
        SLACK_WEBHOOK_URL = st.secrets["SLACK_WEBHOOK"]
        tin_nhan = f"🚨 *CÓ KHÁCH HÀNG MỚI!* 🚨\n👤 *Tên:* {name}\n📧 *Email:* {email}\n📞 *Phone:* {phone}\n📝 *Ghi chú:* {note}"
        
        response = requests.post(SLACK_WEBHOOK_URL, json={"text": tin_nhan})
        
        # Ép hệ thống in ra lỗi nếu Slack từ chối
        if response.status_code != 200:
            st.error(f"⚠️ Lỗi Slack từ chối nhận: {response.status_code} - {response.text}")
            
    except Exception as e:
        st.error(f"⚠️ Lỗi cấu hình Slack: {e}")
def hien_thi_anh_tu_thu_muc(ten_thu_muc):
    if not os.path.exists(ten_thu_muc):
        st.warning(f"⚠️ Chưa tìm thấy thư mục: {ten_thu_muc}")
        return

    danh_sach_file = os.listdir(ten_thu_muc)
    danh_sach_anh = [f for f in danh_sach_file if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if len(danh_sach_anh) == 0:
        st.info("Chưa có hình ảnh nào trong thư mục này.")
        return

    cot1, cot2, cot3 = st.columns(3)
    for chi_muc, ten_file in enumerate(danh_sach_anh):
        duong_dan_anh = os.path.join(ten_thu_muc, ten_file)
        
        chu_thich = ten_file.replace(".jpg", "").replace(".jpeg", "").replace(".png", "").replace("_", " ").capitalize()
        ma_so_anh = ten_file.split('.')[0].upper()
        chu_thich_hoan_chinh = f"✨ {chu_thich} | ID: {ma_so_anh}"
        
        if chi_muc % 3 == 0:
            with cot1: st.image(duong_dan_anh, caption=chu_thich_hoan_chinh, use_container_width=True)
        elif chi_muc % 3 == 1:
            with cot2: st.image(duong_dan_anh, caption=chu_thich_hoan_chinh, use_container_width=True)
        else:
            with cot3: st.image(duong_dan_anh, caption=chu_thich_hoan_chinh, use_container_width=True)

# ================= 2. THANH MENU BÊN TRÁI (SIDEBAR) =================
with st.sidebar:
    st.markdown("## 📞 Contact Us")
    st.write("📍 Serving the Greater US Area")
    st.write("☎️ 1-800-555-0199")
    st.markdown("---")
    
    st.markdown("### Get a Free Quote")
    with st.form("quote_form_sidebar"):
        customer_name = st.text_input("Your Name (Required):", placeholder="John Doe")
        customer_email = st.text_input("Your Email (Required):", placeholder="example@gmail.com")
        customer_phone = st.text_input("Your Phone (Optional):", placeholder="(555) 123-4567")
        customer_note = st.text_area("Interested Design ID & Comments:", placeholder="Example: I like ID: WOOD_FENCE_1...")
        
        if st.form_submit_button("Submit Request", use_container_width=True):
            if customer_name and customer_email:
                
                # Gọi đồng thời 2 hệ thống: Slack và Google Sheets
                gui_thong_bao_slack(customer_name, customer_email, customer_phone, customer_note)
                
                if gui_thong_tin_ve_sheets(customer_name, customer_email, customer_phone, customer_note):
                    st.success(f"✅ Thank you {customer_name}! Our team will contact you shortly.")
                else:
                    st.error("⚠️ Connection error. Please try again.")
            else:
                st.error("⚠️ Please enter both your Name and Email.")

# ================= 3. KHU VỰC TRƯNG BÀY (PORTFOLIO) =================
st.title("🌿 Premier Landscaping & Fencing Solutions")
st.markdown("Explore our recent projects below. Note the **Design ID** if you find a style you love!")
st.markdown("---")

st.markdown("### 📸 Our Project Gallery")

thu_muc_hien_tai = os.path.dirname(os.path.abspath(__file__))
duong_dan_fences = os.path.join(thu_muc_hien_tai, "kho_anh", "fences")
duong_dan_pavers = os.path.join(thu_muc_hien_tai, "kho_anh", "pavers")

tab_fences, tab_pavers = st.tabs(["🏡 Fencing Projects", "🪨 Pavers & Patios"])

with tab_fences:
    st.write("**High-quality fencing solutions for privacy and style.**")
    hien_thi_anh_tu_thu_muc(duong_dan_fences) 

with tab_pavers:
    st.write("**Custom stone patios, walkways, and hardscaping.**")
    hien_thi_anh_tu_thu_muc(duong_dan_pavers) 

st.markdown("---")

# ================= 4. KHUNG CHAT AI TƯ VẤN THÔNG MINH =================
st.markdown("### 🤖 Ask Our AI Consultant")

if "so_luot_chat" not in st.session_state:
    st.session_state.so_luot_chat = 0

if "bo_nho_chat" not in st.session_state:
    try:
        # Lấy API Key từ hệ thống bảo mật st.secrets
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        lenh_cho_ai = """
        You are a professional Landscaping & Fencing Consultant in the United States.
        Always reply in ENGLISH. Keep responses short, friendly, and helpful.
        Ask 1 clarifying question before suggesting solutions.
        If the customer wants a quote, tell them to fill out the form on the left sidebar.
        """
        st.session_state.bo_nho_chat = client.chats.create(
            model='gemini-3.5-flash',
            config=types.GenerateContentConfig(system_instruction=lenh_cho_ai)
        )
        st.session_state.tin_nhan_hien_thi = [
            {"role": "assistant", "content": "Hi there! I can help you choose the right materials or answer any landscaping questions. What are you looking to build?"}
        ]
    except Exception:
        st.error("Lỗi khởi tạo AI. Vui lòng kiểm tra API Key.")

if "tin_nhan_hien_thi" in st.session_state:
    for tin_nhan in st.session_state.tin_nhan_hien_thi:
        with st.chat_message(tin_nhan["role"]):
            st.markdown(tin_nhan["content"])

GIỚI_HẠN_CHAT = 5

if st.session_state.so_luot_chat >= GIỚI_HẠN_CHAT:
    st.warning("⚠️ You've reached the limit of our free AI consultation. Please fill out the form on the left sidebar for further assistance.")
else:
    cau_hoi_cua_khach = st.chat_input(f"Type your question ({GIỚI_HẠN_CHAT - st.session_state.so_luot_chat} messages left)...")

    if cau_hoi_cua_khach:
        with st.chat_message("user"):
            st.markdown(cau_hoi_cua_khach)
        st.session_state.tin_nhan_hien_thi.append({"role": "user", "content": cau_hoi_cua_khach})
        st.session_state.so_luot_chat += 1
        st.rerun()

if "tin_nhan_hien_thi" in st.session_state and len(st.session_state.tin_nhan_hien_thi) > 0:
    tin_nhan_cuoi = st.session_state.tin_nhan_hien_thi[-1]
    
    if tin_nhan_cuoi["role"] == "user":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    ket_qua = st.session_state.bo_nho_chat.send_message(tin_nhan_cuoi["content"])
                    st.markdown(ket_qua.text)
                    st.session_state.tin_nhan_hien_thi.append({"role": "assistant", "content": ket_qua.text})
                except errors.ServerError:
                    st.warning("⚠️ Our consultant is currently assisting other clients. Please wait a few seconds and try again!")
                    st.session_state.so_luot_chat -= 1 
                    st.session_state.tin_nhan_hien_thi.pop()
                except Exception:
                    st.error("Connection error. Please try again.")
                    st.session_state.so_luot_chat -= 1
                    st.session_state.tin_nhan_hien_thi.pop()