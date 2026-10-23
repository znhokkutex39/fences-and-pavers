"""
Premier Fencing & Pavers - Mobile & Desktop Luxury Edition
"""
from __future__ import annotations

import csv
import html
import inspect
import os
import re
import threading
import time
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import streamlit as st

# set_page_config phải là lệnh Streamlit đầu tiên
st.set_page_config(
    page_title="Premier Fencing & Pavers",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

esc = html.escape

# =============================================================================
# 1. CẤU HÌNH & DỮ LIỆU ĐƯỜNG DẪN
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
FENCES_DIR = BASE_DIR / "kho_anh" / "fences"
PAVERS_DIR = BASE_DIR / "kho_anh" / "pavers"
LEADS_FILE = BASE_DIR / "leads.csv"
VISITOR_FILE = BASE_DIR / "visitors.txt"

BUSINESS = {
    "name": "Premier Fencing & Pavers",
    "phone": "(123) 456-7890",
    "email": "info@premieroutdoor.com",
    "city": "Seattle, WA",
}

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
GALLERY_COLUMNS = 3
GALLERY_PAGE_SIZE = 9

PRICING = [
    {"key": "wood", "icon": "🪵", "name": "Wood Privacy Fence", "form": "Wood Fencing",
     "low": 15.50, "high": 45.99, "unit": "ft.", "unit_long": "linear feet",
     "days": "2 – 4 Days", "warranty": "1 Year", "keywords": ("wood", "cedar", "privacy", "timber")},
    {"key": "vinyl", "icon": "🛡️", "name": "Premium Vinyl Fence", "form": "Vinyl Fencing",
     "low": 20.75, "high": 50.50, "unit": "ft.", "unit_long": "linear feet",
     "days": "2 – 3 Days", "warranty": "5 Years", "keywords": ("vinyl", "pvc", "white fence")},
    {"key": "pavers", "icon": "🧱", "name": "Concrete Pavers", "form": "Pavers",
     "low": 10.25, "high": 25.80, "unit": "sq.ft.", "unit_long": "square feet",
     "days": "3 – 6 Days", "warranty": "3 Years", "keywords": ("paver", "patio", "driveway", "walkway", "stone", "brick")},
]
PRICING_BY_KEY = {p["key"]: p for p in PRICING}
PROJECT_OPTIONS = ["Wood Fencing", "Vinyl Fencing", "Pavers", "Other"]

GREETING = (
    f"Hi! I'm the virtual assistant for {BUSINESS['name']}. "
    "Click a topic below for an instant answer, or type your own question!"
)
QUICK_QUESTIONS = [
    "💰 How much does a project cost?",
    "📋 Do I need a permit or HOA approval?",
    "⏱️ How long does installation take?",
    "🛡️ What warranty do you offer?",
    "🌲 What materials do you use?",
]

LEAD_FIELDS = ["timestamp", "name", "phone", "email", "project", "message"]
SPAM_KEYWORDS = (
    "http://", "https://", "www.", "seo", "backlink", "crypto", "bitcoin",
    "casino", "viagra", "marketing agency", "web design", "rank your", "telegram"
)
FAKE_PHONES = {"1234567890", "0123456789", "0000000000", "1111111111", "9999999999"}
DISPOSABLE_EMAILS = ("tempmail.", "mailinator.", "guerrillamail.", "10minutemail.", "yopmail.")

# =============================================================================
# 2. GIAO DIỆN (CSS) - TỐI ƯU CẢ ĐIỆN THOẠI LẪN MÁY TÍNH
# =============================================================================
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

:root{
  --slate:#29323C; --stone-a:#2D3134; --stone-b:#1F2224; --walnut:#4E342E;
  --wood:#5D4037; --oak:#8B5A2B; --oak-dark:#5C4033; --gold:#E6C287;
  --muted:rgba(255,255,255,.72); --glass:rgba(255,255,255,.04);
}

.stApp{background:linear-gradient(135deg,var(--slate) 0%,var(--walnut) 100%) fixed !important;font-family:'Plus Jakarta Sans',system-ui,sans-serif;}
header[data-testid="stHeader"]{background:transparent !important;}
#MainMenu,footer{visibility:hidden;}

/* Làm nổi bật nút mở Sidebar trên điện thoại */
[data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] button{
  background-color:#2C1E16 !important;
  border:1px solid var(--gold) !important;
  color:var(--gold) !important;
  border-radius:8px !important;
}
[data-testid="collapsedControl"] svg, [data-testid="stSidebarCollapsedControl"] svg{
  fill:var(--gold) !important;
  color:var(--gold) !important;
}

[data-testid="stMainBlockContainer"],[data-testid="stAppViewBlockContainer"],[data-testid="block-container"]{
  max-width:1240px !important; margin:36px auto 28px !important; padding:32px 44px !important;
  background:linear-gradient(145deg,var(--stone-a) 0%,var(--stone-b) 100%) !important;
  border:2px solid var(--wood) !important; border-radius:16px; box-shadow:0 20px 50px rgba(0,0,0,.6) !important;
}
@media (max-width:768px){
  [data-testid="stMainBlockContainer"],[data-testid="stAppViewBlockContainer"],[data-testid="block-container"]{
    padding:18px 14px !important; margin:10px auto !important; border-radius:12px;
  }
}

[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] li{
  color:#fff !important; font-weight:300 !important; line-height:1.7 !important; font-size:1.05rem !important; max-width:72ch;
}
[data-testid="stMarkdownContainer"] strong{font-weight:600 !important;}
[data-testid="stWidgetLabel"] p{color:#fff !important;font-weight:500 !important;font-size:.95rem !important;}
a,a:visited{color:var(--gold) !important;text-decoration:none;}

h1,h2,h3,h1 *,h2 *,h3 *{font-family:'Playfair Display',Georgia,serif !important;color:var(--gold) !important;letter-spacing:.5px !important;}
hr{border-color:var(--wood) !important;}

/* Sidebar */
[data-testid="stSidebar"]{background:#2C1E16 !important;border-right:1px solid #4A3525 !important;}
[data-testid="stSidebar"] *{color:#E8EDE9 !important;}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] a{color:var(--gold) !important;}

/* Khung ảnh */
[data-testid="stImage"] img{border-radius:10px !important;border:2px solid var(--wood) !important;box-shadow:0 10px 30px rgba(0,0,0,.5) !important;transition:all .35s ease !important;}
[data-testid="stImage"] img:hover{transform:scale(1.02);box-shadow:0 15px 40px rgba(0,0,0,.7) !important;border-color:var(--gold) !important;}
[data-testid="stSidebar"] [data-testid="stImage"] img{border:none !important;box-shadow:none !important;}
[data-testid="stSidebar"] [data-testid="stImage"] img:hover{transform:none;}

/* Nút bấm chính */
div.stButton button,[data-testid="stFormSubmitButton"] button{
  background:linear-gradient(90deg,var(--oak) 0%,var(--oak-dark) 100%) !important;color:#fff !important;border:none !important;
  border-radius:6px !important;padding:.6rem 1.4rem !important;text-transform:uppercase !important;letter-spacing:1px !important;
  box-shadow:0 4px 15px rgba(139,90,43,.3) !important;transition:all .25s ease !important;
}
div.stButton button:hover,[data-testid="stFormSubmitButton"] button:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(139,90,43,.5) !important;}

/* Nút câu hỏi gợi ý của Chatbot */
div[class*="st-key-quick_"],div[class*="st-key-quick_"] div.stButton{width:100% !important;}
div[class*="st-key-quick_"] div.stButton button{background:var(--glass) !important;border:1px solid var(--wood) !important;box-shadow:none !important;text-transform:none !important;letter-spacing:0 !important;justify-content:flex-start !important;width:100%;padding:.45rem 1rem !important;}
div[class*="st-key-quick_"] div.stButton button:hover{border-color:var(--gold) !important;box-shadow:none !important;transform:none;}
div[class*="st-key-quick_"] div.stButton button p{font-weight:400 !important;font-size:.9rem !important;text-align:left;}

/* Thanh liên hệ nhanh trên đỉnh trang (Rất tiện cho điện thoại) */
.top-bar{
  display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;
  background:rgba(44, 30, 22, 0.85); border:1px solid var(--wood); border-radius:10px;
  padding:10px 16px; margin-bottom:14px; font-size:0.9rem;
}
.top-bar .brand{font-family:'Playfair Display',serif; color:var(--gold); font-weight:700; font-size:1.1rem;}
.top-bar .call-btn{
  background:rgba(230, 194, 135, 0.15); border:1px solid var(--gold); color:var(--gold) !important;
  padding:4px 12px; border-radius:6px; font-weight:600; font-size:0.85rem;
}

.table-wrap{overflow-x:auto;border:1px solid var(--wood);border-radius:12px;background:var(--glass);}
.price-table{width:100%;min-width:520px;margin:0 !important;border:none !important;border-collapse:collapse;}
.price-table th,.price-table td{border:none !important;text-align:left;padding:.85rem 1rem !important;}
.price-table th{background:rgba(139,90,43,.22) !important;color:var(--gold) !important;font-family:'Playfair Display',serif;font-size:1.05rem;border-bottom:1px solid var(--wood) !important;}
.price-table td{background:transparent !important;color:#fff !important;font-weight:300;border-bottom:1px solid #3E2723 !important;}

.est{border-left:3px solid var(--gold);background:var(--glass);padding:16px 22px;margin:.6rem 0 1rem;border-radius:0 10px 10px 0;}
.est .range{font-family:'Playfair Display',serif;color:var(--gold);font-size:clamp(1.8rem,4vw,2.5rem);font-weight:600;}
"""

# =============================================================================
# 3. TIỆN ÍCH CHUNG & ĐẾM LƯỢT TRUY CẬP
# =============================================================================
def html_block(markup: str) -> str:
    return " ".join(line.strip() for line in markup.splitlines() if line.strip())

def render_html(markup: str) -> None:
    st.markdown(html_block(markup), unsafe_allow_html=True)

def md_safe(text: str) -> str:
    return text.replace("$", r"\$")

@lru_cache(maxsize=1)
def _stretch_kwargs() -> dict:
    try:
        if isinstance(inspect.signature(st.image).parameters["width"].default, str):
            return {"width": "stretch"}
    except Exception:
        pass
    return {"use_container_width": True}

def show_image(path, *, width: int | None = None, caption: str | None = None) -> None:
    kwargs = {"caption": caption, **({"width": width} if width else _stretch_kwargs())}
    try:
        st.image(str(path), **kwargs)
    except Exception:
        st.image(str(path), caption=caption)

def _natural_key(name: str) -> list:
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]

@st.cache_data(ttl=60, show_spinner=False)
def list_images(folder: str) -> list[str]:
    p = Path(folder)
    if not p.is_dir():
        return []
    files = [f for f in p.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTS]
    return [str(f) for f in sorted(files, key=lambda f: _natural_key(f.name))]

def go_to(page: str, project: str | None = None) -> None:
    st.session_state["page"] = page

def track_visitor() -> int:
    try:
        count = int(VISITOR_FILE.read_text(encoding="utf-8").strip()) if VISITOR_FILE.is_file() else 120
    except ValueError:
        count = 120

    if not st.session_state.get("visited_logged", False):
        count += 1
        st.session_state["visited_logged"] = True
        try:
            VISITOR_FILE.write_text(str(count), encoding="utf-8")
        except OSError:
            pass
    return count

# =============================================================================
# 4. BẢO MẬT CHỐNG SPAM & LƯU KHÁCH HÀNG THẬT
# =============================================================================
@st.cache_resource
def _lead_lock() -> threading.Lock:
    return threading.Lock()

def _csv_safe(value: str) -> str:
    value = str(value)
    return "'" + value if value[:1] in ("=", "+", "-", "@", "\t", "\r") else value

def save_lead_to_csv(lead: dict) -> bool:
    try:
        with _lead_lock():
            is_new = not LEADS_FILE.exists()
            with LEADS_FILE.open("a", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=LEAD_FIELDS)
                if is_new:
                    writer.writeheader()
                writer.writerow({k: lead[k] if k == "phone" else _csv_safe(lead[k]) for k in LEAD_FIELDS})
        return True
    except OSError:
        return False

def check_lead_security(name: str, phone: str, email: str, message: str, honeypot: str, elapsed_sec: float) -> tuple[str, str]:
    if honeypot.strip() != "" or elapsed_sec < 3.0:
        return "spam", ""

    combined_text = f"{name} {message}".lower()
    if any(kw in combined_text for kw in SPAM_KEYWORDS):
        return "spam", ""

    if email and any(domain in email.lower() for domain in DISPOSABLE_EMAILS):
        return "spam", ""

    if len(name.strip()) < 2:
        return "error", "Please enter your full name."

    digits = re.sub(r"\D", "", phone)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]

    if len(digits) != 10:
        return "error", "Please enter a valid 10-digit US phone number (e.g., 206-555-0199)."

    if digits[0] in ("0", "1") or digits in FAKE_PHONES or len(set(digits)) == 1:
        return "error", "That phone number doesn't look right. Please check again."

    return "valid", ""

# =============================================================================
# 5. HỆ THỐNG TRẢ LỜI TỰ ĐỘNG (SMART FAQ - TIẾT KIỆM TOKEN)
# =============================================================================
def faq_answer(text: str) -> str:
    t = text.lower()
    items = [p for p in PRICING if any(k in t for k in p["keywords"])] or PRICING

    def bullets(fmt) -> str:
        return "\n".join(f"- {fmt(p)}" for p in items)

    if any(w in t for w in ("permit", "hoa", "regulation", "setback", "legal", "code", "neighbor")):
        return (
            "📋 **Permits & HOA Guidelines:**\n"
            "Permit and HOA rules depend on your city, lot lines, and fence height (typically fences under 6ft require no building permit, but rules vary). "
            "We review all local requirements and provide HOA-ready documentation during your **free on-site estimate**."
        )

    if any(w in t for w in ("warrant", "guarantee", "repair", "broken")):
        return (
            "🛡️ **Our Workmanship & Material Warranties:**\n"
            + bullets(lambda p: f"**{p['name']}**: {p['warranty']} full warranty")
            + "\n\nWe stand behind every post and paver we install!"
        )

    if any(w in t for w in ("how long", "duration", "timeline", "days", "time", "start", "schedule")):
        return (
            "⏱️ **Typical Installation Timelines:**\n"
            + bullets(lambda p: f"**{p['name']}**: {p['days']}")
            + "\n\n*Note: Exact timing depends on project size, demolition needs, terrain, and Seattle weather.*"
        )

    if any(w in t for w in ("price", "cost", "how much", "estimate", "quote", "afford", "$", "rate")):
        return (
            "💰 **2026 Average Market Estimates:**\n"
            + bullets(lambda p: f"**{p['name']}**: ${p['low']:.2f} – ${p['high']:.2f} per {p['unit']}")
            + "\n\nThese are baseline ranges. Fill out the form on the left for a **100% free on-site measurement and firm quote**!"
        )

    if any(w in t for w in ("material", "wood", "cedar", "vinyl", "paver", "concrete", "quality", "post", "rot")):
        return (
            "🌲 **Premium Structural Materials:**\n"
            "- **Wood Fences:** Pacific Northwest Western Red Cedar with deep concrete-set posts.\n"
            "- **Vinyl Fences:** Heavy-gauge, UV-stabilized commercial grade PVC (never needs painting).\n"
            "- **Pavers:** High-density interlocking concrete pavers over a compacted crushed-rock base."
        )

    return (
        "Thank you for reaching out! Are you planning a **wood fence**, **vinyl fence**, or **paver patio**?\n\n"
        f"For custom requests or an exact quote, please fill out the **Request a Quote** form on this page or call us directly at **{BUSINESS['phone']}**."
    )

def init_chat() -> None:
    if "chat" not in st.session_state:
        st.session_state["chat"] = [{"role": "assistant", "content": GREETING}]

def queue_question(text: str) -> None:
    init_chat()
    st.session_state["chat"].append({"role": "user", "content": text})

def chat_panel() -> None:
    st.header("🤖 AI Assistant")
    st.caption("Instant answers on pricing, permits, materials & timelines.")
    init_chat()

    for i, question in enumerate(QUICK_QUESTIONS):
        st.button(question, key=f"quick_{i}", on_click=queue_question, args=(question,))

    box = st.container(height=360, border=True)
    prompt = st.chat_input("Or type your own question here...", max_chars=500)
    if prompt:
        queue_question(prompt)

    chat = st.session_state["chat"]
    with box:
        for m in chat:
            with st.chat_message(m["role"], avatar="🌿" if m["role"] == "assistant" else None):
                st.markdown(md_safe(m["content"]))
        if chat[-1]["role"] == "user":
            with st.chat_message("assistant", avatar="🌿"):
                with st.spinner("Checking details..."):
                    time.sleep(0.4)
                    reply = faq_answer(chat[-1]["content"])
                st.markdown(md_safe(reply))
            chat.append({"role": "assistant", "content": reply})

# =============================================================================
# 6. CÁC TRANG CHÍNH
# =============================================================================
def estimator() -> None:
    st.subheader("🧮 Interactive Cost Estimator")
    st.markdown("Use our dynamic calculator to get an instant baseline estimate for your project.")
    
    left, right = st.columns(2)
    key = left.selectbox(
        "Project type", list(PRICING_BY_KEY), key="calc_type",
        format_func=lambda k: f"{PRICING_BY_KEY[k]['icon']} {PRICING_BY_KEY[k]['name']}",
    )
    p = PRICING_BY_KEY[key]
    qty = right.number_input(f"Size ({p['unit_long']})", min_value=1, max_value=100_000, value=153, step=1, key="calc_qty")
    
    render_html(f"""
        <div class="est">
          <div class="range">${p['low'] * qty:,.2f} – ${p['high'] * qty:,.2f}</div>
          <div class="meta">Rough range for {qty:,} {esc(p['unit_long'])} of {esc(p['name'])}. Reference only, not a quote.</div>
        </div>
    """)
    st.button("Request a quote for this project", key="cta_calc", on_click=go_to, args=("quote",))

def page_about() -> None:
    st.title("More Than Just Contractors 🏛️")
    st.write(f"Locally owned and operated specialists in {BUSINESS['city']}.")
    st.markdown("""
        🏡 **A structurally sound fence** doesn't just mark a boundary; it frames your family's memories.
        ☕ **A perfectly leveled paver patio** isn't just concrete; it's the foundation for your weekends.
    """)
    st.divider()
    
    st.header("💼 2026 Average Market Estimates")
    rows = "".join(
        f'<tr><td>{p["icon"]} <strong>{esc(p["name"])}</strong></td>'
        f'<td>${p["low"]:.2f} – ${p["high"]:.2f} / {esc(p["unit"])}</td><td>{esc(p["days"])}</td><td>{esc(p["warranty"])}</td></tr>'
        for p in PRICING
    )
    render_html(
        '<div class="table-wrap"><table class="price-table"><thead><tr><th>Project Type</th><th>Est. Cost</th>'
        f"<th>Duration</th><th>Warranty</th></tr></thead><tbody>{rows}</tbody></table></div>"
    )
    estimator()

def render_gallery(folder: Path, key: str) -> None:
    files = list_images(str(folder))
    if not files:
        render_html(f'<div style="border:1px dashed #5D4037; border-radius:10px; padding:2rem; text-align:center; color:#A0A0A0;">No photos found in {folder.name} folder.</div>')
        return

    count_key = f"gallery_{key}_count"
    shown = st.session_state.setdefault(count_key, GALLERY_PAGE_SIZE)
    columns = st.columns(GALLERY_COLUMNS)
    for i, path in enumerate(files[:shown]):
        with columns[i % GALLERY_COLUMNS]:
            show_image(path)

    if shown < len(files):
        def show_more() -> None:
            st.session_state[count_key] += GALLERY_PAGE_SIZE
        st.button("Show more photos", key=f"gallery_{key}_more", on_click=show_more)

def page_gallery() -> None:
    st.title("Transforming Backyards with Precision 🌿")
    tab_fences, tab_pavers = st.tabs(["🪵 Premium Fences", "🧱 Luxury Pavers"])
    with tab_fences:
        render_gallery(FENCES_DIR, "fences")
    with tab_pavers:
        render_gallery(PAVERS_DIR, "pavers")

def page_quote() -> None:
    st.title("Ready for a Free On-Site Estimate? 🤝")

    if "form_opened_at" not in st.session_state:
        st.session_state["form_opened_at"] = time.time()

    form_col, chat_col = st.columns(2, gap="large")
    with form_col:
        st.header("📝 Request a Quote")
        with st.form("contact_form"):
            name = st.text_input("👤 Full Name *", placeholder="John Doe")
            phone = st.text_input("📞 Phone Number *", placeholder="(206) 555-0199")
            email = st.text_input("✉️ Email (optional)", placeholder="you@example.com")
            project = st.selectbox("🏗️ Project Interest", PROJECT_OPTIONS)
            message = st.text_area("💬 Project Details", placeholder="Tell us about your yard, approximate footage, or timeline...", height=130)

            st.markdown('<div style="display:none;">', unsafe_allow_html=True)
            honeypot = st.text_input("Leave this field blank", key="hp_company_fax")
            st.markdown('</div>', unsafe_allow_html=True)

            submitted = st.form_submit_button("Send my request")

            if submitted:
                now = time.time()
                elapsed = now - st.session_state.get("form_opened_at", now)
                last_sent = st.session_state.get("last_lead_sent", 0)

                if now - last_sent < 60:
                    st.warning("⏳ We already received your request. Please wait a minute before sending another.")
                else:
                    status, err_msg = check_lead_security(name, phone, email, message, honeypot, elapsed)

                    if status == "error":
                        st.error(f"⚠️ {err_msg}")
                    elif status == "spam":
                        st.success("Thank you! Your request has been received.")
                    else:
                        lead_data = {
                            "timestamp": datetime.now().isoformat(timespec="seconds"),
                            "name": name.strip(),
                            "phone": phone.strip(),
                            "email": email.strip(),
                            "project": project,
                            "message": message.strip(),
                        }
                        save_lead_to_csv(lead_data)
                        st.session_state["last_lead_sent"] = now
                        st.success(f"✅ Thank you, {name}! Your request is verified. We will call you at {phone} shortly.")

    with chat_col:
        chat_panel()

# =============================================================================
# 7. ĐIỀU HƯỚNG ĐỒNG BỘ (ĐIỆN THOẠI + MÁY TÍNH)
# =============================================================================
PAGES = {
    "about": ("📜 About & Pricing", page_about),
    "gallery": ("🖼️ Projects Gallery", page_gallery),
    "quote": ("✉️ Free Estimate & AI", page_quote),
}

def _sync_nav(source_key: str) -> None:
    """Đồng bộ hóa thanh menu trên màn hình chính và thanh menu bên trái."""
    st.session_state["page"] = st.session_state[source_key]

def render_top_mobile_nav(total_visits: int) -> None:
    """Thanh điều hướng ngang luôn hiển thị rõ ràng trên điện thoại."""
    digits = re.sub(r"\D", "", BUSINESS["phone"])
    render_html(f"""
        <div class="top-bar">
            <span class="brand">⚜️ {esc(BUSINESS['name'])}</span>
            <span>
                <a class="call-btn" href="tel:{digits}">📞 Call {esc(BUSINESS['phone'])}</a>
                &nbsp; <small style="color:#A0A0A0;">👁️ {total_visits:,}</small>
            </span>
        </div>
    """)
    page_keys = list(PAGES)
    current_idx = page_keys.index(st.session_state["page"])
    nav_cols = st.columns(len(page_keys))
    for idx, k in enumerate(page_keys):
        with nav_cols[idx]:
            st.button(
                PAGES[k][0],
                key=f"top_nav_{k}",
                on_click=go_to,
                args=(k,),
                use_container_width=True,
            )
    st.divider()

def render_sidebar(total_visits: int) -> None:
    with st.sidebar:
        logo = BASE_DIR / "logo2.png"
        if logo.is_file():
            show_image(logo)
            st.markdown("<br>", unsafe_allow_html=True)
            
        st.title("⚜️ Navigation")
        page_keys = list(PAGES)
        current_idx = page_keys.index(st.session_state["page"])
        st.radio(
            "Menu",
            page_keys,
            index=current_idx,
            format_func=lambda k: PAGES[k][0],
            key="nav_sidebar",
            on_change=_sync_nav,
            args=("nav_sidebar",),
            label_visibility="collapsed",
        )
        st.divider()
        render_html(f"""
            <div style="line-height: 2;">
              📞 {esc(BUSINESS['phone'])}<br>
              📫 {esc(BUSINESS['email'])}<br>
              📍 {esc(BUSINESS['city'])}
            </div>
        """)
        st.caption(f"👁️ Total Visitors: **{total_visits:,}**")

def render_footer() -> None:
    st.divider()
    render_html(f"""
    <div style="text-align: center; padding: 30px 0 10px 0;">
        <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 20px; margin-bottom: 25px;">
            <span style="background: rgba(230, 194, 135, 0.1); border: 1px solid #5D4037; padding: 10px 20px; border-radius: 8px; color: #E6C287; font-size: 0.9rem; font-weight: 500;">
                🛡️ Fully Licensed & Insured
            </span>
            <span style="background: rgba(230, 194, 135, 0.1); border: 1px solid #5D4037; padding: 10px 20px; border-radius: 8px; color: #E6C287; font-size: 0.9rem; font-weight: 500;">
                ⭐ 5-Star Rated Professional
            </span>
            <span style="background: rgba(230, 194, 135, 0.1); border: 1px solid #5D4037; padding: 10px 20px; border-radius: 8px; color: #E6C287; font-size: 0.9rem; font-weight: 500;">
                🏆 Master Builder Certified
            </span>
        </div>
        <p style="color: #A0A0A0; font-size: 0.9rem; margin-bottom: 5px;">
            © {datetime.now().year} {esc(BUSINESS["name"])}. All Rights Reserved.
        </p>
        <p style="color: #666666; font-size: 0.8rem; font-style: italic;">
            Contractor License: #PREMIFP892KL | Serving the {esc(BUSINESS["city"])} Area
        </p>
    </div>
    """)

def main() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
    if st.session_state.get("page") not in PAGES:
        st.session_state["page"] = "about"
    
    total_visits = track_visitor()
    render_sidebar(total_visits)
    render_top_mobile_nav(total_visits)
    PAGES[st.session_state["page"]][1]()
    render_footer()

if __name__ == "__main__":
    main()