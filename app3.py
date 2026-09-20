import streamlit as st
import streamlit.components.v1 as components
import random
import io
from PIL import Image, ImageOps, ImageDraw, ImageFont
from pathlib import Path

# ============================================================
# NOVA // PERSONAL ARCHIVE
# Complete interactive birthday experience for FARHEEN
# ============================================================

st.set_page_config(
    page_title="FARHEEN ✦ NOVA",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Session state
# -----------------------------
defaults = {
    "page": "🌌 HOME",
    "home_card": None,
    "captured_photos": [],
    "day_submitted": False,
    "review_submitted": False,
    "secret_found": False,
    "random_event": None,
    "capsule_saved": False,
    "soundtrack": [],
    "achievements": set(),
    "future_message_seen": False,
    "final_reveal_requested": False,
    "quiz_options": None,
    "archive_override": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ------------------------------------------------------------
# Navigation + reveal routing
# ------------------------------------------------------------
reveal_route = st.query_params.get("nova_reveal")
if reveal_route == "1":
    st.session_state["final_reveal_requested"] = True

# -----------------------------
# Helpers
# -----------------------------
def award(name):
    st.session_state.achievements.add(name)

def nav_button(label, target):
    if st.button(label, key=f"nav_{target}", use_container_width=True):
        st.query_params.clear()
        st.session_state.page = target
        st.rerun()

def activity_checks():
    if st.session_state.archive_override:
        return [
            ("ARCHIVE EXPLORED", True),
            ("MEMORIES CAPTURED", True),
            ("DAY RECORDED", True),
            ("WEBSITE REVIEWED", True),
            ("SECRET FOUND", True),
            ("FUTURE VISITED", True),
        ]
    return [
        ("ARCHIVE EXPLORED", "FIRST DISCOVERY" in st.session_state.achievements),
        ("MEMORIES CAPTURED", len(st.session_state.captured_photos) > 0),
        ("DAY RECORDED", st.session_state.day_submitted),
        ("WEBSITE REVIEWED", st.session_state.review_submitted),
        ("SECRET FOUND", st.session_state.secret_found),
        ("FUTURE VISITED", "TIME TRAVELER" in st.session_state.achievements),
    ]

def activity_percent():
    checks = activity_checks()
    completed = sum(done for _, done in checks)
    return int(completed / len(checks) * 100), completed, len(checks)

def section_title(kicker, title, subtitle=""):
    st.markdown(
        f"""
        <div class="section-head">
            <div class="kicker">{kicker}</div>
            <div class="section-title">{title}</div>
            <div class="section-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def card(title, body, icon="✦"):
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="card-icon">{icon}</div>
            <div class="card-title">{title}</div>
            <div class="card-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def make_collage(photo_bytes_list):
    imgs = []
    for raw in photo_bytes_list:
        try:
            im = Image.open(io.BytesIO(raw)).convert("RGB")
            im.thumbnail((900, 900))
            imgs.append(im)
        except Exception:
            pass

    if not imgs:
        return None

    W, H = 1800, 1350
    bg = Image.new("RGB", (W, H), "#070b18")
    draw = ImageDraw.Draw(bg)

    # Header
    draw.text((90, 55), "✦ NOVA MEMORY VAULT ✦", fill="white")
    draw.text((90, 105), "06 • 11 • 2009   //   A DAY WORTH REMEMBERING", fill="#b8c7ff")

    n = len(imgs)
    if n == 1:
        boxes = [(120, 190, 1680, 1230)]
    elif n == 2:
        boxes = [(100, 210, 850, 1230), (950, 210, 1700, 1230)]
    elif n == 3:
        boxes = [(90, 220, 850, 760), (950, 220, 1710, 760), (520, 800, 1280, 1280)]
    elif n == 4:
        boxes = [(90, 220, 850, 735), (950, 220, 1710, 735),
                 (90, 790, 850, 1305), (950, 790, 1710, 1305)]
    else:
        # 5+ photos: large hero + smaller memories
        boxes = [(90, 220, 1110, 820), (1170, 220, 1710, 820),
                 (90, 870, 610, 1305), (650, 870, 1170, 1305),
                 (1210, 870, 1710, 1305)]
        if n > 5:
            # Reuse the remaining images in a compact strip by replacing slots cyclically.
            pass

    for i, im in enumerate(imgs[:len(boxes)]):
        x1, y1, x2, y2 = boxes[i]
        crop = ImageOps.fit(im, (x2-x1, y2-y1), method=Image.Resampling.LANCZOS)
        # shadow
        draw.rounded_rectangle((x1+8, y1+10, x2+8, y2+10), radius=24, fill="#02040b")
        bg.paste(crop, (x1, y1))
        draw.rounded_rectangle((x1, y1, x2, y2), radius=24, outline="#dbe4ff", width=4)

    if n > len(boxes):
        # Make a second tiny row using any extra images.
        extra = imgs[len(boxes):]
        y = 1320
        for i, im in enumerate(extra[:3]):
            crop = ImageOps.fit(im, (180, 20), method=Image.Resampling.LANCZOS)
            bg.paste(crop, (90 + i*210, y))

    return bg

# -----------------------------
# Grand visual system
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700;800&family=Orbitron:wght@400;500;600;700;800&family=Poppins:wght@300;400;500;600;700&display=swap');

    :root {
        --bg:#040610;
        --panel:rgba(12,17,38,.72);
        --line:rgba(160,180,255,.20);
        --text:#f3f6ff;
        --muted:#9da8c8;
        --glow:#8ea7ff;
        --glow2:#d7b8ff;
    }

    .stApp {
        background:
            radial-gradient(circle at 20% 10%, rgba(82,105,220,.16), transparent 26%),
            radial-gradient(circle at 80% 25%, rgba(180,92,255,.12), transparent 25%),
            radial-gradient(circle at 50% 100%, rgba(30,150,210,.10), transparent 35%),
            #040610;
        color:var(--text);
        font-family:'Poppins',sans-serif;
        overflow-x:hidden;
    }

    .stApp:before {
        content:"";
        position:fixed;
        inset:0;
        pointer-events:none;
        opacity:.5;
        background-image:
          radial-gradient(circle, rgba(255,255,255,.8) 1px, transparent 1.5px),
          radial-gradient(circle, rgba(150,180,255,.45) 1px, transparent 1.5px);
        background-size:97px 97px, 173px 173px;
        background-position:10px 20px, 55px 80px;
        animation: drift 28s linear infinite;
    }

    @keyframes drift { to { background-position:500px 300px, -300px 500px; } }
    @keyframes pulse { 0%,100%{transform:scale(1);opacity:.8} 50%{transform:scale(1.05);opacity:1} }
    @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
    @keyframes scan { from{transform:translateX(-110%)} to{transform:translateX(110%)} }
    @keyframes shimmer { 0%{background-position:-600px 0} 100%{background-position:600px 0} }
    @keyframes spin { to{transform:rotate(360deg)} }

    .nova-hero {
        min-height:360px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        text-align:center;
        position:relative;
        margin:20px 0 15px;
        border:1px solid var(--line);
        border-radius:35px;
        background:linear-gradient(145deg,rgba(18,25,55,.82),rgba(5,8,20,.68));
        box-shadow:0 0 70px rgba(108,135,255,.13), inset 0 0 70px rgba(255,255,255,.025);
        overflow:hidden;
    }

    .nova-hero:after {
        content:"";
        position:absolute;
        width:70%;
        height:2px;
        background:linear-gradient(90deg,transparent,#a9bbff,transparent);
        animation:scan 5s ease-in-out infinite;
    }

    .nova-system {
        font-family:'Orbitron';
        letter-spacing:6px;
        color:#9daeff;
        font-size:12px;
        margin-bottom:24px;
    }

    .nova-name {
        font-family:'Cinzel';
        font-size:clamp(58px,9vw,125px);
        letter-spacing:18px;
        font-weight:700;
        line-height:1;
        text-shadow:0 0 25px rgba(160,180,255,.45),0 0 70px rgba(160,150,255,.2);
        animation:pulse 4s ease-in-out infinite;
    }

    .nova-codename {
        margin-top:20px;
        font-family:'Orbitron';
        letter-spacing:14px;
        color:#c9d2ff;
        font-size:15px;
        animation:float 4s ease-in-out infinite;
    }

    .section-head {
        text-align:center;
        padding:25px 0 20px;
    }
    .kicker {
        font-family:'Orbitron';
        letter-spacing:5px;
        font-size:11px;
        color:#899aff;
    }
    .section-title {
        font-family:'Cinzel';
        font-size:42px;
        font-weight:700;
        letter-spacing:3px;
        margin:8px 0;
        text-shadow:0 0 25px rgba(155,175,255,.25);
    }
    .section-sub { color:var(--muted); font-size:14px; }

    .glass-card {
        min-height:170px;
        padding:28px;
        border:1px solid var(--line);
        border-radius:24px;
        background:linear-gradient(145deg,rgba(20,28,60,.74),rgba(8,11,27,.74));
        box-shadow:0 15px 50px rgba(0,0,0,.25);
        transition:.35s ease;
        margin-bottom:20px;
        position:relative;
        overflow:hidden;
    }
    .glass-card:hover {
        transform:translateY(-7px) scale(1.01);
        border-color:rgba(190,205,255,.5);
        box-shadow:0 20px 65px rgba(82,110,255,.18);
    }
    .glass-card:before {
        content:"";
        position:absolute;
        top:0;left:-100%;
        width:70%;height:1px;
        background:#dbe4ff;
        animation:scan 6s linear infinite;
    }
    .card-icon { font-size:28px; animation:float 3s ease-in-out infinite; }
    .card-title {
        font-family:'Orbitron';
        letter-spacing:2px;
        margin:12px 0 8px;
        font-size:16px;
    }
    .card-body { color:#aeb8d6; line-height:1.7; font-size:14px; }

    .mission-card, .memory-card, .review-card, .diary-card, .achievement-card {
        padding:30px;
        border-radius:28px;
        border:1px solid rgba(164,184,255,.25);
        background:rgba(10,15,34,.82);
        box-shadow:0 0 55px rgba(94,119,255,.09);
        margin:18px 0;
    }

    .mission-number {
        font-family:'Orbitron';
        font-size:12px;
        letter-spacing:4px;
        color:#98a9ff;
    }
    .mission-question {
        font-family:'Cinzel';
        font-size:26px;
        margin:10px 0 20px;
    }

    .big-reveal {
        text-align:center;
        padding:55px 20px;
        border-radius:32px;
        background:radial-gradient(circle,rgba(92,115,255,.22),transparent 60%),rgba(10,14,31,.9);
        border:1px solid rgba(205,215,255,.35);
        box-shadow:0 0 100px rgba(110,130,255,.22);
        animation:pulse 3s infinite;
    }
    .big-reveal h1 {
        font-family:'Cinzel';
        font-size:58px;
        letter-spacing:7px;
    }

    .secret {
        padding:26px;
        border:1px dashed rgba(190,200,255,.4);
        border-radius:24px;
        background:rgba(20,22,48,.72);
        text-align:center;
    }

    .star {
        display:inline-block;
        margin:10px;
        font-size:30px;
        animation:pulse 2s infinite;
    }

    .status-line {
        height:10px;
        background:rgba(255,255,255,.08);
        border-radius:99px;
        overflow:hidden;
        margin:8px 0 18px;
    }
    .status-fill {
        height:100%;
        background:linear-gradient(90deg,#7d8fff,#d4b7ff);
        border-radius:99px;
        box-shadow:0 0 18px rgba(150,160,255,.55);
    }

    .streamlit-expanderHeader, label, .stMarkdown, p, div {
        color:inherit;
    }

    div.stButton > button {
        border:1px solid rgba(168,184,255,.28);
        border-radius:15px;
        background:linear-gradient(135deg,rgba(35,45,92,.9),rgba(13,18,40,.95));
        color:#eef2ff;
        font-family:'Orbitron';
        letter-spacing:1px;
        transition:.3s ease;
        min-height:48px;
        box-shadow:0 5px 20px rgba(0,0,0,.18);
    }
    div.stButton > button:hover {
        border-color:#cdd7ff;
        transform:translateY(-3px);
        box-shadow:0 0 28px rgba(130,150,255,.28);
    }

    .footer {
        text-align:center;
        color:#707b9e;
        font-family:'Orbitron';
        font-size:10px;
        letter-spacing:4px;
        padding:55px 0 25px;
    }

    [data-testid="stSidebar"] { background:#060916; }
    
    .runaway-wrap{min-height:180px;position:relative;text-align:center;}
    .runaway-hint{font-family:'Orbitron';font-size:10px;letter-spacing:3px;color:#8f9dca;margin:20px 0;}
    .runaway-reveal{position:fixed;left:50%;top:62%;transform:translate(-50%,-50%);z-index:99999;display:inline-flex;align-items:center;justify-content:center;min-height:54px;padding:0 24px;border-radius:16px;border:1px solid rgba(255,220,150,.65);background:linear-gradient(135deg,rgba(150,82,30,.96),rgba(68,25,25,.98));color:#fff;text-decoration:none;font-family:'Orbitron';font-size:12px;letter-spacing:1px;box-shadow:0 0 30px rgba(255,170,70,.28),0 12px 30px rgba(0,0,0,.35);transition:left .18s ease,top .18s ease,transform .18s ease;}
    .runaway-reveal:hover{color:#fff;transform:translate(-50%,-50%) scale(1.04);}
    .runaway-reveal.runaway-active{animation:float .9s ease-in-out infinite;}
    @media(max-width:520px){.runaway-reveal{max-width:calc(100vw - 36px);text-align:center;font-size:10px;padding:0 14px;}}
    .stone-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin:22px 0}
    .infinity-stone{
        min-height:115px;padding:12px 6px;border-radius:20px;
        border:1px solid rgba(170,185,255,.16);background:rgba(8,12,28,.82);
        text-align:center;font-family:'Orbitron';font-size:9px;letter-spacing:1px;color:#68728f;
        transition:.35s ease;
    }
    .infinity-stone .gem{
        width:46px;height:46px;margin:0 auto 8px;border-radius:50%;
        background:#20263a;border:2px solid #3a425e;box-shadow:inset 0 0 16px rgba(0,0,0,.55);
    }
    .infinity-stone.unlocked{color:#eef2ff;border-color:rgba(225,230,255,.45);box-shadow:0 0 28px rgba(130,150,255,.18)}
    .infinity-stone.unlocked .gem{border-color:white;box-shadow:0 0 12px rgba(255,255,255,.55),0 0 30px currentColor}
    .stone-space .gem{background:radial-gradient(circle at 35% 28%,#e9fbff,#45adff 55%,#173fb0)}
    .stone-time .gem{background:radial-gradient(circle at 35% 28%,#efffdf,#62d76c 55%,#176c31)}
    .stone-reality .gem{background:radial-gradient(circle at 35% 28%,#ffe6e6,#ff4e5b 55%,#8d1825)}
    .stone-power .gem{background:radial-gradient(circle at 35% 28%,#f0ddff,#9b5cff 55%,#4e1b9c)}
    .stone-mind .gem{background:radial-gradient(circle at 35% 28%,#fffbd0,#ffd63b 55%,#b37a00)}
    .stone-soul .gem{background:radial-gradient(circle at 35% 28%,#ffe6ce,#ff9d45 55%,#a84c17)}
    @media(max-width:850px){
        .solar-system{height:540px}
        .stone-grid{grid-template-columns:repeat(3,1fr)}
        .orbit-c{width:410px;height:410px}
    }
    @media(max-width:520px){
        .solar-system{height:500px}
        .orbit-b{width:285px;height:285px}.orbit-c{width:390px;height:390px}
    }

    
    .archive-nav {
        display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:18px 0 30px;
    }
    .archive-nav-note {
        text-align:center;font-family:'Orbitron';letter-spacing:3px;color:#8f9dca;font-size:11px;margin:0 0 12px;
    }
    @media(max-width:850px){.archive-nav{grid-template-columns:repeat(2,1fr)}}
    @media(max-width:520px){.archive-nav{grid-template-columns:1fr}}

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HERO
# ============================================================
st.markdown(
    """
    <div class="nova-hero">
        <div class="nova-system">✦ NOVA ARCHIVE // PERSONAL FILE ✦</div>
        <div class="nova-name">FARHEEN</div>
        <div class="nova-codename">N O V A</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# ============================================================
# ============================================================
# ARCHIVE NAVIGATION — CLEAN HOME, NO SOLAR SYSTEM
# ============================================================
st.markdown(
    """
    <div class="archive-nav-note">◉ NOVA ARCHIVE // CHOOSE A FILE</div>
    """,
    unsafe_allow_html=True,
)
nav = [
    ("🌌 HOME", "🌌 HOME"), ("🪐 ABOUT", "🪐 ABOUT"),
    ("😂 FUN FACTS", "😂 FUN FACTS"), ("📸 MOMENTS", "📸 MOMENTS"),
    ("🐾 CATS", "🐾 CATS"), ("🧠 QUIZ", "🧠 QUIZ"),
    ("🔮 FUTURE", "🔮 FUTURE"), ("🎂 BIRTHDAY", "🎂 BIRTHDAY"),
]
cols = st.columns(4)
for i, (label, target) in enumerate(nav):
    with cols[i % 4]:
        nav_button(label, target)


# ============================================================
# ORIGIN STORY // CHILDHOOD + FAMILY
# ============================================================
if st.session_state.page == "🧸 ORIGIN":
    award("ORIGIN DISCOVERED")
    section_title(
        "MEMORY ARCHIVE // 01",
        "THE BEGINNING OF NOVA",
        "One real childhood memory. One little star. The story starts here."
    )

    st.markdown("""
    <div class="glass-card">
        <div class="card-icon">🧸</div>
        <div class="card-title">THE FIRST SIGHTING</div>
        <div class="card-body">
            Before the NOVA archive, before all the memories and moments,
            there was simply this little chapter of her story. ✦
        </div>
    </div>
    """, unsafe_allow_html=True)

    # The supplied childhood photo is the single genuine archive image.
    childhood_candidates = [
        "/mnt/data/1ofF.jpeg",
        "/mnt/data/files/1ofF.jpeg",
    ]
    childhood_path = next((p for p in childhood_candidates if Path(p).exists()), None)

    if childhood_path:
        st.image(
            childhood_path,
            caption="NOVA // ORIGIN MEMORY",
            use_container_width=True
        )
    else:
        st.info("🧸 Add the childhood photo file beside the app to display this memory.")

    st.markdown("""
    <div class="glass-card">
        <div class="card-title">FAMILY FILE</div>
        <div class="card-body">
            <b>FATHER</b><br>
            Mahaboob Sheriff
            <br><br>
            <b>MOTHER</b><br>
            Salma
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <div class="card-title">ORIGIN NOTE</div>
        <div class="card-body">
            Every universe has a beginning. 🌌<br><br>
            This is the first memory in the NOVA archive.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🌌 RETURN TO THE ARCHIVE", use_container_width=True):
        st.session_state.page = "🌌 HOME"
        st.query_params.clear()
        st.rerun()


# ============================================================
# CAT ARCHIVE // NOVA'S CATS
# ============================================================
if st.session_state.page == "🐾 CATS":
    award("CAT ARCHIVIST")
    section_title(
        "COMPANION ARCHIVE // 02",
        "NOVA'S CAT ARCHIVE",
        "Seven cats. No official names in the archive. Unlimited personality. 🐾"
    )

    st.markdown(
        """
        <div class="glass-card">
            <div class="card-icon">🐾</div>
            <div class="card-title">THE CAT CREW</div>
            <div class="card-body">
                No need for official names here — every cat gets its own little
                archive file. These are real moments from NOVA's cat collection. ✦
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    base_dir = Path(__file__).resolve().parent
    cat_files = [
        (base_dir / "assets" / "cat_01.jpeg", "CAT FILE 01", "COZY MODE ACTIVATED 💤"),
        (base_dir / "assets" / "cat_02.jpeg", "CAT FILE 02", "ROOFTOP SUPERVISOR 🌇🐾"),
    ]

    c1, c2 = st.columns(2)

    for idx, (cat_path, title, mood) in enumerate(cat_files):
        with (c1 if idx == 0 else c2):
            if cat_path.exists():
                st.image(
                    str(cat_path),
                    caption=f"{title} ✦ {mood}",
                    use_container_width=True,
                )
            else:
                st.warning(f"🐾 {title} image not found.")

            st.markdown(
                f"""
                <div class="glass-card" style="min-height:auto;text-align:center;">
                    <div class="card-title">{title}</div>
                    <div class="card-body">{mood}<br><br>
                    <span style="color:#899aff;">NOVA CAT ARCHIVE // MEMORY STORED ✦</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="big-reveal" style="padding:35px 20px;">
            <div class="kicker">🐱 CAT CREW STATUS</div>
            <h1 style="font-size:42px;">CHAOS: ONLINE</h1>
            <p style="color:#aeb8d6;">
                The archive confirms: NOVA's cat department is fully operational. 😂🐾
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    if st.button("🌌 RETURN TO THE ARCHIVE", use_container_width=True):
        st.session_state.page = "🌌 HOME"
        st.query_params.clear()
        st.rerun()

# ============================================================
# HOME
# ============================================================
if st.session_state.page == "🌌 HOME":
    award("FIRST DISCOVERY")
    section_title("NOVA SYSTEM // ONLINE", "WELCOME TO THE ARCHIVE", "A birthday universe built one memory at a time.")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("✦ 06 • 11 • 2009", use_container_width=True):
            st.session_state.home_card = "date"
    with c2:
        if st.button("✦ NOVA", use_container_width=True):
            st.session_state.home_card = "nova"
    with c3:
        if st.button("✦ STATUS", use_container_width=True):
            st.session_state.home_card = "status"

    if st.session_state.home_card == "date":
        card("SPECIAL DATE", "06 November 2009 — the date this particular NOVA entered the universe. ✦", "🎂")
    elif st.session_state.home_card == "nova":
        card("WHY NOVA?", "A nova is a star that suddenly becomes dramatically brighter. A pretty fitting codename for someone who can light up a room. ✦", "🌟")
    elif st.session_state.home_card == "status":
        st.markdown('<div class="glass-card"><div class="card-title">NOVA STATUS</div>', unsafe_allow_html=True)
        for label, pct in [("CHAOS", 91), ("EXTROVERT ENERGY", 94), ("NIGHT OWL", 98), ("MATH POWER", 97)]:
            st.write(f"**{label} — {pct}%**")
            st.markdown(f'<div class="status-line"><div class="status-fill" style="width:{pct}%"></div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card"><div class="card-title">MISSION CONTROL</div><div class="card-body">Explore the archive, discover hidden memories, collect achievements, complete every activity, and unlock the final surprise.</div></div>', unsafe_allow_html=True)




# ============================================================
# ABOUT
# ============================================================
elif st.session_state.page == "🪐 ABOUT":
    award("ARCHIVE EXPLORER")
    section_title("PERSONAL FILE // 01", "ABOUT NOVA", "A few coordinates from the person behind the codename.")

    a, b = st.columns(2)
    with a:
        card("IDENTITY", "<b>FARHEEN</b><br>Codename: <b>N O V A</b><br>Birthday: <b>06 • 11 • 2009</b><br>Birth Time: <b>10:30 AM</b>", "🌌")
        card("THE SPECS", "Oval-shaped glasses — a tiny detail, but one that is unmistakably NOVA.", "👓")
    with b:
        card("ENERGY PROFILE", "Cool with close people, kind character, and strong extrovert energy.", "⚡")
        card("NIGHT MODE", "Officially operating on suspiciously high levels of night-owl energy. 🌙", "🌙")

# ============================================================
# FUN FACTS
# ============================================================
elif st.session_state.page == "😂 FUN FACTS":
    award("ARCHIVE EXPLORER")
    section_title("PERSONAL FILE // 02", "NOVA FILES", "Tap a file. Discover a fact.")

    facts = [
        ("🥻", "THE SERI CODE", "The legendary 🥻 emoji has one special translation in NOVA language: “seri”."),
        ("🌙", "NIGHT OWL", "Sleep schedule: classified. Night mode: permanently active."),
        ("😴", "CLASSROOM STEALTH", "Can apparently enter sleep mode during class without the universe noticing."),
        ("🧮", "MATH POWER", "Mathematics is firmly inside the NOVA skill tree."),
        ("📚", "ACADEMIC MODE", "450+ territory. The archive acknowledges the academic power."),
        ("🗣️", "EXTROVERT ENERGY", "Social battery appears to have its own independent power source."),
        ("👓", "SIGNATURE SPECS", "Oval frames: officially part of the NOVA visual identity."),
        ("✨", "UNKNOWN VARIABLE", "There are probably more secrets. The archive refuses to confirm."),
    ]

    for i in range(0, len(facts), 2):
        c1, c2 = st.columns(2)
        for col, fact in zip((c1, c2), facts[i:i+2]):
            with col:
                if st.button(f"{fact[0]}  {fact[1]}", key=f"fact_{i}_{fact[1]}", use_container_width=True):
                    award("FIRST DISCOVERY")
                    card(fact[1], fact[2], fact[0])

    # Secret star
    st.markdown('<div class="secret"><span class="star">✦</span> Somewhere in this archive, one tiny secret is waiting...</div>', unsafe_allow_html=True)
    if st.button("⭐ TOUCH THE HIDDEN STAR", key="hidden_star", use_container_width=True):
        st.session_state.secret_found = True
        award("SECRET FOUND")
        st.balloons()
        st.success("⚠ SECRET AREA DISCOVERED — You found the hidden star!")

    if st.session_state.secret_found:
        card("CLASSIFIED MESSAGE", "You actually found it. 😭✨ The archive officially recognizes you as a NOVA explorer.", "🔐")

# ============================================================
# MOMENTS
# ============================================================
elif st.session_state.page == "📸 MOMENTS":
    award("MEMORY MAKER")
    section_title("MEMORY VAULT // 03", "CAPTURE THE MOMENT", "Take as many photos as you want, then turn them into one keepsake.")

    photo = st.camera_input("📸 CAPTURE A MOMENT")

    if photo is not None:
        st.session_state.captured_photos.append(photo.getvalue())
        st.success(f"✨ MOMENT CAPTURED — {len(st.session_state.captured_photos)} photo(s) in the vault.")
        st.image(photo, caption="NOVA MEMORY ✦", use_container_width=True)

    count = len(st.session_state.captured_photos)
    if count:
        st.markdown(f'<div class="memory-card"><div class="card-title">MEMORY VAULT // {count} CAPTURE(S)</div><div class="card-body">Keep capturing more moments, or generate the final collage when you are ready.</div></div>', unsafe_allow_html=True)

        if st.button("🖼️ CREATE MY MEMORY COLLAGE", use_container_width=True):
            collage = make_collage(st.session_state.captured_photos)
            if collage:
                buf = io.BytesIO()
                collage.save(buf, format="PNG")
                st.session_state["collage_bytes"] = buf.getvalue()
                award("MEMORY MAKER")
                st.success("🌌 MEMORY COLLAGE GENERATED!")
                st.image(collage, caption="✦ NOVA MEMORY VAULT ✦", use_container_width=True)
                st.download_button(
                    "💾 SAVE MY COLLAGE",
                    data=st.session_state["collage_bytes"],
                    file_name="NOVA_MEMORY_VAULT.png",
                    mime="image/png",
                    use_container_width=True,
                )
    else:
        st.info("📷 CAMERA STANDBY — Capture your first memory above.")

# ============================================================
# QUIZ
# ============================================================
elif st.session_state.page == "🧠 QUIZ":
    award("QUIZ EXPLORER")
    section_title("NOVA ANALYSIS // 04", "HOW WELL DO YOU KNOW YOURSELF?", "Choose what feels most like you. The archive will analyse the result.")

    # The five questions are fixed, while the answer choices are shuffled once
    # per session so the correct answer is not always option A.
    quiz = [
        (
            "Q1",
            "How many cats do you have?",
            ["🐱 7", "🐱 5", "🐱 9", "🐱 3"],
            "🐱 7",
        ),
        (
            "Q2",
            "Solve: x² − 17x + 66 = 0. What are the values of x?",
            ["🔢 6 and 11", "🔢 7 and 10", "🔢 5 and 12", "🔢 8 and 9"],
            "🔢 6 and 11",
        ),
        (
            "Q3",
            "Describe yourself with one thing about your character.",
            ["🌙 Night owl", "☀️ Early bird", "📚 Bookworm", "⚡ Always energetic"],
            "🌙 Night owl",
        ),
        (
            "Q4",
            "Name the specific region on a pollen grain where sporopollenin is absent, allowing the pollen tube to emerge.",
            ["🌱 Germ pore", "🌸 Stigma", "🌿 Anther", "🧬 Ovule"],
            "🌱 Germ pore",
        ),
        (
            "Q5",
            "What is the probability of finding a person who is born on November 6, wears spectacles, is a topper, has an extroverted personality, and is the one and only person who matches all these qualities?",
            ["1", "0", "1/2", "1/100"],
            "1",
        ),
    ]

    if st.session_state.quiz_options is None:
        st.session_state.quiz_options = {}
        for code, q, opts, correct in quiz:
            shuffled = opts.copy()
            random.shuffle(shuffled)
            st.session_state.quiz_options[code] = shuffled

    answers = {}
    for code, q, opts, correct in quiz:
        answers[code] = st.radio(
            q,
            st.session_state.quiz_options[code],
            key=f"quiz_{code}",
        )

    if st.button("🧠 RUN NOVA ANALYSIS", use_container_width=True):
        score = sum(answers[k] == correct for k, _, _, correct in quiz)
        st.success(f"ANALYSIS COMPLETE — {score}/{len(quiz)} correct.")

        if answers["Q5"] == "1":
            card(
                "Q5 // ARCHIVE EXPLANATION",
                "The answer is 1 because the question defines the target as the one and only person who matches every listed quality. In this archive, that one-and-only piece is YOU. ✦",
                "✨",
            )

        if score == len(quiz):
            award("QUIZ MASTER")
            st.balloons()
            card(
                "NOVA ANALYSIS: PERFECT",
                "The archive has determined that you know the NOVA system suspiciously well. 😂✨",
                "🏆",
            )
        else:
            card(
                "NOVA ANALYSIS",
                "The archive recommends another expedition through the files.",
                "🔭",
            )

# ============================================================
# FUTURE
# ============================================================
elif st.session_state.page == "🔮 FUTURE":
    award("TIME TRAVELER")
    section_title("TEMPORAL ARCHIVE // 05", "FUTURE CAPSULE", "Write something that future NOVA can discover later.")

    future = st.text_area(
        "💭 Dear future me...",
        placeholder="Where do you think you'll be in 5 years? What do you want to achieve? What should you never forget?",
        height=220,
    )
    if st.button("🔮 SEAL THE TIME CAPSULE", use_container_width=True):
        if future.strip():
            st.session_state.capsule_saved = True
            award("TIME TRAVELER")
            st.success("🔐 TIME CAPSULE SEALED.")
        else:
            st.warning("Write at least a little message before sealing the capsule.")

    if st.session_state.capsule_saved:
        st.markdown(
            '<div class="diary-card"><div class="card-title">NOVA // TIME CAPSULE SEALED</div><div class="card-body">This message has been recorded for the future. ✦<br><br><i>Your future self is going to have fun reading this.</i></div></div>',
            unsafe_allow_html=True,
        )

    if st.button("🛰️ RECEIVE MESSAGE FROM THE FUTURE", use_container_width=True):
        st.session_state.future_message_seen = True
        award("FUTURE TRANSMISSION")
        st.session_state.page = "🔮 FUTURE"
        st.rerun()

    if st.session_state.future_message_seen:
        st.markdown(
            """
            <div class="big-reveal">
                <div class="kicker">📡 INCOMING TRANSMISSION...</div>
                <h1>FROM THE FUTURE</h1>
                <p style="color:#b7c1df;font-size:17px;">
                “Keep going. Keep laughing. Keep being the person who makes ordinary days feel memorable.”
                </p>
                <p style="color:#8490b5;">TRANSMISSION COMPLETE ✦</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    section_title("AUDIO ARCHIVE", "BIRTHDAY SOUNDTRACK", "Record the songs that became part of this day.")
    song = st.text_input("🎧 Add a song", placeholder="Song title — Artist")
    if st.button("➕ ADD TO SOUNDTRACK", use_container_width=True):
        if song.strip():
            st.session_state.soundtrack.append(song.strip())
    if st.session_state.soundtrack:
        for i, s in enumerate(st.session_state.soundtrack, 1):
            st.markdown(f'<div class="glass-card"><div class="card-title">TRACK {i:02d}</div><div class="card-body">🎧 {s}</div></div>', unsafe_allow_html=True)

# ============================================================
# BIRTHDAY — FINAL REVEAL
# ============================================================
elif st.session_state.page == "🎂 BIRTHDAY":
    section_title(
        "CLASSIFIED // FINAL PROTOCOL",
        "THE BIRTHDAY REVEAL",
        "The surprise is waiting. But first, complete the entire archive."
    )

    pct, completed, total = activity_percent()

    st.markdown(
        f"""
        <div class="mission-card" style="text-align:center;">
            <div class="mission-number">FINAL GATE // ACTIVITY REPORT</div>
            <div class="mission-question" style="font-size:30px;">{pct}% COMPLETE</div>
            <div style="color:#aeb8d6;">
                {completed}/{total} archive objectives completed.
            </div>
            <div style="margin-top:15px;height:10px;background:rgba(255,255,255,.08);
                        border-radius:99px;overflow:hidden;">
                <div style="height:100%;width:{pct}%;
                            background:linear-gradient(90deg,#7d8fff,#d4b7ff);
                            border-radius:99px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    gift = st.text_area(
        "💌 FINAL BIRTHDAY MESSAGE",
        value="Happy Birthday, NOVA! ✨ Keep shining, keep laughing, and keep collecting beautiful memories.",
        height=150,
        key="final_gift"
    )

    if pct < 100:
        st.markdown(
            """
            <div class="glass-card" style="text-align:center;">
                <div class="card-title">😈 CATCH ME IF YOU CAN</div>
                <div class="card-body">
                    The final reveal button refuses to cooperate until the Activity Report reaches 100%.
                    Move your cursor near it and... watch it escape. 😂
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        components.html(
            """
            <style>
                html, body { margin:0; padding:0; background:transparent; overflow:hidden; }
                #runawayArea {
                    position:relative;
                    width:100%;
                    height:180px;
                    overflow:hidden;
                }
                #runawayReveal {
                    position:absolute;
                    left:50%;
                    top:50%;
                    transform:translate(-50%,-50%);
                    display:inline-flex;
                    align-items:center;
                    justify-content:center;
                    padding:15px 22px;
                    border:1px solid rgba(180,195,255,.45);
                    border-radius:16px;
                    background:linear-gradient(135deg,rgba(35,45,92,.98),rgba(13,18,40,.98));
                    color:#eef2ff;
                    text-decoration:none;
                    font-family:Arial,sans-serif;
                    font-size:14px;
                    font-weight:700;
                    letter-spacing:1px;
                    box-shadow:0 0 25px rgba(130,150,255,.2);
                    white-space:nowrap;
                    cursor:pointer;
                    transition:left .16s ease, top .16s ease;
                    user-select:none;
                    -webkit-tap-highlight-color:transparent;
                }
            </style>

            <div id="runawayArea">
                <a id="runawayReveal" href="?nova_reveal=1">
                    🎉 OPEN THE FINAL BIRTHDAY REVEAL
                </a>
            </div>

            <script>
            (() => {
                const area = document.getElementById("runawayArea");
                const btn = document.getElementById("runawayReveal");
                if (!area || !btn) return;

                const move = () => {
                    const ar = area.getBoundingClientRect();
                    const br = btn.getBoundingClientRect();
                    const pad = 8;

                    const maxX = Math.max(pad, ar.width - br.width - pad);
                    const maxY = Math.max(pad, ar.height - br.height - pad);

                    const x = pad + Math.random() * Math.max(1, maxX - pad);
                    const y = pad + Math.random() * Math.max(1, maxY - pad);

                    btn.style.left = x + "px";
                    btn.style.top = y + "px";
                    btn.style.transform = "none";
                };

                const near = (px, py) => {
                    const r = btn.getBoundingClientRect();
                    const cx = r.left + r.width / 2;
                    const cy = r.top + r.height / 2;
                    return Math.hypot(px - cx, py - cy) < 120;
                };

                area.addEventListener("pointermove", (e) => {
                    if (near(e.clientX, e.clientY)) move();
                }, {passive:true});

                btn.addEventListener("pointerdown", (e) => {
                    e.preventDefault();
                    move();
                }, {passive:false});

                move();
            })();
            </script>
            """,
            height=200,
            scrolling=False,
        )

    else:
        st.success("🔓 ALL ARCHIVE OBJECTIVES COMPLETE — THE BUTTON HAS STOPPED RUNNING!")

        st.markdown(
            """
            <div style="text-align:center;margin:18px 0 10px;">
                <div style="font-family:Orbitron,Arial,sans-serif;letter-spacing:3px;color:#aebeff;font-size:12px;">
                    FINAL GATE UNLOCKED
                </div>
                <div style="color:#c8d0e8;margin-top:7px;">The button is stable now. Start the NOVA origin cinematic.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🎂 OPEN THE BIRTHDAY REVEAL 🎂", key="open_nova_cinematic", use_container_width=True):
            st.session_state.final_reveal_requested = True
            st.query_params.clear()
            st.rerun()

    if st.session_state.final_reveal_requested and pct >= 100:
        award("BIRTHDAY COMPLETE")
        st.balloons()

        # ------------------------------------------------------------
        # CINEMATIC NOVA ORIGIN STORY
        # Planet -> collision -> cosmic rebirth -> 06 Nov 2009
        # ------------------------------------------------------------
        components.html(
            r"""
            <style>
                * { box-sizing:border-box; }
                html,body { margin:0; padding:0; background:#02030a; overflow:hidden; }
                body { font-family:Arial,sans-serif; min-height:100%; }

                .nova-film {
                    position:relative;
                    width:100%;
                    height:700px;
                    min-height:700px;
                    overflow:hidden;
                    border-radius:26px;
                    background:
                        radial-gradient(circle at 50% 48%, rgba(88,105,255,.12), transparent 22%),
                        radial-gradient(circle at 50% 50%, rgba(255,255,255,.035), transparent 45%),
                        #02030a;
                    border:1px solid rgba(170,185,255,.28);
                    box-shadow:0 0 55px rgba(92,112,255,.20), inset 0 0 80px rgba(0,0,0,.85);
                }

                .stars, .stars2, .stars3 {
                    position:absolute; inset:0;
                    background-repeat:repeat;
                    pointer-events:none;
                }
                .stars {
                    opacity:.8;
                    background-image:
                        radial-gradient(circle, #fff 0 1px, transparent 1.5px),
                        radial-gradient(circle, #b8c8ff 0 1px, transparent 1.5px);
                    background-size:83px 91px, 137px 121px;
                    background-position:11px 17px, 50px 70px;
                    animation: drift 20s linear infinite;
                }
                .stars2 {
                    opacity:.5;
                    background-image:radial-gradient(circle, #fff 0 1px, transparent 1.5px);
                    background-size:211px 173px;
                    animation: drift 32s linear infinite reverse;
                }
                .stars3 {
                    opacity:.3;
                    background-image:radial-gradient(circle, #d8c8ff 0 1.2px, transparent 1.7px);
                    background-size:53px 149px;
                    animation: drift 14s linear infinite;
                }

                .film-vignette {
                    position:absolute; inset:0; pointer-events:none;
                    background:radial-gradient(circle, transparent 42%, rgba(0,0,0,.75) 100%);
                }

                .scene-title {
                    position:absolute; top:42px; left:0; width:100%;
                    text-align:center; z-index:20;
                    color:#dfe6ff; font-size:12px; letter-spacing:5px;
                    opacity:0; animation:titleIn 2s ease forwards .3s;
                }
                .scene-title b { color:#fff; }

                .planet {
                    position:absolute;
                    width:190px; height:190px;
                    left:calc(50% - 95px); top:calc(50% - 95px);
                    border-radius:50%; z-index:7;
                    background:
                        radial-gradient(circle at 34% 28%, #e5eaff 0 3%, #a6b5ff 9%, transparent 25%),
                        radial-gradient(circle at 63% 62%, #5d72d8 0 14%, #253474 42%, #0a102c 76%, #02030a 100%);
                    box-shadow:
                        -28px -18px 45px rgba(135,160,255,.35),
                        20px 25px 45px rgba(0,0,0,.9),
                        0 0 45px rgba(105,130,255,.18);
                    opacity:0;
                    transform:scale(.15);
                    animation:planetAppear 4s cubic-bezier(.16,.8,.2,1) forwards 2s,
                              planetPulse 3s ease-in-out infinite 6s;
                }
                .planet:before {
                    content:""; position:absolute; inset:-12px; border-radius:50%;
                    border:1px solid rgba(166,190,255,.35);
                    box-shadow:0 0 25px rgba(112,140,255,.22);
                }
                .planet-name {
                    position:absolute; top:calc(50% + 112px); width:100%;
                    text-align:center; z-index:9; color:#e7ecff;
                    font-family:Georgia,serif; font-size:20px; letter-spacing:8px;
                    opacity:0; animation:fadeIn 2s ease forwards 4.8s;
                }

                .intruder {
                    position:absolute; width:86px; height:86px; border-radius:50%;
                    left:-120px; top:calc(50% - 43px); z-index:10;
                    background:radial-gradient(circle at 30% 25%, #fff1df, #ff9f63 22%, #9d3657 58%, #25091f 100%);
                    box-shadow:0 0 35px #ff8a66, 0 0 75px rgba(255,95,80,.45);
                    opacity:0;
                    animation:intruderMove 3.1s cubic-bezier(.65,.02,.9,.35) forwards 6.1s;
                }
                .trail {
                    position:absolute; width:260px; height:18px; left:-310px;
                    top:calc(50% - 9px); z-index:8; border-radius:50%;
                    background:linear-gradient(90deg, transparent, rgba(255,145,105,.8), transparent);
                    filter:blur(5px); opacity:0;
                    animation:trailMove 3.1s linear forwards 6.1s;
                }

                .impact {
                    position:absolute; width:40px; height:40px; border-radius:50%;
                    left:calc(50% - 20px); top:calc(50% - 20px);
                    z-index:15; background:white; opacity:0; transform:scale(.1);
                    box-shadow:0 0 35px #fff, 0 0 100px #9eb3ff, 0 0 180px #8c5cff;
                    animation:impact 2.1s ease forwards 9.05s;
                }
                .shock {
                    position:absolute; width:80px; height:80px; border-radius:50%;
                    left:calc(50% - 40px); top:calc(50% - 40px);
                    border:2px solid rgba(230,240,255,.85); z-index:14;
                    opacity:0; transform:scale(.1);
                    animation:shock 2.4s ease-out forwards 9.15s;
                }

                .flash {
                    position:absolute; inset:0; z-index:16;
                    background:white; opacity:0; pointer-events:none;
                    animation:flash 1.7s ease forwards 9.25s;
                }

                .rebirth-core {
                    position:absolute; width:30px; height:30px; border-radius:50%;
                    left:calc(50% - 15px); top:calc(50% - 15px);
                    background:#fff; z-index:18; opacity:0; transform:scale(.1);
                    box-shadow:0 0 35px white, 0 0 100px #b9c7ff, 0 0 180px #9d75ff;
                    animation:rebirth 4s ease-out forwards 10.2s;
                }

                .nova-born {
                    position:absolute; inset:0; z-index:25;
                    display:flex; flex-direction:column; align-items:center; justify-content:center;
                    text-align:center; opacity:0; transform:scale(.92);
                    animation:born 3.5s ease forwards 12.4s;
                    pointer-events:none;
                }
                .nova-date {
                    font-family:Arial,sans-serif; color:#aebeff;
                    font-size:15px; letter-spacing:8px; margin-bottom:18px;
                }
                .nova-born h1 {
                    margin:0; color:white; font-family:Georgia,serif;
                    font-size:clamp(42px,7vw,88px); letter-spacing:8px;
                    text-shadow:0 0 18px rgba(188,205,255,.7), 0 0 55px rgba(116,137,255,.55);
                }
                .nova-born p {
                    margin:18px 0 0; color:#c9d2ee; font-size:14px; letter-spacing:5px;
                }
                .nova-credit {
                    position:absolute; bottom:30px; left:0; width:100%; text-align:center;
                    z-index:30; color:rgba(205,214,240,.55); font-size:10px;
                    letter-spacing:3px; opacity:0; animation:fadeIn 2s ease forwards 15s;
                }

                @keyframes drift { from{transform:translateY(0)} to{transform:translateY(30px)} }
                @keyframes titleIn { to{opacity:1} }
                @keyframes fadeIn { to{opacity:1} }
                @keyframes planetAppear {
                    0%{opacity:0;transform:scale(.15) rotate(-25deg)}
                    55%{opacity:1;transform:scale(1.08) rotate(8deg)}
                    100%{opacity:1;transform:scale(1) rotate(0)}
                }
                @keyframes planetPulse {
                    0%,100%{filter:brightness(1)} 50%{filter:brightness(1.18)}
                }
                @keyframes intruderMove {
                    0%{opacity:0;transform:translateX(0) rotate(0)}
                    8%{opacity:1}
                    100%{opacity:1;transform:translateX(calc(50vw + 120px)) rotate(720deg)}
                }
                @keyframes trailMove {
                    0%{opacity:0;transform:translateX(0)}
                    10%{opacity:1}
                    100%{opacity:0;transform:translateX(calc(50vw + 120px))}
                }
                @keyframes impact {
                    0%{opacity:0;transform:scale(.1)}
                    25%{opacity:1;transform:scale(1.5)}
                    100%{opacity:0;transform:scale(20)}
                }
                @keyframes shock {
                    0%{opacity:0;transform:scale(.1)}
                    15%{opacity:1}
                    100%{opacity:0;transform:scale(15)}
                }
                @keyframes flash {
                    0%{opacity:0} 15%{opacity:.95} 38%{opacity:.15} 55%{opacity:.65} 100%{opacity:0}
                }
                @keyframes rebirth {
                    0%{opacity:0;transform:scale(.1)}
                    20%{opacity:1;transform:scale(3)}
                    60%{opacity:1;transform:scale(1)}
                    100%{opacity:0;transform:scale(.1)}
                }
                @keyframes born {
                    0%{opacity:0;transform:scale(.92)}
                    35%{opacity:1;transform:scale(1.03)}
                    100%{opacity:1;transform:scale(1)}
                }

                @media (prefers-reduced-motion:reduce) {
                    .stars,.stars2,.stars3,.planet,.planet-name,.intruder,.trail,.impact,.shock,.flash,.rebirth-core,.nova-born,.scene-title,.nova-credit { animation:none !important; }
                    .scene-title,.planet,.planet-name,.nova-born,.nova-credit { opacity:1 !important; }
                    .planet { transform:scale(1) !important; }
                    .intruder,.trail,.impact,.shock,.flash,.rebirth-core { opacity:0 !important; }
                }
            </style>

            <div class="nova-film" aria-label="Cinematic origin story of NOVA">
                <div class="stars"></div>
                <div class="stars2"></div>
                <div class="stars3"></div>
                <div class="scene-title">THE ARCHIVE HAS BEEN COMPLETED &nbsp;•&nbsp; <b>NOVA ORIGIN PROTOCOL</b></div>

                <div class="planet"></div>
                <div class="planet-name">N O V A</div>

                <div class="trail"></div>
                <div class="intruder"></div>
                <div class="impact"></div>
                <div class="shock"></div>
                <div class="flash"></div>
                <div class="rebirth-core"></div>

                <div class="nova-born">
                    <div class="nova-date">06 • 11 • 2009 &nbsp; | &nbsp; 10:30 AM</div>
                    <h1>NOVA WAS BORN.</h1>
                    <p>ONE COLLISION. ONE NEW STAR. ONE UNFORGETTABLE STORY.</p>
                </div>

                <div class="nova-credit">FARHEEN ✦ NOVA &nbsp; // &nbsp; PERSONAL ARCHIVE</div>
                <div class="film-vignette"></div>
            </div>
            """,
            height=730,
            scrolling=False,
        )

        if st.button("🔁 PLAY NOVA ORIGIN AGAIN", key="replay_nova_cinematic", use_container_width=True):
            st.rerun()

        st.markdown(
            f"""
            <div class="big-reveal" style="margin-top:18px;">
                <div class="kicker">🎊 PARTY PROTOCOL // COMPLETE 🎊</div>
                <h1>🎂 HAPPY BIRTHDAY, NOVA 🎂</h1>
                <p style="font-family:Orbitron;letter-spacing:4px;color:#c8d0e8;">
                    06 • 11 • 2009 ✦ 10:30 AM
                </p>
                <p style="font-size:18px;color:#c8d0e8;">{gift}</p>
                <p style="font-size:32px;">🎉 🥳 🎊 🎈 🎂 🎈 🎊 🥳 🎉</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# RANDOMIZER + JOURNAL + REVIEW + ACHIEVEMENTS
# ============================================================
st.markdown("---")

r1, r2, r3 = st.columns(3)
with r1:
    if st.button("🎰 NOVA RANDOMIZER", use_container_width=True):
        events = [
            ("😂 RANDOM FACT", "NOVA's night-owl mode has been detected."),
            ("💭 RANDOM MEMORY", "Some ordinary moments become the ones you remember forever."),
            ("🎯 MINI CHALLENGE", "Find one thing around you that makes you smile."),
            ("💌 RANDOM MESSAGE", "You made it this far. The archive is proud of you. ✦"),
            ("✨ RANDOM COMPLIMENT", "Your energy deserves its own power source."),
        ]
        st.session_state.random_event = random.choice(events)
with r2:
    if st.button("📖 HOW DID THE DAY GO?", use_container_width=True):
        st.query_params.clear()
        st.session_state.page = "💌 JOURNAL"
        st.rerun()
with r3:
    if st.button("🏆 ACTIVITY REPORT", use_container_width=True):
        st.query_params.clear()
        st.session_state.page = "🏆 REPORT"
        st.rerun()

if st.session_state.random_event:
    title, text = st.session_state.random_event
    card(title, text, "🎰")

# Journal is rendered after the global controls so it is accessible even without a nav item.
if st.session_state.page == "💌 JOURNAL":
    award("DAY RECORDED")
    section_title("PERSONAL LOG // 06", "HOW DID YOUR DAY GO?", "Leave a little record of the birthday.")
    day = st.text_area("✍️ Tell me about your day", placeholder="What happened? What made you smile? What was your favourite moment?", height=240)
    mood = st.select_slider("😊 DAY ENERGY", options=["😶 Quiet", "🙂 Good", "😄 Great", "🤩 Unforgettable"], value="😄 Great")
    if st.button("💌 SUBMIT MY BIRTHDAY LOG", use_container_width=True):
        if day.strip():
            st.session_state.day_submitted = True
            award("DAY RECORDED")
            st.success("✨ BIRTHDAY LOG RECORDED.")
        else:
            st.warning("Write something about your day first.")
    if st.session_state.day_submitted:
        st.markdown(f'<div class="diary-card"><div class="card-title">NOVA BIRTHDAY LOG</div><div class="card-body"><b>DAY ENERGY:</b> {mood}<br><br>Memory recorded successfully. ✦<br><br>Come back to this page whenever you want to remember the day.</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    section_title("FEEDBACK ARCHIVE", "REVIEW THE WEBSITE", "Your honest review becomes part of the archive.")
    rating = st.slider("⭐ RATE THIS WEBSITE", 1, 5, 5)
    liked = st.text_input("❤️ What did you like the most?", placeholder="The puzzle, animations, memories, etc.")
    suggestion = st.text_area("💡 Anything you would improve?", height=120)
    if st.button("⭐ SUBMIT MY REVIEW", use_container_width=True):
        st.session_state.review_submitted = True
        award("WEBSITE REVIEWED")
        st.success("🌟 REVIEW ARCHIVED. Thank you!")
    if st.session_state.review_submitted:
        st.markdown(f'<div class="review-card"><div class="card-title">NOVA WEBSITE REVIEW // {rating}/5 ⭐</div><div class="card-body">Your review has been added to the birthday archive. ✦</div></div>', unsafe_allow_html=True)

# ============================================================
# ACTIVITY REPORT
# ============================================================
if st.session_state.page == "🏆 REPORT":
    section_title("FINAL ARCHIVE // 07", "NOVA ACTIVITY REPORT", "Everything you discovered during the experience.")

    checks = activity_checks()
    for label, done in checks:
        st.markdown(
            f"""
            <div class="glass-card" style="min-height:auto;padding:18px 24px;">
                <div class="card-body" style="font-family:Orbitron;letter-spacing:2px;">
                    {label} &nbsp;&nbsp; {'✓' if done else '○'}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    completed = sum(done for _, done in checks)
    total = len(checks)
    pct = int(completed / total * 100)

    st.markdown(
        f"""
        <div class="big-reveal">
            <div class="kicker">NOVA ACTIVITY SCORE</div>
            <h1>{pct}%</h1>
            <p style="color:#aab4d4;">{completed}/{total} archive objectives completed.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    section_title("ACHIEVEMENT VAULT", "BADGES UNLOCKED", "Every discovery leaves a mark.")
    if st.session_state.achievements:
        cols = st.columns(3)
        icons = {
            "FIRST DISCOVERY":"🏅", "ARCHIVE EXPLORER":"🌌", "MEMORY MAKER":"📸",
            "QUIZ EXPLORER":"🧠", "QUIZ MASTER":"🏆", "TIME TRAVELER":"🔮",
            "FUTURE TRANSMISSION":"🛰️", "SECRET FOUND":"⭐", "PUZZLE SOLVER":"🧩",
            "BIRTHDAY COMPLETE":"🎂", "DAY RECORDED":"💌", "WEBSITE REVIEWED":"⭐",
        }
        for i, badge in enumerate(sorted(st.session_state.achievements)):
            with cols[i % 3]:
                st.markdown(f'<div class="achievement-card" style="text-align:center;"><div style="font-size:38px">{icons.get(badge,"✦")}</div><div class="card-title">{badge}</div></div>', unsafe_allow_html=True)
    else:
        st.info("No achievements yet. Start exploring.")

# ============================================================
# PRIVATE ARCHIVE OVERRIDE
# ============================================================
# Temporary developer shortcut: this is intentionally tucked away at the very
# bottom of the archive. It completes the checklist without creating fake
# photos/reviews; the activity report simply treats the archive as complete.
st.markdown(
    """
    <div style="height:18px;"></div>
    """,
    unsafe_allow_html=True,
)

with st.expander("·", expanded=False):
    st.caption("Archive maintenance")
    if st.button("🔐 COMPLETE ARCHIVE TASKS", key="private_archive_override", use_container_width=True):
        st.session_state.archive_override = True
        st.session_state.day_submitted = True
        st.session_state.review_submitted = True
        st.session_state.secret_found = True
        st.session_state.capsule_saved = True
        for badge in [
            "FIRST DISCOVERY", "ARCHIVE EXPLORER", "MEMORY MAKER",
            "QUIZ EXPLORER", "QUIZ MASTER", "TIME TRAVELER",
            "FUTURE TRANSMISSION", "SECRET FOUND", "PUZZLE SOLVER",
            "DAY RECORDED", "WEBSITE REVIEWED",
        ]:
            award(badge)
        st.success("Archive override activated. All objectives are complete.")
        st.rerun()

# ============================================================
# Footer
# ============================================================
st.markdown(
    """
    <div class="footer">
        NOVA // PERSONAL ARCHIVE ✦ 06 • 11 • 2009 ✦ 10:30 AM<br>
        ARCHIVE STATUS: ONLINE
    </div>
    """,
    unsafe_allow_html=True,
)
