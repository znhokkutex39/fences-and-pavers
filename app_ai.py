"""
Premier Fencing & Pavers | Seattle, WA
Unified Desktop & Mobile Edition:
- 100% Local Image Assets (.jpg, .png, .webp, .avif) - Zero external image URLs
- Responsive UI: Hero Banner, 3-Tier Comparison Grid, Mobile Top Nav & Desktop Sidebar
- Consent-Based Analytics (analytics_events.csv) + Password-Protected Admin Dashboard
- Smart Lead Protection (leads.csv for verified leads, leads_review.csv for suspicious items)
"""
from __future__ import annotations

import base64
import csv
import hashlib
import html
import inspect
import mimetypes
import os
import re
import threading
import time
import uuid
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Premier Fencing & Pavers | Seattle, WA",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

esc = html.escape

# =============================================================================
# 1. CONFIGURATION & LOCAL ASSET PATHS (NO EXTERNAL URLS)
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
FENCES_DIR = BASE_DIR / "kho_anh" / "fences"
PAVERS_DIR = BASE_DIR / "kho_anh" / "pavers"
PHOTO_DIRS = {"Fencing": FENCES_DIR, "Pavers": PAVERS_DIR}

LEADS_FILE = BASE_DIR / "leads.csv"
REVIEW_FILE = BASE_DIR / "leads_review.csv"
ANALYTICS_FILE = BASE_DIR / "analytics_events.csv"

BUSINESS = {
    "name": "Premier Fencing & Pavers",
    "phone": "(123) 456-7890",
    "email": "info@premieroutdoor.com",
    "city": "Seattle, WA",
    "areas": ["Seattle", "Bellevue", "Kirkland", "Redmond"],
    "radius_mi": 30,
    "hours": "7:30 AM – 4:30 PM",
    "license": "PREMIFP892KL",
}
TRUST_BADGES = [
    "🛡️ Fully Licensed & Insured",
    "⭐ Owner-Operated Precision",
    "🏆 3-to-15 Year Workmanship Warranty",
]

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".avif"}
GALLERY_COLUMNS = 3
GALLERY_PAGE_SIZE = 9

# Local named files placed in BASE_DIR or kho_anh/
LOCAL_NAMED_ASSETS = {
    "hero": "bg_about.jpg",
    "workflow": "workflow 1.avif",
    "prem_fence_1": "premium fences 1.jpg",
    "prem_paver_1": "premium pavers 1.jpg",
    "prem_paver_2": "premium pavers 2.avif",
}

# =============================================================================
# 2. CONTENT: TIERS, PACKAGES, PROCESS & FAQ
# =============================================================================
TIER_ORDER = ("Budget", "Standard", "Premium")
CATEGORY_LABEL = {"Fencing": "🪵 Custom Fencing", "Pavers": "🧱 Patios, Walkways & Outdoor Living"}

TIERS = {
    "Budget": {
        "for": "Side yards, pet containment, rentals, and utility walkways.",
        "materials": "Pressure-treated pine, black vinyl-coated chain link, crushed rock & pea gravel.",
    },
    "Standard": {
        "flag": "⭐ Most Popular",
        "for": "Most Seattle backyards: authentic Western Red Cedar privacy and durable concrete paver patios.",
        "materials": "Western Red Cedar, Cedar + Black Hog Wire mesh, Concrete Pavers with Pea Gravel border.",
    },
    "Premium": {
        "for": "Architectural custom homes across Seattle, Bellevue, and Mercer Island.",
        "materials": "Woven & horizontal hardwoods, modular hardwood/porcelain pavers, and pergola living suites.",
    },
}

PRICING = [
    # --- STANDARD TIER ---
    {
        "key": "cedar_full",
        "tier": "Standard",
        "category": "Fencing",
        "icon": "🪵",
        "name": "Full Western Red Cedar Privacy Fence",
        "short": "Full Cedar Fence",
        "tag": "⭐ Most Popular Privacy Fence",
        "asset": "cedar_full.jpg",
        "fallback_idx": 0,
        "low": 35.0,
        "high": 48.0,
        "unit": "ft",
        "unit_long": "linear feet",
        "days": (3, 5),
        "warranty": 3,
        "keywords": ("cedar", "privacy", "wood", "full"),
        "points": [
            "**Built for Seattle weather:** Natural aromatic oils resist rot, warping, and damp Pacific Northwest winters.",
            "**Full privacy on both sides:** Tight vertical boards framed with a protective top cap and fascia trim.",
            "**Deep concrete footings:** Posts set 24–30 inches deep in high-strength concrete to handle windstorms.",
        ],
    },
    {
        "key": "cedar_wire",
        "tier": "Standard",
        "category": "Fencing",
        "icon": "🔲",
        "name": "Western Red Cedar Frame + Black Wire Mesh (Hog Wire)",
        "short": "Cedar + Wire Mesh",
        "tag": "⭐ Best for Views & Pets",
        "asset": "cedar_wire.jpg",
        "fallback_idx": 1,
        "low": 28.0,
        "high": 38.0,
        "unit": "ft",
        "unit_long": "linear feet",
        "days": (2, 4),
        "warranty": 3,
        "keywords": ("hog wire", "wire", "mesh", "cedar"),
        "points": [
            "**Smart hybrid layout:** Combine Full Cedar on street-facing sides with Cedar + Wire Mesh along the back line to preserve views and save ~20%.",
            "**Heavy 6-gauge welded steel:** Black powder-coated architectural grid secured tightly inside thick Cedar rails.",
            "**Pet & family friendly:** Keeps dogs safely inside while letting sunlight reach your garden beds.",
        ],
    },
    {
        "key": "pavers_std",
        "tier": "Standard",
        "category": "Pavers",
        "icon": "🧱",
        "name": "Standard Concrete Pavers + Crushed Rock / Pea Gravel Border",
        "short": "Concrete Pavers & Gravel",
        "tag": "⭐ Signature Patio Combo",
        "asset": "pavers_std.jpg",
        "fallback_idx": 0,
        "low": 12.0,
        "high": 18.5,
        "unit": "sq ft",
        "unit_long": "square feet",
        "days": (3, 6),
        "warranty": 3,
        "keywords": ("paver", "concrete", "patio", "pea gravel"),
        "points": [
            "**Solid center, permeable edge:** Interlocking concrete pavers for furniture and BBQ grills, framed by a natural crushed rock or pea gravel border.",
            "**Built-in rainwater drainage:** The gravel border absorbs heavy Seattle runoff and prevents puddles near your foundation.",
            "**4–6 inch compacted base:** Excavated over commercial geotextile weed fabric and locked with polymeric joint sand.",
        ],
    },
    # --- PREMIUM TIER (USES LOCAL DOWNLOADED FILES) ---
    {
        "key": "woven_hardwood_fence",
        "tier": "Premium",
        "category": "Fencing",
        "icon": "💎",
        "name": "Architectural Woven & Horizontal Hardwood Privacy Fence",
        "short": "Architectural Hardwood Fence",
        "tag": "💎 Architectural Woven Hardwood",
        "asset": LOCAL_NAMED_ASSETS["prem_fence_1"],
        "fallback_idx": -1,
        "low": 65.0,
        "high": 95.0,
        "unit": "ft",
        "unit_long": "linear feet",
        "days": (5, 9),
        "warranty": 15,
        "keywords": ("ipe", "hardwood", "luxury", "woven", "horizontal"),
        "points": [
            "**Custom basket-weave & horizontal slats:** Thick, kiln-dried hardwood boards interwoven across structural center stiles for a 3D shadow line.",
            "**Identical on both sides:** Good-neighbor double-sided craftsmanship looks finished from both inside your patio and the exterior lot line.",
            "**Decades of durability:** Naturally dense hardwood treated with UV-protective penetrating oil to resist moisture and insects.",
        ],
    },
    {
        "key": "modular_deck_paver",
        "tier": "Premium",
        "category": "Pavers",
        "icon": "✨",
        "name": "Architectural Modular Hardwood & Porcelain Paver Patio",
        "short": "Modular Hardwood / Porcelain Patio",
        "tag": "💎 Seamless Modular Patio",
        "asset": LOCAL_NAMED_ASSETS["prem_paver_1"],
        "fallback_idx": 0,
        "low": 35.0,
        "high": 55.0,
        "unit": "sq ft",
        "unit_long": "square feet",
        "days": (5, 8),
        "warranty": 10,
        "keywords": ("porcelain", "luxury", "modular", "deck", "slab"),
        "points": [
            "**Precision flush-fit grid:** Large-format modular hardwood and wood-grain porcelain slabs aligned with zero tripping hazards.",
            "**Custom planter & threshold integration:** Scribed cleanly around garden beds, Japanese maples, and sliding glass door thresholds.",
            "**Rapid sub-surface drainage:** Engineered over a permeable aggregate base so rainwater drains immediately beneath the surface.",
        ],
    },
    {
        "key": "outdoor_living_suite",
        "tier": "Premium",
        "category": "Pavers",
        "icon": "🏖️",
        "name": "Complete Luxury Patio, Decking & Pergola Lounge Suite",
        "short": "Luxury Patio & Pergola Suite",
        "tag": "💎 Complete Outdoor Living Suite",
        "asset": LOCAL_NAMED_ASSETS["prem_paver_2"],
        "fallback_idx": 1,
        "low": 45.0,
        "high": 75.0,
        "unit": "sq ft",
        "unit_long": "square feet",
        "days": (6, 12),
        "warranty": 15,
        "keywords": ("pergola", "suite", "resort", "lounge"),
        "points": [
            "**Resort-style backyard transformation:** Combines architectural patio surfacing with an overhead shade pergola and integrated lounge areas.",
            "**All-season Seattle enjoyment:** Creates a sheltered outdoor dining and relaxation room from spring through autumn.",
        ],
    },
    # --- BUDGET TIER ---
    {
        "key": "budget_fence",
        "tier": "Budget",
        "category": "Fencing",
        "icon": "🛠️",
        "name": "Pressure-Treated Pine or Black Vinyl-Coated Chain Link",
        "short": "Pine or Chain-Link Fence",
        "tag": "🛠️ Economy Fencing",
        "asset": "budget_fence.jpg",
        "fallback_idx": 2,
        "low": 15.5,
        "high": 25.0,
        "unit": "ft",
        "unit_long": "linear feet",
        "days": (2, 3),
        "warranty": 1,
        "keywords": ("pine", "chain link", "chain-link", "budget"),
        "points": [
            "**Pressure-treated pine:** Most affordable solid-wood privacy option, chemically treated to resist ground rot and insects.",
            "**Black vinyl-coated chain link:** Blends quietly into wooded yards, needs zero upkeep, and secures pets across long property lines.",
        ],
    },
    {
        "key": "budget_gravel",
        "tier": "Budget",
        "category": "Pavers",
        "icon": "🪨",
        "name": "Crushed Rock & Pea Gravel Patio or Side Walkway",
        "short": "Crushed Rock & Pea Gravel",
        "tag": "🛠️ Economy Hardscaping",
        "asset": "budget_gravel.jpg",
        "fallback_idx": 2,
        "low": 4.5,
        "high": 8.5,
        "unit": "sq ft",
        "unit_long": "square feet",
        "days": (1, 2),
        "warranty": 1,
        "keywords": ("gravel", "crushed rock", "walkway", "budget"),
        "points": [
            "**100% permeable drainage:** Eliminates mud in shaded side yards, dog runs, and fire-pit seating areas in 1–2 days.",
            "**Commercial weed barrier & timber edging:** Installed over heavy-duty geotextile fabric with pressure-treated timber borders.",
        ],
    },
]

for _p in PRICING:
    _p["form"] = f"{_p['tier']} - {_p['short']}"
PRICING_BY_KEY = {p["key"]: p for p in PRICING}
PROJECT_OPTIONS = ["Not sure yet"] + [p["form"] for p in PRICING] + ["Custom / Other"]

STEPS = [
    ("On-Site Measure", "We walk your property lines together, check slopes and drainage, and bring material samples."),
    ("Written Quote", "Materials and labor itemized line by line. A standard deposit reserves your build dates."),
    ("Utility Locate (811)", "Before digging a single post hole, we coordinate 811 marking for underground lines."),
    ("Precision Build", "Deep concrete footings, compacted gravel bases, and daily vacuum/broom job-site cleanup."),
    ("Final Walkthrough", "We inspect every gate latch and paver joint with you before collecting final payment."),
]

GREETING = (
    f"Hi! I'm the virtual assistant for {BUSINESS['name']}. "
    "Pick a question below or type your own for instant answers on materials, pricing, timelines, and warranties!"
)
QUICK_QUESTIONS = [
    "⭐ What is in your Standard Cedar & Paver package?",
    "💎 What makes the Premium tier special?",
    "📋 How does your 5-step process work?",
    "⏱️ How long does an installation take?",
    "🛡️ What warranty do you offer?",
]

LEAD_FIELDS = ["timestamp", "name", "phone", "email", "project", "message"]
ANALYTICS_FIELDS = ["timestamp", "session_hash", "event_type", "page"]
URL_RE = re.compile(r"https?://|www\.", re.I)
SPAM_RE = re.compile(
    r"\b(seo|backlinks?|crypto|bitcoin|casino|viagra|telegram|marketing agency|web design|rank your)\b",
    re.I,
)
FAKE_PHONES = {"1234567890", "0123456789", "0000000000", "1111111111", "9999999999"}
DISPOSABLE_EMAILS = ("tempmail.", "mailinator.", "guerrillamail.", "10minutemail.", "yopmail.")

# =============================================================================
# 3. THEME & RESPONSIVE CSS (DESKTOP + MOBILE)
# =============================================================================
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

:root{
  --slate:#29323C; --stone-a:#2D3134; --stone-b:#1F2224; --walnut:#4E342E;
  --wood:#5D4037; --oak:#8B5A2B; --oak-dark:#5C4033; --gold:#E6C287;
  --muted:rgba(255,255,255,.72); --glass:rgba(255,255,255,.04);
  --serif:'Playfair Display',Georgia,serif;
}

.stApp{background:linear-gradient(135deg,var(--slate) 0%,var(--walnut) 100%) fixed !important;font-family:'Plus Jakarta Sans',system-ui,sans-serif;}
header[data-testid="stHeader"]{background:transparent !important;}
#MainMenu,footer{visibility:hidden;}
[data-testid="collapsedControl"],[data-testid="stSidebarCollapsedControl"] button{background-color:#2C1E16 !important;border:1px solid var(--gold) !important;color:var(--gold) !important;border-radius:8px !important;}
[data-testid="collapsedControl"] svg,[data-testid="stSidebarCollapsedControl"] svg{fill:var(--gold) !important;color:var(--gold) !important;}

[data-testid="stMainBlockContainer"],[data-testid="stAppViewBlockContainer"],[data-testid="block-container"]{
  max-width:1240px !important; margin:32px auto 28px !important; padding:32px 44px !important;
  background:linear-gradient(145deg,var(--stone-a) 0%,var(--stone-b) 100%) !important;
  border:2px solid var(--wood) !important; border-radius:16px; box-shadow:0 20px 50px rgba(0,0,0,.6) !important;
}
@media (max-width:768px){
  [data-testid="stMainBlockContainer"],[data-testid="stAppViewBlockContainer"],[data-testid="block-container"]{
    padding:18px 14px !important; margin:10px auto !important; border-radius:12px;
  }
}

[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] li{color:#fff !important;font-weight:300 !important;line-height:1.7 !important;font-size:1.03rem !important;max-width:72ch;}
[data-testid="stMarkdownContainer"] strong{font-weight:600 !important;color:#FFE5B4;}
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p{color:#fff !important;font-weight:500 !important;font-size:.95rem !important;}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p{color:var(--muted) !important;font-size:.9rem !important;}
a,a:visited{color:var(--gold) !important;text-decoration:none;}
a:hover{text-decoration:underline;}

h1,h2,h3,h1 *,h2 *,h3 *{font-family:var(--serif) !important;color:var(--gold) !important;letter-spacing:.5px !important;}
[data-testid="stHeaderActionElements"]{display:none;}
hr{border-color:var(--wood) !important;}

/* Sidebar */
[data-testid="stSidebar"]{background:#2C1E16 !important;border-right:1px solid #4A3525 !important;}
[data-testid="stSidebar"] *{color:#E8EDE9 !important;}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] a{color:var(--gold) !important;}

/* Local Photos */
[data-testid="stImage"] img, .real-photo{
  width:100%; height:auto; aspect-ratio:4/3; object-fit:cover;
  border:2px solid var(--wood) !important; border-radius:12px !important;
  box-shadow:0 10px 28px rgba(0,0,0,.55) !important; transition:transform .3s ease,border-color .3s ease !important; display:block;
}
[data-testid="stImage"] img:hover, .real-photo:hover{transform:scale(1.015);border-color:var(--gold) !important;}
[data-testid="stSidebar"] [data-testid="stImage"] img{aspect-ratio:auto;object-fit:contain;border:none !important;box-shadow:none !important;}

/* Buttons */
div.stButton button,[data-testid="stFormSubmitButton"] button{
  background:linear-gradient(90deg,var(--oak) 0%,var(--oak-dark) 100%) !important;color:#fff !important;border:none !important;
  border-radius:6px !important;padding:.6rem 1.3rem !important;text-transform:uppercase !important;letter-spacing:1px !important;
  box-shadow:0 4px 15px rgba(139,90,43,.3) !important;transition:transform .25s ease,box-shadow .25s ease !important;
}
div.stButton button:hover,[data-testid="stFormSubmitButton"] button:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(139,90,43,.5) !important;}
div.stButton button p,[data-testid="stFormSubmitButton"] button p{color:#fff !important;font-weight:700 !important;font-size:.88rem !important;}

div[class*="st-key-ghost_"] div.stButton button{background:transparent !important;border:1px solid var(--gold) !important;box-shadow:none !important;}
div[class*="st-key-ghost_"] div.stButton button p{color:var(--gold) !important;}

div[class*="st-key-quick_"],div[class*="st-key-quick_"] div.stButton{width:100% !important;}
div[class*="st-key-quick_"] div.stButton button{background:var(--glass) !important;border:1px solid var(--wood) !important;box-shadow:none !important;text-transform:none !important;letter-spacing:0 !important;justify-content:flex-start !important;width:100%;padding:.45rem 1rem !important;}
div[class*="st-key-quick_"] div.stButton button:hover{border-color:var(--gold) !important;transform:none;}
div[class*="st-key-quick_"] div.stButton button p{font-weight:500 !important;font-size:.9rem !important;text-align:left;}

/* Mobile vs Laptop Top Navigation */
@media (max-width:768px){
  div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-top_nav_"]){flex-wrap:nowrap !important;gap:6px !important;}
  div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-top_nav_"])>div{min-width:0 !important;flex:1 1 0 !important;width:auto !important;}
  div[class*="st-key-top_nav_"] div.stButton button{padding:.45rem .15rem !important;letter-spacing:0 !important;text-transform:none !important;}
  div[class*="st-key-top_nav_"] div.stButton button p{font-size:.78rem !important;}
}

/* Top Bar & Consent Banner */
.top-bar{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;background:rgba(44,30,22,0.85);border:1px solid var(--wood);border-radius:10px;padding:10px 16px;margin-bottom:12px;}
.top-bar .brand{font-family:var(--serif);color:var(--gold);font-weight:700;font-size:1.12rem;}
.top-bar .call{background:rgba(230,194,135,0.15);border:1px solid var(--gold);border-radius:6px;padding:4px 12px;font-weight:600;font-size:.86rem;}
.consent-box{background:rgba(44,30,22,0.92);border:1px solid var(--gold);border-radius:10px;padding:12px 18px;margin-bottom:12px;font-size:0.9rem;color:#fff;}

/* Hero Section */
.hero{position:relative;overflow:hidden;display:flex;align-items:flex-end;min-height:clamp(260px,38vw,420px);margin:0 0 1.2rem;border:2px solid var(--wood);border-radius:14px;background:linear-gradient(135deg,#3b2a20 0%,var(--stone-b) 100%);}
.hero .bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;}
.hero::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,14,10,.15) 15%,rgba(18,14,10,.88) 100%);}
.hero .inner{position:relative;z-index:2;padding:clamp(20px,4vw,42px);}
.hero h1{margin:0 !important;font-size:clamp(2rem,5vw,3.4rem) !important;line-height:1.12 !important;text-shadow:0 2px 14px rgba(0,0,0,.6);}
.hero .sub{margin-top:.7rem;max-width:58ch;color:rgba(255,255,255,.92);font-weight:300;font-size:1.08rem;line-height:1.55;}

/* Ruled Columns (3 Value Props & 5 Process Steps) */
.ruled{display:grid;gap:24px;margin:.6rem 0 1.2rem;}
.ruled.c3{grid-template-columns:repeat(auto-fit,minmax(230px,1fr));}
.ruled.c5{grid-template-columns:repeat(auto-fit,minmax(170px,1fr));}
.ruled>div{position:relative;border-top:2px solid var(--wood);padding-top:14px;}
.ruled>div::before{content:"";position:absolute;top:-2px;left:0;width:44px;height:2px;background:var(--gold);}
.ruled .num{font-family:var(--serif);color:var(--gold);font-size:1.85rem;font-weight:600;line-height:1;margin-bottom:.3rem;}
.ruled h4{margin:0 0 .35rem !important;color:#fff !important;font-size:1.03rem !important;font-weight:600 !important;}
.ruled .desc{color:var(--muted);font-size:.94rem;line-height:1.6;font-weight:300;}

.note{border-left:3px solid var(--gold);background:var(--glass);padding:14px 18px;border-radius:0 10px 10px 0;margin:.8rem 0 1.2rem;color:#fff;font-weight:300;line-height:1.65;}
.note strong{color:var(--gold);font-weight:600;}

/* 3-Column Tier Overview */
.tiers{display:grid;grid-template-columns:repeat(3,1fr);border:1px solid var(--wood);border-radius:12px;overflow:hidden;margin:.5rem 0 1.4rem;background:var(--glass);}
.tier{padding:20px;border-right:1px solid var(--wood);}
.tier:last-child{border-right:none;}
.tier.feature{background:rgba(230,194,135,.07);box-shadow:inset 0 3px 0 var(--gold);}
.tier-head{display:flex;align-items:baseline;justify-content:space-between;gap:8px;margin-bottom:.4rem;}
.tier-name{font-family:var(--serif);color:var(--gold);font-size:1.45rem;font-weight:600;}
.tier .flag{color:var(--gold);font-size:.82rem;font-weight:600;}
.tier-for{color:#fff;font-weight:300;line-height:1.55;font-size:.95rem;margin-bottom:.8rem;}
.tier dl{margin:0 0 .8rem;}
.tier dl>div{display:flex;justify-content:space-between;gap:10px;padding:.4rem 0;border-top:1px solid rgba(93,64,55,.7);font-size:.92rem;}
.tier dt{color:var(--muted);font-weight:300;}
.tier dd{margin:0;color:#fff;font-weight:600;text-align:right;}
.tier-mat{color:var(--muted);font-size:.85rem;line-height:1.5;}

/* Package Showcase & Price Table */
.pkg-tag{display:inline-block;color:var(--gold);background:rgba(230,194,135,0.14);border:1px solid rgba(230,194,135,.55);border-radius:99px;padding:3px 12px;font-size:.8rem;font-weight:600;margin-bottom:.3rem;}
.pkg h3{margin:.2rem 0 .6rem !important;font-size:1.5rem !important;line-height:1.25 !important;}
.spec{display:flex;flex-wrap:wrap;gap:.5rem 2rem;padding:.65rem 0;margin-bottom:.5rem;border-top:1px solid var(--wood);border-bottom:1px solid var(--wood);}
.spec span{display:block;color:var(--muted);font-size:.78rem;}
.spec strong{display:block;color:#fff !important;font-weight:600;font-size:1rem;}

.table-wrap{overflow-x:auto;border:1px solid var(--wood);border-radius:12px;background:var(--glass);}
.price-table{width:100%;min-width:560px;border-collapse:collapse;}
.price-table th,.price-table td{text-align:left;padding:.8rem 1rem !important;}
.price-table th{background:rgba(139,90,43,.25) !important;color:var(--gold) !important;font-family:var(--serif);border-bottom:1px solid var(--wood) !important;}
.price-table td{color:#fff !important;font-weight:300;border-bottom:1px solid #3E2723 !important;}

.est{border-left:3px solid var(--gold);background:var(--glass);padding:16px 22px;margin:.6rem 0 1rem;border-radius:0 10px 10px 0;}
.est .range{font-family:var(--serif);color:var(--gold);font-size:clamp(1.8rem,4vw,2.5rem);font-weight:600;}
.est .meta{color:var(--muted);font-size:.92rem;margin-top:.35rem;}

@media (max-width:768px){
  .tiers{grid-template-columns:1fr;}
  .tier{border-right:none;border-bottom:1px solid var(--wood);}
  .tier:last-child{border-bottom:none;}
  .price-table{min-width:0;}
  .price-table th,.price-table td{padding:.6rem .5rem !important;font-size:.86rem;}
}
"""

# =============================================================================
# 4. HELPERS & 100% LOCAL IMAGE / AVIF ENGINE
# =============================================================================
def get_setting(name: str, default: str | None = None) -> str | None:
    val = os.environ.get(name)
    if val:
        return val
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default

def html_block(markup: str) -> str:
    return " ".join(line.strip() for line in markup.splitlines() if line.strip())

def render_html(markup: str) -> None:
    st.markdown(html_block(markup), unsafe_allow_html=True)

def md_safe(text: str) -> str:
    return text.replace("$", r"\$")

@lru_cache(maxsize=None)
def stretch_kwargs(widget: str) -> dict:
    try:
        if isinstance(inspect.signature(getattr(st, widget)).parameters["width"].default, str):
            return {"width": "stretch"}
    except (AttributeError, KeyError, TypeError, ValueError):
        pass
    return {"use_container_width": True}

def button(label: str, *, stretch: bool = False, **kwargs) -> bool:
    if stretch:
        try:
            return st.button(label, **kwargs, **stretch_kwargs("button"))
        except TypeError:
            pass
    return st.button(label, **kwargs)

def join_and(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]

def money(v: float) -> str:
    return f"${v:,.0f}" if float(v).is_integer() else f"${v:,.2f}"

def span_text(lo: int, hi: int) -> str:
    return f"{lo}" if lo == hi else f"{lo}–{hi}"

def days_text(lo: int, hi: int) -> str:
    return f"{span_text(lo, hi)} day" + ("" if hi == 1 else "s")

def years_text(lo: int, hi: int | None = None) -> str:
    hi = lo if hi is None else hi
    return f"{span_text(lo, hi)} year" + ("" if hi == 1 else "s")

def price_text(p: dict) -> str:
    return f"{money(p['low'])}–{money(p['high'])} / {p['unit']}"

def tier_items(tier: str, category: str | None = None) -> list[dict]:
    return [p for p in PRICING if p["tier"] == tier and (category is None or p["category"] == category)]

def tier_facts(tier: str) -> dict:
    items = tier_items(tier)
    return {
        "fence_from": min(p["low"] for p in tier_items(tier, "Fencing")),
        "patio_from": min(p["low"] for p in tier_items(tier, "Pavers")),
        "days": (min(p["days"][0] for p in items), max(p["days"][1] for p in items)),
        "warranty": (min(p["warranty"] for p in items), max(p["warranty"] for p in items)),
    }

def _natural_key(name: str) -> list:
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]

@st.cache_data(ttl=60, show_spinner=False)
def list_images(folder: str) -> list[str]:
    p = Path(folder)
    if not p.is_dir():
        return []
    files = [f for f in p.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTS]
    return [str(f) for f in sorted(files, key=lambda f: _natural_key(f.name))]

def resolve_local_asset(filename: str, fallback_folder: Path | None = None, fallback_idx: int = 0) -> Path | None:
    """Finds a local image in project root, kho_anh, fences, or pavers without using any external URLs."""
    candidates = [
        BASE_DIR / filename,
        BASE_DIR / "kho_anh" / filename,
        FENCES_DIR / filename,
        PAVERS_DIR / filename,
    ]
    for c in candidates:
        if c.is_file():
            return c

    target_lower = filename.lower()
    target_stem = Path(filename).stem.lower().replace("-", "_")
    for search_dir in (BASE_DIR, BASE_DIR / "kho_anh", FENCES_DIR, PAVERS_DIR):
        if search_dir.is_dir():
            for f in search_dir.iterdir():
                if f.is_file() and f.suffix.lower() in IMAGE_EXTS:
                    if f.name.lower() == target_lower or target_stem in f.stem.lower().replace("-", "_"):
                        return f

    if fallback_folder is not None:
        files = list_images(str(fallback_folder))
        if files:
            return Path(files[fallback_idx % len(files)])

    for any_folder in (FENCES_DIR, PAVERS_DIR, BASE_DIR):
        files = list_images(str(any_folder))
        if files:
            return Path(files[fallback_idx % len(files)])
    return None

@st.cache_data(show_spinner=False)
def _file_to_data_uri(path_str: str, mtime: float) -> str | None:
    """Encodes local .jpg/.png/.webp/.avif files directly into Data URIs so browsers never fail to load."""
    p = Path(path_str)
    if not p.is_file():
        return None
    ext = p.suffix.lower()
    mime_map = {
        ".avif": "image/avif",
        ".webp": "image/webp",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }
    mime = mime_map.get(ext) or mimetypes.guess_type(path_str)[0] or "image/jpeg"
    try:
        raw = p.read_bytes()
        b64 = base64.b64encode(raw).decode("ascii")
        return f"data:{mime};base64,{b64}"
    except OSError:
        return None

def show_image(path_or_obj, *, caption: str | None = None, is_sidebar: bool = False) -> None:
    """Renders local photos uniformly (including .avif) with zero external links."""
    if path_or_obj is None:
        render_html(
            '<div style="border:1px dashed #5D4037;border-radius:12px;padding:2.2rem;text-align:center;color:#A0A0A0;">'
            'Local photo not found. Add image files to your project folder or kho_anh/.</div>'
        )
        return

    p = Path(str(path_or_obj))
    if p.is_file():
        if is_sidebar:
            st.image(str(p))
            return
        uri = _file_to_data_uri(str(p), p.stat().st_mtime)
        if uri:
            cap_html = (
                f'<div style="text-align:center;color:rgba(255,255,255,0.72);font-size:0.88rem;margin-top:6px;">{esc(caption)}</div>'
                if caption else ""
            )
            render_html(
                f'<div><img class="real-photo" src="{uri}" alt="{esc(caption or p.name)}" loading="lazy"/>{cap_html}</div>'
            )
            return

    render_html(
        '<div style="border:1px dashed #5D4037;border-radius:12px;padding:2.2rem;text-align:center;color:#A0A0A0;">'
        'Local photo not found.</div>'
    )

def go_to(page: str, project: str | None = None) -> None:
    st.session_state["page"] = page
    if project:
        st.session_state["selected_project"] = project

# =============================================================================
# 5. CONSENT-BASED ANALYTICS (NO FAKE COUNTERS)
# =============================================================================
@st.cache_resource
def _file_lock() -> threading.Lock:
    return threading.Lock()

def _get_session_hash() -> str:
    if "anon_session_id" not in st.session_state:
        raw_id = f"{uuid.uuid4()}-{time.time()}"
        st.session_state["anon_session_id"] = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:12]
    return st.session_state["anon_session_id"]

def log_analytics_event(event_type: str, page: str) -> None:
    if st.session_state.get("analytics_consent") != "granted":
        return
    session_hash = _get_session_hash()
    logged_key = f"logged_{event_type}_{page}"
    if st.session_state.get(logged_key, False):
        return
    try:
        with _file_lock():
            is_new = not ANALYTICS_FILE.exists()
            with ANALYTICS_FILE.open("a", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=ANALYTICS_FIELDS)
                if is_new:
                    writer.writeheader()
                writer.writerow({
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "session_hash": session_hash,
                    "event_type": event_type,
                    "page": page,
                })
        st.session_state[logged_key] = True
    except OSError:
        pass

def inject_external_analytics() -> None:
    if st.session_state.get("analytics_consent") != "granted":
        return
    if st.session_state.get("ext_analytics_injected", False):
        return
    ga_id = get_setting("GA_MEASUREMENT_ID")
    cf_token = get_setting("CF_BEACON_TOKEN")
    scripts = []
    if ga_id:
        scripts.append(f"""
        <script async src="https://www.googletagmanager.com/gtag/js?id={esc(ga_id)}"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
          gtag('config', '{esc(ga_id)}', {{ 'anonymize_ip': true }});
        </script>
        """)
    if cf_token:
        scripts.append(f"""
        <script defer src="https://static.cloudflareinsights.com/beacon.min.js"
                data-cf-beacon='{{"token": "{esc(cf_token)}"}}'></script>
        """)
    if scripts:
        components.html("".join(scripts), height=0, width=0)
        st.session_state["ext_analytics_injected"] = True

def get_verified_analytics_summary() -> tuple[int, int]:
    if not ANALYTICS_FILE.is_file():
        return 0, 0
    sessions = set()
    pageviews = 0
    try:
        with ANALYTICS_FILE.open("r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pageviews += 1
                if row.get("session_hash"):
                    sessions.add(row["session_hash"])
    except OSError:
        return 0, 0
    return len(sessions), pageviews

def render_consent_banner() -> None:
    if st.session_state.get("analytics_consent") is not None:
        return
    render_html("""
        <div class="consent-box">
            🍪 <strong>Privacy &amp; Analytics Notice:</strong> We use privacy-friendly, anonymized analytics to understand which fencing and patio packages interest Seattle homeowners. No personal data is tracked without your permission.
        </div>
    """)
    c1, c2, _ = st.columns([1.2, 1.2, 3])
    with c1:
        if button("✅ Accept Analytics", key="btn_consent_yes", stretch=True):
            st.session_state["analytics_consent"] = "granted"
            st.rerun()
    with c2:
        if button("🔒 Essential Only", key="btn_consent_no", stretch=True):
            st.session_state["analytics_consent"] = "declined"
            st.rerun()

# =============================================================================
# 6. LEAD VALIDATION, HONEYPOT & STORAGE
# =============================================================================
def _csv_safe(value: str) -> str:
    value = str(value)
    return "'" + value if value[:1] in ("=", "+", "-", "@", "\t", "\r") else value

def save_lead(lead: dict, *, review: bool = False) -> bool:
    path = REVIEW_FILE if review else LEADS_FILE
    try:
        with _file_lock():
            is_new = not path.exists()
            with path.open("a", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=LEAD_FIELDS)
                if is_new:
                    writer.writeheader()
                writer.writerow({k: lead[k] if k == "phone" else _csv_safe(lead[k]) for k in LEAD_FIELDS})
        return True
    except OSError:
        return False

def assess_lead(name: str, phone: str, email: str, message: str, honeypot: str, elapsed_sec: float) -> tuple[str, str]:
    """Returns ('error' | 'review' | 'ok', error_message)."""
    if len(name.strip()) < 2:
        return "error", "Please enter your full name."
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10 or digits[0] in ("0", "1") or digits in FAKE_PHONES or len(set(digits)) == 1:
        return "error", "Please enter a valid 10-digit US phone number (e.g., 206-555-0199)."

    suspicious = (
        bool(honeypot.strip())
        or elapsed_sec < 3.0
        or bool(URL_RE.search(name))
        or bool(URL_RE.search(message) or SPAM_RE.search(message))
        or any(d in email.lower() for d in DISPOSABLE_EMAILS)
    )
    return ("review" if suspicious else "ok"), ""

# =============================================================================
# 7. SMART FAQ ASSISTANT
# =============================================================================
def _hit(text: str, *patterns: str) -> bool:
    return any(re.search(p, text) for p in patterns)

def faq_answer(text: str) -> str:
    t = text.lower().replace("’", "'")
    matched = [p for p in PRICING if any(re.search(rf"\b{re.escape(k)}", t) for k in p["keywords"])]
    items = matched or PRICING

    def lines(fmt) -> str:
        return "\n".join(f"- {fmt(p)}" for p in items)

    if _hit(t, r"\bpermits?\b", r"\bhoa\b", r"\bsetbacks?\b", r"\bregulations?\b"):
        return (
            "📋 **Permits & HOA Rules:**\n"
            "Permit and HOA rules depend on your city, lot lines, and fence height. "
            "We review all local requirements with you during your free on-site measurement."
        )
    if _hit(t, r"\bwarrant", r"\bguarantee"):
        return "🛡️ **Workmanship Warranties:**\n" + lines(lambda p: f"**{p['name']}**: {years_text(p['warranty'])}")
    if _hit(t, r"\bhow long\b", r"\btimeline\b", r"\bhow many days\b", r"\binstall\b", r"\bduration\b"):
        return (
            "⏱️ **Typical Build Times:**\n"
            + lines(lambda p: f"**{p['name']}**: {days_text(*p['days'])}")
            + "\n\n*Exact timing depends on project footage, slope, access, and Seattle weather.*"
        )
    if _hit(t, r"\bprocess\b", r"\bsteps?\b", r"\b5-step\b", r"\bwork\b"):
        return "📋 **Our 5-Step Process:**\n" + "\n".join(f"{n}. **{title}** — {desc}" for n, (title, desc) in enumerate(STEPS, 1))
    if _hit(t, r"\bstandard\b", r"\bpopular\b"):
        return (
            "⭐ **Our Most Popular Standard Setup:**\n"
            "- **Fencing:** Full Western Red Cedar ($35–$48/ft) or Cedar Frame + Black Hog Wire Mesh ($28–$38/ft).\n"
            "- **Patios:** Standard Interlocking Concrete Pavers with a Crushed Rock / Pea Gravel border ($12–$18.50/sq ft)."
        )
    if _hit(t, r"\bpremium\b", r"\bluxury\b", r"\bwoven\b", r"\bpergola\b", r"\bporcelain\b"):
        return (
            "💎 **Premium Custom Collection:**\n"
            "- **Fencing:** Architectural Woven & Horizontal Hardwood Fence ($65–$95/ft).\n"
            "- **Patios & Living:** Modular Hardwood & Porcelain Patios ($35–$55/sq ft) and Luxury Pergola Suites ($45–$75/sq ft)."
        )
    if _hit(t, r"\bprice", r"\bpricing\b", r"\bcosts?\b", r"\bhow much\b", r"\bquote\b", r"\bestimate"):
        return (
            "💰 **2026 Installed Price Ranges:**\n"
            + lines(lambda p: f"**{p['name']}**: {price_text(p)}")
            + "\n\nFill out the form on this page for a free on-site measurement and itemized written quote."
        )
    return (
        f"Thank you for reaching out! Use the **Request a Free Estimate** form on the left "
        f"or call us directly at **{BUSINESS['phone']}** to schedule your free on-site measure."
    )

def init_chat() -> None:
    if "chat" not in st.session_state:
        st.session_state["chat"] = [{"role": "assistant", "content": GREETING}]

def queue_question(text: str) -> None:
    init_chat()
    st.session_state["chat"].append({"role": "user", "content": text})

def chat_panel() -> None:
    st.header("🤖 Quick Answers")
    st.caption("Instant answers on materials, pricing, timelines, and warranties.")
    init_chat()
    for i, question in enumerate(QUICK_QUESTIONS):
        button(question, key=f"quick_{i}", stretch=True, on_click=queue_question, args=(question,))

    box = st.container(height=360, border=True)
    prompt = st.chat_input("Ask a question about your project...", max_chars=500)
    if prompt:
        queue_question(prompt)

    chat = st.session_state["chat"]
    with box:
        for m in chat:
            with st.chat_message(m["role"], avatar="🌿" if m["role"] == "assistant" else None):
                st.markdown(md_safe(m["content"]))
        if chat[-1]["role"] == "user":
            reply = faq_answer(chat[-1]["content"])
            with st.chat_message("assistant", avatar="🌿"):
                st.markdown(md_safe(reply))
            chat.append({"role": "assistant", "content": reply})

# =============================================================================
# 8. PAGES (HOME/CREW, PRICING, GALLERY, QUOTE, ADMIN)
# =============================================================================

# PAGE 1: HOME / OUR CREW & PROCESS
def page_home() -> None:
    hero_path = resolve_local_asset(LOCAL_NAMED_ASSETS["hero"], FENCES_DIR, 0)
    hero_uri = _file_to_data_uri(str(hero_path), hero_path.stat().st_mtime) if (hero_path and hero_path.is_file()) else None
    bg_img = f'<img class="bg" src="{hero_uri}" alt="Premier Fencing & Pavers">' if hero_uri else ""

    render_html(f"""
        <section class="hero">
          {bg_img}
          <div class="inner">
            <h1>Local Craftsmen. Zero Middlemen.</h1>
            <div class="sub">Owner-operated fencing and hardscaping crew serving {esc(join_and(BUSINESS['areas']))} within a {BUSINESS['radius_mi']}-mile radius.</div>
          </div>
        </section>
    """)

    c1, c2, _ = st.columns([1.2, 1.2, 2.6])
    with c1:
        button("Get a Free Estimate", key="cta_home_top", stretch=True, on_click=go_to, args=("quote",))
    with c2:
        button("Explore Materials & Pricing", key="ghost_home_pricing", stretch=True, on_click=go_to, args=("pricing",))

    st.header("Why Homeowners Prefer Our Small, Dedicated Crew")
    st.write(
        "With a large corporate contractor, the salesperson who estimates your yard is rarely the person who builds it. "
        "With Premier Fencing & Pavers, the owner who measures your yard is on-site building your project every single day."
    )
    render_html("""
        <div class="ruled c3">
          <div><h4>🤝 Talk Directly to the Builder</h4><div class="desc">Work directly with the lead installer—nothing gets lost between a sales rep and a subcontracted crew.</div></div>
          <div><h4>📐 2–3 Master Installers</h4><div class="desc">The same tight-knit, experienced team stays on your backyard from the first post hole to the final cleanup.</div></div>
          <div><h4>💰 Fair Local Pricing</h4><div class="desc">Low overhead means more of your budget goes straight into thicker Western Red Cedar, deeper concrete footings, and stronger base rock.</div></div>
        </div>
    """)

    st.divider()
    st.header("What We Build")
    left, right = st.columns(2, gap="large")
    with left:
        show_image(
            resolve_local_asset("cedar_full.jpg", FENCES_DIR, 0),
            caption="Custom Western Red Cedar, Hog Wire Mesh & Architectural Hardwood Fencing",
        )
        st.subheader(CATEGORY_LABEL["Fencing"])
        st.markdown("\n".join(f"- **{p['short']}** ({p['tier']} Tier)" for p in PRICING if p["category"] == "Fencing"))
    with right:
        show_image(
            resolve_local_asset(LOCAL_NAMED_ASSETS["prem_paver_1"], PAVERS_DIR, 0),
            caption="Interlocking Concrete Pavers, Pea Gravel Borders & Modular Patio Suites",
        )
        st.subheader(CATEGORY_LABEL["Pavers"])
        st.markdown("\n".join(f"- **{p['short']}** ({p['tier']} Tier)" for p in PRICING if p["category"] == "Pavers"))

    st.divider()
    st.header("📋 Our 5-Step Contracting Workflow")
    std_days = days_text(*tier_facts("Standard")["days"])
    steps_html = "".join(
        f'<div><div class="num">{n:02d}</div><h4>{esc(title)}</h4>'
        f'<div class="desc">{esc(desc)}{esc(f" Standard builds typically take {std_days}." if n == 4 else "")}</div></div>'
        for n, (title, desc) in enumerate(STEPS, 1)
    )
    render_html(f'<div class="ruled c5">{steps_html}</div>')

    wf_col1, wf_col2 = st.columns([1.25, 1], gap="large")
    with wf_col1:
        render_html(
            f'<div class="note"><strong>Clean, Respectful Job Sites Every Day:</strong> We work {esc(BUSINESS["hours"])}, '
            "respect your neighbors, custom-cut materials with precision, sweep polymeric joints, and shop-vac debris at the end of every single afternoon.</div>"
        )
        button("👉 View Detailed Packages & Price Calculator", key="cta_home_bottom", on_click=go_to, args=("pricing",))
    with wf_col2:
        show_image(
            resolve_local_asset(LOCAL_NAMED_ASSETS["workflow"], PAVERS_DIR, 0),
            caption="Our crew on-site cutting stone pavers, sweeping joints, and vacuuming debris",
        )

# PAGE 2: MATERIALS, PACKAGES & PRICING
def tier_overview() -> None:
    cols = []
    for tier in TIER_ORDER:
        info, f = TIERS[tier], tier_facts(tier)
        flag = f'<span class="flag">{esc(info["flag"])}</span>' if info.get("flag") else ""
        cols.append(
            f'<div class="tier{" feature" if info.get("flag") else ""}">'
            f'<div class="tier-head"><span class="tier-name">{tier}</span>{flag}</div>'
            f'<div class="tier-for">{esc(info["for"])}</div>'
            f'<dl><div><dt>Fences from</dt><dd>{money(f["fence_from"])} / ft</dd></div>'
            f'<div><dt>Patios from</dt><dd>{money(f["patio_from"])} / sq ft</dd></div>'
            f'<div><dt>Build time</dt><dd>{days_text(*f["days"])}</dd></div>'
            f'<div><dt>Warranty</dt><dd>{years_text(*f["warranty"])}</dd></div></dl>'
            f'<div class="tier-mat">{esc(info["materials"])}</div></div>'
        )
    render_html('<div class="tiers">' + "".join(cols) + "</div>")

def package_row(p: dict) -> None:
    folder = PHOTO_DIRS[p["category"]]
    img_path = resolve_local_asset(p["asset"], folder, p["fallback_idx"])
    left, right = st.columns([1, 1.35], gap="large")
    with left:
        show_image(img_path, caption=p["name"])
    with right:
        render_html(
            f'<div class="pkg"><span class="pkg-tag">{esc(p["tag"])}</span><h3>{esc(p["name"])}</h3>'
            f'<div class="spec"><div><span>Installed Price</span><strong>{esc(price_text(p))}</strong></div>'
            f'<div><span>Build Time</span><strong>{esc(days_text(*p["days"]))}</strong></div>'
            f'<div><span>Warranty</span><strong>{esc(years_text(p["warranty"]))}</strong></div></div></div>'
        )
        st.markdown(md_safe("\n".join(f"- {pt}" for pt in p["points"])))
        button(f"Request Quote for {p['short']}", key=f"quote_{p['key']}", on_click=go_to, args=("quote", p["form"]))
    st.markdown("<br>", unsafe_allow_html=True)

def price_table() -> None:
    rows = "".join(
        f'<tr>'
        f'<td><strong>{esc(p["tier"])}</strong></td>'
        f'<td>{esc(p["category"])}</td>'
        f'<td>{p["icon"]} <strong>{esc(p["name"])}</strong></td>'
        f'<td>{esc(price_text(p))}</td>'
        f'<td>{esc(days_text(*p["days"]))}</td>'
        f'<td>{esc(years_text(p["warranty"]))}</td>'
        f'</tr>'
        for p in PRICING
    )
    render_html(
        '<div class="table-wrap"><table class="price-table">'
        '<thead><tr><th>Tier</th><th>Category</th><th>Package</th><th>Installed Price</th><th>Build Time</th><th>Warranty</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div>'
    )

def estimator() -> None:
    st.subheader("🧮 Interactive Cost Estimator")
    st.caption("Select any package and enter your approximate size for an instant baseline range.")
    left, right = st.columns(2)
    key = left.selectbox(
        "Select Material Package",
        list(PRICING_BY_KEY),
        key="calc_type",
        format_func=lambda k: f"[{PRICING_BY_KEY[k]['tier']}] {PRICING_BY_KEY[k]['icon']} {PRICING_BY_KEY[k]['name']}",
    )
    p = PRICING_BY_KEY[key]
    qty = right.number_input(
        f"Project Size ({p['unit_long']})",
        min_value=1,
        max_value=100_000,
        value=120,
        step=1,
        key="calc_qty",
    )
    render_html(f"""
        <div class="est">
          <div class="range">${p['low'] * qty:,.2f} – ${p['high'] * qty:,.2f}</div>
          <div class="meta">Estimated range for <strong>{qty:,} {esc(p['unit_long'])}</strong> of <strong>{esc(p['name'])}</strong> ({esc(p['tier'])} Tier). Includes standard labor &amp; materials.</div>
        </div>
    """)
    button("📩 Lock In a Free On-Site Measurement for This Package", key="cta_calc", on_click=go_to, args=("quote", p["form"]))

def page_pricing() -> None:
    st.title("Materials, Packages & Pricing 🧱")
    st.write("Compare our 3 material tiers side-by-side, then select a tier tab below to inspect project photos and specifications for **Fencing** and **Pavers**.")
    tier_overview()
    price_table()
    st.divider()

    st.subheader("🔍 Select a Tier Below to View Photos & Specifications")
    tabs = st.tabs([
        "⭐ STANDARD TIER (Most Popular - Cedar & Concrete Pavers)",
        "💎 PREMIUM TIER (Ultra-Luxury Custom Collection)",
        "🛠️ BUDGET TIER (Economy - Pine, Chain Link & Gravel)",
    ])
    for tab, tier in zip(tabs, ("Standard", "Premium", "Budget")):
        with tab:
            st.markdown(f"> **{tier} Tier Focus:** {TIERS[tier]['for']}")
            for category in ("Fencing", "Pavers"):
                items = tier_items(tier, category)
                if items:
                    st.markdown(f"## {CATEGORY_LABEL[category]}")
                    for p in items:
                        package_row(p)

    st.divider()
    estimator()

# PAGE 3: COMPLETED PROJECTS GALLERY
def render_gallery(category: str, key: str, fallback_asset: str) -> None:
    files = list_images(str(PHOTO_DIRS[category]))
    if not files:
        fallback = resolve_local_asset(fallback_asset)
        if fallback:
            show_image(fallback, caption="Featured Local Installation")
        else:
            st.info(f"Add project photos to `kho_anh/{PHOTO_DIRS[category].name}` to populate this gallery.")
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
        button("Show more photos", key=f"gallery_{key}_more", on_click=show_more)

def page_gallery() -> None:
    st.title("Completed Projects Gallery 🌿")
    st.write("Browse real fencing and patio installations across the Greater Seattle area.")
    tab_fences, tab_pavers = st.tabs(["🪵 Fencing Portfolio", "🧱 Pavers & Hardscaping Portfolio"])
    with tab_fences:
        render_gallery("Fencing", "fences", LOCAL_NAMED_ASSETS["prem_fence_1"])
    with tab_pavers:
        render_gallery("Pavers", "pavers", LOCAL_NAMED_ASSETS["prem_paver_1"])
    st.divider()
    button("Get a Free Estimate for Your Yard", key="cta_gallery", on_click=go_to, args=("quote",))

# PAGE 4: FREE ESTIMATE & AI ASSISTANT
def _clear_lead_done() -> None:
    st.session_state.pop("lead_done", None)

def page_quote() -> None:
    st.title("Request a Free On-Site Estimate 🤝")
    st.write("Tell us what you are planning. We will call to schedule a free on-site measurement, then send an itemized written quote.")
    st.session_state.setdefault("form_opened_at", time.time())

    form_col, chat_col = st.columns(2, gap="large")
    with form_col:
        st.header("📝 Your Project Details")
        done = st.session_state.get("lead_done")
        if done:
            render_html(
                f'<div class="note"><strong>✅ Request Received!</strong> Thank you, {esc(done["first"])}. '
                f'We have logged your interest in <strong>{esc(done["project"])}</strong> and will call '
                f'<strong>{esc(done["phone"])}</strong> shortly to schedule your free on-site measure.</div>'
            )
            button("Send Another Request", key="ghost_lead_again", on_click=_clear_lead_done)
        else:
            default_proj = st.session_state.get("selected_project", PROJECT_OPTIONS[0])
            proj_idx = PROJECT_OPTIONS.index(default_proj) if default_proj in PROJECT_OPTIONS else 0

            with st.form("contact_form"):
                name = st.text_input("👤 Full Name *", placeholder="John Doe", max_chars=80)
                phone = st.text_input("📞 US Phone Number *", placeholder="(206) 555-0199", max_chars=24)
                email = st.text_input("✉️ Email Address (optional)", placeholder="you@example.com", max_chars=120)
                project = st.selectbox("🏗️ Selected Package / Interest", PROJECT_OPTIONS, index=proj_idx)
                message = st.text_area(
                    "💬 Approximate Footage & Yard Notes",
                    placeholder="e.g., About 140 ft of Cedar + Wire fence, or 300 sq ft Concrete Paver patio with Pea Gravel border...",
                    height=130,
                    max_chars=1000,
                )

                st.markdown('<div style="display:none;">', unsafe_allow_html=True)
                honeypot = st.text_input("Leave this field blank", key="hp_company_fax")
                st.markdown("</div>", unsafe_allow_html=True)

                submitted = st.form_submit_button("Send My Request")

                if submitted:
                    now = time.time()
                    elapsed = now - st.session_state.get("form_opened_at", now)
                    if now - st.session_state.get("last_lead_sent", 0) < 60:
                        st.warning("⏳ We already received your request. Please wait a minute before sending another.")
                    else:
                        status, err_msg = assess_lead(name, phone, email, message, honeypot, elapsed)
                        if status == "error":
                            st.error(f"⚠️ {err_msg}")
                        else:
                            lead_data = {
                                "timestamp": datetime.now().isoformat(timespec="seconds"),
                                "name": name.strip(),
                                "phone": re.sub(r"[^\d+()\-.\s]", "", phone).strip(),
                                "email": email.strip(),
                                "project": project,
                                "message": message.strip(),
                            }
                            save_lead(lead_data, review=(status == "review"))
                            if status == "ok":
                                log_analytics_event("lead_submitted", "quote")
                            st.session_state["last_lead_sent"] = now
                            st.session_state["lead_done"] = {
                                "first": lead_data["name"].split()[0],
                                "project": project,
                                "phone": lead_data["phone"],
                            }
                            st.session_state.pop("selected_project", None)
                            st.rerun()

    with chat_col:
        chat_panel()

# PAGE 5: ADMIN & ANALYTICS DASHBOARD (PASSWORD PROTECTED)
def page_admin() -> None:
    st.title("🔒 Admin & Analytics Dashboard")
    admin_pass = get_setting("ADMIN_PASSCODE", "premier2026")

    if not st.session_state.get("admin_unlocked", False):
        st.info("Restricted area for management. Enter passcode to view traffic and customer leads.")
        pwd = st.text_input("Admin Passcode", type="password")
        if button("Unlock Dashboard", key="btn_unlock_admin"):
            if pwd == admin_pass:
                st.session_state["admin_unlocked"] = True
                st.rerun()
            else:
                st.error("❌ Incorrect passcode.")
        return

    if button("🔒 Lock Dashboard", key="ghost_lock_admin"):
        st.session_state["admin_unlocked"] = False
        st.rerun()

    st.divider()
    st.header("📈 Website Traffic & Page Interests")
    if ANALYTICS_FILE.is_file():
        import pandas as pd
        try:
            df_traffic = pd.read_csv(ANALYTICS_FILE)
            page_counts = df_traffic[df_traffic["event_type"] == "pageview"]["page"].value_counts()
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Total Verified Pageviews", int(page_counts.sum()))
                st.metric("Unique Opt-In Sessions", int(df_traffic["session_hash"].nunique()))
            with c2:
                st.write("**Most Visited Pages:**")
                st.bar_chart(page_counts)
        except Exception as e:
            st.error(f"Error reading analytics: {e}")
    else:
        st.info("No consented analytics data recorded yet.")

    st.divider()
    st.header("📬 Verified Customer Leads (leads.csv)")
    if LEADS_FILE.is_file():
        import pandas as pd
        try:
            df_leads = pd.read_csv(LEADS_FILE)
            st.write("**Most Requested Material Packages:**")
            st.bar_chart(df_leads["project"].value_counts())
            st.write("**Customer Contact List:**")
            st.dataframe(df_leads.sort_values(by="timestamp", ascending=False), use_container_width=True)
        except Exception as e:
            st.error(f"Error reading leads: {e}")
    else:
        st.info("No customer leads submitted yet.")

    if REVIEW_FILE.is_file():
        import pandas as pd
        with st.expander("🕵️ Suspicious / Filtered Submissions (leads_review.csv)"):
            try:
                df_rev = pd.read_csv(REVIEW_FILE)
                st.dataframe(df_rev.sort_values(by="timestamp", ascending=False), use_container_width=True)
            except Exception as e:
                st.error(f"Error reading review file: {e}")

# =============================================================================
# 9. NAVIGATION (MOBILE + LAPTOP) & FOOTER
# =============================================================================
PAGES = {
    "home": ("🏛️ Our Crew & Process", page_home, "Crew"),
    "pricing": ("🧱 Materials & Pricing", page_pricing, "Pricing"),
    "gallery": ("🖼️ Projects Gallery", page_gallery, "Gallery"),
    "quote": ("✉️ Free Estimate & AI", page_quote, "Estimate"),
    "admin": ("🔒 Admin Dashboard", page_admin, "Admin"),
}
PUBLIC_NAV_KEYS = ("home", "pricing", "gallery", "quote")

def _sync_nav(source_key: str) -> None:
    st.session_state["page"] = st.session_state[source_key]

def render_top_bar() -> None:
    """Displays Brand + Call button + 4 clean navigation buttons optimized for mobile & laptop."""
    digits = re.sub(r"\D", "", BUSINESS["phone"])
    render_html(f"""
        <div class="top-bar">
            <span class="brand">⚜️ {esc(BUSINESS['name'])}</span>
            <a class="call" href="tel:{digits}">📞 Call {esc(BUSINESS['phone'])}</a>
        </div>
    """)
    nav_cols = st.columns(len(PUBLIC_NAV_KEYS))
    for col, k in zip(nav_cols, PUBLIC_NAV_KEYS):
        with col:
            button(PAGES[k][2], key=f"top_nav_{k}", stretch=True, on_click=go_to, args=(k,))
    st.divider()

def render_sidebar() -> None:
    with st.sidebar:
        logo = BASE_DIR / "logo2.png"
        if logo.is_file():
            show_image(logo, is_sidebar=True)
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
        digits = re.sub(r"\D", "", BUSINESS["phone"])
        render_html(f"""
            <div style="line-height: 2;">
              📞 <a href="tel:{digits}">{esc(BUSINESS['phone'])}</a><br>
              📫 <a href="mailto:{esc(BUSINESS['email'])}">{esc(BUSINESS['email'])}</a><br>
              📍 {esc(BUSINESS['city'])} ({BUSINESS['radius_mi']}-mi radius)
            </div>
        """)

        with st.expander("🔒 Privacy & Analytics"):
            consent_state = st.session_state.get("analytics_consent")
            status_label = (
                "Granted (Opted-In)" if consent_state == "granted"
                else "Declined (Essential Only)" if consent_state == "declined"
                else "Pending Consent"
            )
            st.caption(f"Status: **{status_label}**")
            c_yes, c_no = st.columns(2)
            with c_yes:
                if button("Opt-In", key="sb_opt_in", stretch=True):
                    st.session_state["analytics_consent"] = "granted"
                    st.rerun()
            with c_no:
                if button("Opt-Out", key="sb_opt_out", stretch=True):
                    st.session_state["analytics_consent"] = "declined"
                    st.rerun()

            if consent_state == "granted":
                uniq_sessions, total_views = get_verified_analytics_summary()
                st.caption(f"Verified Sessions: **{uniq_sessions}** | Pageviews: **{total_views}**")

def render_footer() -> None:
    st.divider()
    badges_html = "".join(
        f'<span style="background:rgba(230,194,135,0.1);border:1px solid #5D4037;padding:8px 16px;border-radius:8px;color:#E6C287;font-size:0.86rem;font-weight:500;">{esc(b)}</span>'
        for b in TRUST_BADGES
    )
    render_html(f"""
    <div style="text-align: center; padding: 20px 0 10px 0;">
        <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 14px; margin-bottom: 18px;">
            {badges_html}
        </div>
        <p style="color: #A0A0A0; font-size: 0.88rem; margin-bottom: 4px;">
            © {datetime.now().year} {esc(BUSINESS["name"])}. All Rights Reserved.
        </p>
        <p style="color: #666666; font-size: 0.78rem; font-style: italic;">
            Contractor License: #{esc(BUSINESS["license"])} | Serving {esc(join_and(BUSINESS["areas"]))} &amp; Surrounding Areas
        </p>
    </div>
    """)

def main() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
    if st.session_state.get("page") not in PAGES:
        st.session_state["page"] = "home"

    current_page = st.session_state["page"]
    log_analytics_event("pageview", current_page)
    inject_external_analytics()

    render_sidebar()
    render_consent_banner()
    render_top_bar()
    PAGES[current_page][1]()
    render_footer()

if __name__ == "__main__":
    main()