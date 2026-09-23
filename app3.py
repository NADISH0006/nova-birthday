import streamlit as st
import streamlit.components.v1 as components
import random
import time
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
    # NOVA ARCADE state
    "arcade_catch_score": 0,
    "arcade_catch_target": random.randint(0, 8),
    "arcade_catch_done": False,
    "arcade_memory_sequence": random.sample(["🌙", "⭐", "🪐", "💙", "🐾", "✨"], 4),
    "arcade_memory_showing": True,
    "arcade_memory_user": [],
    "arcade_memory_done": False,
    "arcade_reaction_started": False,
    "arcade_reaction_ready_at": None,
    "arcade_reaction_done": False,
    "arcade_code_done": False,
    "arcade_unlocked": False,
    "secret_files_opened": set(),
    "secret_final_unlocked": False,
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
    ("🕹️ ARCADE", "🕹️ ARCADE"), ("🔐 SECRET ROOM", "🔐 SECRET ROOM"),
]
cols = st.columns(4)
for i, (label, target) in enumerate(nav):
    with cols[i % 4]:
        nav_button(label, target)


# ============================================================
# NOVA ARCADE // 4 MINI GAMES
# ============================================================
if st.session_state.page == "🕹️ ARCADE":
    section_title(
        "NOVA ARCADE // 4 GAMES",
        "PLAY. COLLECT. UNLOCK.",
        "Each completed game gives one digit. Finish all four to reveal the Secret Room code."
    )

    if st.button("↻ RESET ARCADE", key="reset_arcade", use_container_width=False):
        st.session_state.arcade_catch_score = 0
        st.session_state.arcade_catch_target = random.randint(0, 8)
        st.session_state.arcade_catch_done = False
        st.session_state.arcade_memory_sequence = random.sample(["🌙", "⭐", "🪐", "💙", "🐾", "✨"], 4)
        st.session_state.arcade_memory_showing = True
        st.session_state.arcade_memory_user = []
        st.session_state.arcade_memory_done = False
        st.session_state.arcade_reaction_started = False
        st.session_state.arcade_reaction_ready_at = None
        st.session_state.arcade_reaction_done = False
        st.session_state.arcade_code_done = False
        st.session_state.arcade_unlocked = False
        st.session_state.secret_files_opened = set()
        st.session_state.secret_final_unlocked = False
        st.rerun()

    arcade_digits = {
        "CATCH THE STAR": "7",
        "MEMORY HACK": "4",
        "REACTION TEST": "2",
        "CODE BREAKER": "9",
    }

    # ---------- GAME 1 ----------
    st.markdown('<div class="card-title">⭐ 01 // CATCH THE STAR</div>', unsafe_allow_html=True)
    st.caption("Catch the hidden star 3 times. Wrong squares are safe — just try again.")
    if not st.session_state.arcade_catch_done:
        grid = st.columns(3)
        for idx in range(9):
            with grid[idx % 3]:
                label = "✦" if idx == st.session_state.arcade_catch_target else "·"
                if st.button(label, key=f"catch_star_{idx}", use_container_width=True):
                    if idx == st.session_state.arcade_catch_target:
                        st.session_state.arcade_catch_score += 1
                        if st.session_state.arcade_catch_score >= 3:
                            st.session_state.arcade_catch_done = True
                            award("ARCADE STAR")
                        else:
                            st.session_state.arcade_catch_target = random.randint(0, 8)
                            st.success(f"STAR CAUGHT! {st.session_state.arcade_catch_score}/3")
                    else:
                        st.session_state.arcade_catch_target = random.randint(0, 8)
                        st.info("Not there, da. The star moved. ✦")
                    st.rerun()
    else:
        st.success(f"GAME COMPLETE — DIGIT {arcade_digits['CATCH THE STAR']}")
    # ---------- GAME 2 ----------
    st.markdown('<div class="card-title">🧠 02 // MEMORY HACK</div>', unsafe_allow_html=True)
    st.caption("Memorize the four-symbol sequence, hide it, then enter it in the same order.")
    seq = st.session_state.arcade_memory_sequence
    if not st.session_state.arcade_memory_done:
        if st.session_state.arcade_memory_showing:
            st.markdown(
                f"<div style='font-size:38px;letter-spacing:14px;text-align:center;padding:18px'>{' '.join(seq)}</div>",
                unsafe_allow_html=True,
            )
            if st.button("HIDE SEQUENCE", key="memory_hide", use_container_width=True):
                st.session_state.arcade_memory_showing = False
                st.rerun()
        else:
            st.write("Your sequence:", " → ".join(st.session_state.arcade_memory_user) or "—")
            mem_cols = st.columns(6)
            for idx, emoji in enumerate(["🌙", "⭐", "🪐", "💙", "🐾", "✨"]):
                with mem_cols[idx]:
                    if st.button(emoji, key=f"memory_pick_{idx}", use_container_width=True):
                        expected = seq[len(st.session_state.arcade_memory_user)]
                        if emoji == expected:
                            st.session_state.arcade_memory_user.append(emoji)
                            if len(st.session_state.arcade_memory_user) == len(seq):
                                st.session_state.arcade_memory_done = True
                                award("MEMORY HACKER")
                        else:
                            st.session_state.arcade_memory_user = []
                            st.warning("Sequence reset. Take another look and try again.")
                        st.rerun()
    else:
        st.success(f"GAME COMPLETE — DIGIT {arcade_digits['MEMORY HACK']}")
    # ---------- GAME 3 ----------
    st.markdown('<div class="card-title">⚡ 03 // REACTION TEST</div>', unsafe_allow_html=True)
    st.caption("Start the test. When GO appears, hit it as quickly as you can.")
    if not st.session_state.arcade_reaction_done:
        if not st.session_state.arcade_reaction_started:
            if st.button("START REACTION TEST", key="reaction_start", use_container_width=True):
                delay = random.uniform(0.8, 1.8)
                time.sleep(delay)
                st.session_state.arcade_reaction_ready_at = time.monotonic()
                st.session_state.arcade_reaction_started = True
                st.rerun()
        else:
            if st.button("🟢 GO!", key="reaction_go", use_container_width=True):
                elapsed = time.monotonic() - st.session_state.arcade_reaction_ready_at
                st.session_state.arcade_reaction_done = True
                award("REACTION RUNNER")
                st.success(f"Reaction time: {elapsed:.3f} seconds — DIGIT {arcade_digits['REACTION TEST']}")
                st.rerun()
    else:
        st.success(f"GAME COMPLETE — DIGIT {arcade_digits['REACTION TEST']}")
    # ---------- GAME 4 ----------
    st.markdown('<div class="card-title">🔢 04 // CODE BREAKER</div>', unsafe_allow_html=True)
    st.caption("Final puzzle: what is 3²?")
    if not st.session_state.arcade_code_done:
        answer = st.number_input("Enter the digit", min_value=0, max_value=9, value=0, step=1, key="code_breaker_answer")
        if st.button("VERIFY DIGIT", key="code_breaker_verify", use_container_width=True):
            if answer == 9:
                st.session_state.arcade_code_done = True
                award("CODE BREAKER")
                st.rerun()
            else:
                st.error("Not quite. Try again.")
    else:
        st.success(f"GAME COMPLETE — DIGIT {arcade_digits['CODE BREAKER']}")
    all_games = (
        st.session_state.arcade_catch_done
        and st.session_state.arcade_memory_done
        and st.session_state.arcade_reaction_done
        and st.session_state.arcade_code_done
    )
    if all_games:
        st.markdown('<div class="card-title">🔓 ARCADE COMPLETE</div>', unsafe_allow_html=True)
        st.markdown(
            "<div class='card-body'>All four digits collected. The access code is waiting in your archive.</div>",
            unsafe_allow_html=True,
        )
        st.code("7429", language="text")
        if st.button("🔐 ENTER NOVA SECRET ROOM", key="arcade_enter_secret", use_container_width=True):
            st.session_state.arcade_unlocked = True
            st.session_state.page = "🔐 SECRET ROOM"
            award("SECRET ROOM ACCESS")
            st.rerun()
        

# ============================================================
# NOVA SECRET ROOM // LOCKED ARCHIVE
# ============================================================
if st.session_state.page == "🔐 SECRET ROOM":
    section_title(
        "RESTRICTED ARCHIVE // 7429",
        "NOVA SECRET ROOM",
        "A private collection unlocked by completing the four arcade files."
    )

    if not st.session_state.arcade_unlocked:
        st.markdown('<div class="card-title">🔒 ACCESS DENIED</div>', unsafe_allow_html=True)
        st.markdown(
            "<div class='card-body'>Complete the four NOVA ARCADE games first. "
            "The code is collected one digit at a time.</div>",
            unsafe_allow_html=True,
        )
        if st.button("🕹️ GO TO NOVA ARCADE", key="secret_go_arcade", use_container_width=True):
            st.session_state.page = "🕹️ ARCADE"
            st.rerun()
    else:
        secret_files = [
            ("CORE FILE", "core"),
            ("ORIGIN STORY", "origin"),
            ("NOVA FILES", "files"),
            ("MEMORY VAULT", "vault"),
            ("THE MESSAGE", "message"),
            ("ACHIEVEMENT WALL", "achievements"),
        ]

        for title, key in secret_files:
            opened = key in st.session_state.secret_files_opened
            label = ("▾ " if opened else "▸ ") + title
            if st.button(label, key=f"secret_file_{key}", use_container_width=True):
                if opened:
                    st.session_state.secret_files_opened.discard(key)
                else:
                    st.session_state.secret_files_opened.add(key)
                st.rerun()

            if opened:
                if key == "core":
                    card(
                        "CORE FILE // NOVA",
                        "<b>NAME:</b> FARHEEN<br>"
                        "<b>CODENAME:</b> NOVA<br>"
                        "<b>DOB:</b> 06 November 2009<br>"
                        "<b>BIRTH TIME:</b> 10:30 AM<br>"
                        "<b>ARCHETYPE:</b> Night owl<br>"
                        "<b>ENERGY:</b> Extrovert<br>"
                        "<b>KNOWN FOR:</b> Mathematics, oval specs, and her unique 🥻 = “seri” message code.",
                        "🌌",
                    )
                elif key == "origin":
                    section_title("RESTRICTED MEMORY", "THE BEGINNING", "The original chapter of the archive.")
                    image_paths = [
                        Path("/mnt/data/1ofF.jpeg"),
                        Path("1ofF.jpeg"),
                        Path("assets/1ofF.jpeg"),
                    ]
                    image_path = next((x for x in image_paths if x.exists()), None)
                    if image_path:
                        st.image(str(image_path), caption="ORIGIN FRAME // NOVA", use_container_width=True)
                    else:
                        st.info("Origin photo not found yet. Add 1ofF.jpeg beside the app or in assets/.")
                    card(
                        "ORIGIN NOTE",
                        "Before the archive became a collection of moments, there was simply the beginning. "
                        "This file keeps that first chapter separate from everything that came later.",
                        "🧸",
                    )
                elif key == "files":
                    card(
                        "NOVA FILES",
                        "<b>FILE 01:</b> Night Owl Protocol 🌙<br>"
                        "<b>FILE 02:</b> Mathematics Mode 🧮<br>"
                        "<b>FILE 03:</b> Oval Specimen Signal 👓<br>"
                        "<b>FILE 04:</b> Cat Archive 🐾<br>"
                        "<b>FILE 05:</b> The 🥻 Message Code<br>"
                        "<b>FILE 06:</b> Unknown Variable — still classified.",
                        "📁",
                    )
                elif key == "vault":
                    if st.session_state.captured_photos:
                        collage = make_collage(st.session_state.captured_photos)
                        if collage:
                            st.image(collage, caption="NOVA MEMORY VAULT", use_container_width=True)
                    else:
                        card(
                            "MEMORY VAULT",
                            "No captured moments have been added yet. Use the MOMENTS page to create the first memory.",
                            "📸",
                        )
                elif key == "message":
                    card(
                        "A MESSAGE FOR NOVA",
                        "Some people leave ordinary memories. Some turn ordinary days into stories. "
                        "This archive is a small digital way of keeping the funny, bright, chaotic, "
                        "and unforgettable parts of the journey together. ✦<br><br>"
                        "<b>HAPPY BIRTHDAY, NOVA.</b> 🌌",
                        "💌",
                    )
                elif key == "achievements":
                    earned = sorted(st.session_state.achievements)
                    if earned:
                        st.markdown(
                            "<div class='glass-card'><div class='card-title'>ACHIEVEMENT WALL</div>"
                            + "".join(f"<div class='card-body'>✦ {a}</div>" for a in earned)
                            + "</div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.info("Explore the archive to collect achievements.")

        if len(st.session_state.secret_files_opened) == len(secret_files):
            st.session_state.secret_final_unlocked = True

        if st.session_state.secret_final_unlocked:
            st.markdown('<div class="card-title">🌟 FINAL SECRET FILE // UNLOCKED</div>', unsafe_allow_html=True)
            st.markdown(
                "<div class='card-body'>"
                "You opened every restricted file. There is nothing left to hide.<br><br>"
                "<b>FARHEEN // NOVA</b><br>"
                "This archive was made to celebrate one person, one story, and a lot of memories. ✦"
                "</div>",
                unsafe_allow_html=True,
            )
            if st.button("🎂 OPEN FINAL BIRTHDAY REVEAL", key="secret_final_reveal", use_container_width=True):
                st.session_state.final_reveal_requested = True
                st.session_state.page = "🎂 BIRTHDAY"
                st.rerun()
            

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
                *{box-sizing:border-box}
                html,body{margin:0;padding:0;background:#02030a;overflow:hidden}
                body{font-family:Arial,sans-serif}
                .film{position:relative;width:100%;height:760px;overflow:hidden;border-radius:28px;background:#010208;border:1px solid rgba(175,190,255,.28);box-shadow:0 0 70px rgba(80,100,255,.22),inset 0 0 100px #000}
                .film:before{content:"";position:absolute;inset:-20%;background:radial-gradient(circle at 50% 50%,rgba(75,100,255,.16),transparent 28%),radial-gradient(circle at 20% 80%,rgba(130,55,255,.10),transparent 30%);animation:spacePulse 8s ease-in-out infinite;pointer-events:none}
                .stars,.dust{position:absolute;inset:-10%;pointer-events:none;background-repeat:repeat}
                .stars{background-image:radial-gradient(circle,#fff 0 1px,transparent 1.5px),radial-gradient(circle,#9db5ff 0 1px,transparent 1.5px);background-size:71px 83px,127px 113px;background-position:8px 20px,40px 70px;opacity:.8;animation:starMove 18s linear infinite}
                .dust{background-image:radial-gradient(circle,rgba(150,170,255,.7) 0 1px,transparent 2px);background-size:181px 151px;opacity:.28;animation:dustMove 11s linear infinite reverse}
                .scan{position:absolute;inset:0;pointer-events:none;opacity:.12;background:repeating-linear-gradient(0deg,transparent 0 3px,rgba(180,200,255,.08) 4px,transparent 5px);mix-blend-mode:screen}
                .vignette{position:absolute;inset:0;z-index:50;pointer-events:none;background:radial-gradient(circle,transparent 38%,rgba(0,0,0,.82) 100%)}
                .letterbox{position:absolute;left:0;width:100%;height:54px;background:#000;z-index:60}.topbar{top:0}.bottombar{bottom:0}
                .hud{position:absolute;top:78px;left:30px;right:30px;z-index:45;display:flex;justify-content:space-between;color:rgba(210,220,255,.62);font-size:10px;letter-spacing:3px;text-transform:uppercase}
                .progress{position:absolute;left:30px;right:30px;bottom:72px;height:2px;background:rgba(255,255,255,.12);z-index:45}.progress i{display:block;height:100%;width:0;background:linear-gradient(90deg,#7194ff,#c28cff,#fff);animation:progress 19s linear forwards}
                .scene{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;text-align:center;opacity:0;pointer-events:none;z-index:30}
                .scene .eyebrow{font-size:11px;letter-spacing:6px;color:#9eb1ef;margin-bottom:20px}.scene h1{margin:0;color:#fff;font-family:Georgia,serif;font-size:clamp(38px,7vw,86px);letter-spacing:7px;text-shadow:0 0 20px rgba(175,195,255,.8),0 0 70px rgba(95,110,255,.55)}
                .scene p{margin:18px auto 0;max-width:720px;color:#cbd4ee;font-size:14px;line-height:1.8;letter-spacing:3px}
                .intro{animation:intro 3.2s ease forwards}.intro2{animation:intro2 3.5s ease forwards 3s}.bornScene{animation:bornScene 4.5s ease forwards 13.3s}
                .planet{position:absolute;width:230px;height:230px;left:calc(50% - 115px);top:calc(50% - 115px);border-radius:50%;z-index:10;background:radial-gradient(circle at 31% 25%,#fff 0 3%,#b9c7ff 10%,transparent 25%),radial-gradient(circle at 60% 60%,#6479dd 0 15%,#26336f 43%,#080c26 76%,#010208 100%);box-shadow:-30px -25px 55px rgba(150,175,255,.35),25px 30px 65px #000,0 0 55px rgba(100,130,255,.25);opacity:0;transform:scale(.2);animation:planetIn 4s cubic-bezier(.16,.8,.2,1) forwards 2.7s,planetFloat 5s ease-in-out infinite 6.7s}
                .planet:before{content:"";position:absolute;inset:-14px;border-radius:50%;border:1px solid rgba(170,190,255,.35);box-shadow:0 0 35px rgba(105,135,255,.3)}
                .planet:after{content:"";position:absolute;width:330px;height:70px;left:-50px;top:80px;border:2px solid rgba(180,190,255,.25);border-radius:50%;transform:rotate(-18deg);box-shadow:0 0 25px rgba(120,150,255,.18)}
                .planet-label{position:absolute;top:calc(50% + 135px);width:100%;z-index:15;text-align:center;color:#dce4ff;font-size:12px;letter-spacing:8px;opacity:0;animation:fade 2s ease forwards 6s}
                .meteor{position:absolute;width:90px;height:90px;border-radius:50%;left:-140px;top:calc(50% - 45px);z-index:16;background:radial-gradient(circle at 28% 24%,#fff3df,#ff9b63 20%,#9c315a 58%,#21091d 100%);box-shadow:0 0 30px #ff9b70,0 0 90px rgba(255,80,80,.5);animation:meteor 3.1s cubic-bezier(.65,.02,.9,.35) forwards 7.1s}
                .meteor:before{content:"";position:absolute;width:290px;height:22px;right:60px;top:34px;background:linear-gradient(90deg,transparent,rgba(255,150,100,.8),transparent);filter:blur(6px);transform:rotate(0deg)}
                .orbit{position:absolute;width:430px;height:430px;border:1px solid rgba(130,155,255,.16);border-radius:50%;z-index:8;animation:orbit 10s linear infinite 4s;transform:rotateX(66deg)}
                .orbit:after{content:"";position:absolute;width:8px;height:8px;border-radius:50%;background:#a9c0ff;box-shadow:0 0 18px #8ca8ff;left:8px;top:50%}
                .rings{position:absolute;width:80px;height:80px;border:2px solid rgba(190,210,255,.7);border-radius:50%;left:calc(50% - 40px);top:calc(50% - 40px);z-index:24;opacity:0;animation:rings 3s ease-out forwards 10.15s}
                .rings:before,.rings:after{content:"";position:absolute;inset:-30px;border:1px solid rgba(120,150,255,.55);border-radius:50%}.rings:after{inset:-65px;border-color:rgba(190,130,255,.35)}
                .flash{position:absolute;inset:0;background:#fff;z-index:40;opacity:0;pointer-events:none;animation:flash 2s ease forwards 10.15s}
                .shock{position:absolute;width:60px;height:60px;left:calc(50% - 30px);top:calc(50% - 30px);border-radius:50%;border:2px solid #fff;z-index:25;opacity:0;animation:shock 2.8s ease-out forwards 10.1s}
                .core{position:absolute;width:24px;height:24px;left:calc(50% - 12px);top:calc(50% - 12px);border-radius:50%;background:#fff;z-index:28;box-shadow:0 0 40px #fff,0 0 110px #a9bfff,0 0 190px #a16cff;opacity:0;animation:core 4s ease-out forwards 10.2s}
                .particle{position:absolute;width:5px;height:5px;border-radius:50%;left:50%;top:50%;background:#fff;z-index:27;opacity:0;box-shadow:0 0 12px #fff;animation:particle 2.8s ease-out forwards 10.35s}
                .p1{--x:-280px;--y:-190px}.p2{--x:300px;--y:-150px}.p3{--x:-330px;--y:110px}.p4{--x:350px;--y:150px}.p5{--x:-130px;--y:260px}.p6{--x:170px;--y:240px}.p7{--x:-420px;--y:-40px}.p8{--x:420px;--y:20px}.p9{--x:-210px;--y:-300px}.p10{--x:230px;--y:-290px}
                .born-card{padding:35px 25px}.born-card .date{color:#aabcf5;font-size:14px;letter-spacing:8px;margin-bottom:22px}.born-card h1{font-size:clamp(42px,8vw,96px);margin:0}.born-card .line{height:1px;width:180px;margin:25px auto;background:linear-gradient(90deg,transparent,#fff,transparent)}
                @keyframes starMove{to{transform:translate3d(-50px,35px,0)}}@keyframes dustMove{to{transform:translate3d(70px,-40px,0)}}@keyframes spacePulse{50%{transform:scale(1.15);opacity:.8}}
                @keyframes progress{to{width:100%}}
                @keyframes intro{0%{opacity:0;transform:scale(1.08);filter:blur(7px)}20%{opacity:1;transform:scale(1);filter:blur(0)}75%{opacity:1}100%{opacity:0;transform:scale(.96);filter:blur(4px)}}
                @keyframes intro2{0%{opacity:0;transform:translateY(25px)}18%{opacity:1;transform:translateY(0)}75%{opacity:1}100%{opacity:0;transform:translateY(-20px)}}
                @keyframes planetIn{0%{opacity:0;transform:scale(.2) rotate(-30deg)}55%{opacity:1;transform:scale(1.08) rotate(8deg)}100%{opacity:1;transform:scale(1) rotate(0)}}
                @keyframes planetFloat{50%{transform:translateY(-10px) rotate(2deg)}}
                @keyframes fade{to{opacity:1}}@keyframes orbit{to{transform:rotateX(66deg) rotateZ(360deg)}}
                @keyframes meteor{0%{opacity:0;transform:translateX(0) rotate(0)}8%{opacity:1}100%{opacity:1;transform:translateX(calc(50vw + 150px)) rotate(900deg)}}
                @keyframes rings{0%{opacity:0;transform:scale(.1)}20%{opacity:1}100%{opacity:0;transform:scale(9)}}
                @keyframes shock{0%{opacity:0;transform:scale(.1)}15%{opacity:1}100%{opacity:0;transform:scale(18)}}
                @keyframes flash{0%{opacity:0}12%{opacity:.95}25%{opacity:0}45%{opacity:.5}100%{opacity:0}}
                @keyframes core{0%{opacity:0;transform:scale(.1)}20%{opacity:1;transform:scale(4)}55%{opacity:1;transform:scale(1.2)}100%{opacity:0;transform:scale(.2)}}
                @keyframes particle{0%{opacity:0;transform:translate(0,0) scale(.3)}18%{opacity:1}100%{opacity:0;transform:translate(var(--x),var(--y)) scale(1.8)}}
                @keyframes bornScene{0%{opacity:0;transform:scale(.82);filter:blur(12px)}22%{opacity:1;transform:scale(1.04);filter:blur(0)}35%{transform:scale(1)}100%{opacity:1}}
                @media(max-width:700px){.film{height:620px;border-radius:20px}.hud{left:18px;right:18px;top:68px;font-size:8px}.progress{left:18px;right:18px}.letterbox{height:38px}.planet{width:170px;height:170px;left:calc(50% - 85px);top:calc(50% - 85px)}.orbit{width:300px;height:300px}.planet-label{top:calc(50% + 105px)}.scene p{padding:0 25px;font-size:11px}.born-card .date{letter-spacing:4px;font-size:11px}}
                @media(prefers-reduced-motion:reduce){*{animation:none!important}.scene{opacity:1}.planet{opacity:1;transform:scale(1)}.meteor,.flash,.shock,.core,.rings{display:none}}
            </style>
            <div class="film">
                <div class="stars"></div><div class="dust"></div><div class="scan"></div>
                <div class="letterbox topbar"></div><div class="letterbox bottombar"></div>
                <div class="hud"><span>NOVA ORIGIN // CINEMATIC CUT</span><span>06 • 11 • 2009</span></div>
                <div class="progress"><i></i></div>

                <div class="scene intro"><div><div class="eyebrow">ARCHIVE COMPLETE • FINAL TRANSMISSION</div><h1>EVERY STAR<br>HAS A STORY.</h1><p>Some stories begin quietly.<br>Some arrive like a supernova.</p></div></div>
                <div class="scene intro2"><div><div class="eyebrow">THE ARCHIVE PRESENTS</div><h1>NOVA</h1><p>A small universe of memories, chaos, laughter and moments worth keeping.</p></div></div>

                <div class="orbit"></div><div class="planet"></div><div class="planet-label">N O V A • PERSONAL UNIVERSE</div>
                <div class="meteor"></div><div class="rings"></div><div class="shock"></div><div class="flash"></div><div class="core"></div>
                <div class="particle p1"></div><div class="particle p2"></div><div class="particle p3"></div><div class="particle p4"></div><div class="particle p5"></div><div class="particle p6"></div><div class="particle p7"></div><div class="particle p8"></div><div class="particle p9"></div><div class="particle p10"></div>

                <div class="scene bornScene"><div class="born-card"><div class="date">06 • 11 • 2009 &nbsp; | &nbsp; 10:30 AM</div><h1>NOVA WAS BORN.</h1><div class="line"></div><p>ONE COLLISION. ONE NEW STAR.<br>ONE UNFORGETTABLE STORY.</p></div></div>
                <div class="vignette"></div>
            </div>
            """,
            height=790,
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
