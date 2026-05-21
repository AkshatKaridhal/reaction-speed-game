import streamlit as st
import time
import random

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="Reaction Speed Game",
    page_icon="⚡",
    layout="centered"
)

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

.main .block-container {
    max-width: 560px;
    padding-top: 2rem;
}

/* ---------- Header ---------- */
.game-header {
    text-align: center;
    margin-bottom: 1.5rem;
}
.game-header h1 {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin: 0;
}
.game-header p {
    font-size: 0.9rem;
    color: #888;
    margin-top: 4px;
}

/* ---------- Stat cards ---------- */
.stat-card {
    background: #1c1c1e;
    border-radius: 12px;
    padding: 16px 12px;
    text-align: center;
}
.stat-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #666;
    margin-bottom: 6px;
}
.stat-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    color: #f0f0f0;
}
.stat-value.green { color: #1D9E75; }

/* ---------- Arena ---------- */
.arena {
    border-radius: 16px;
    padding: 3rem 2rem;
    text-align: center;
    margin: 1.25rem 0;
    transition: background 0.2s ease;
}
.arena-idle    { background: #1c1c1e; border: 1px solid #2a2a2a; }
.arena-waiting { background: #1c1c1e; border: 1px solid #2a2a2a; }
.arena-go      { background: #04342C; border: 1px solid #1D9E75; }
.arena-early   { background: #2a0f05; border: 1px solid #D85A30; }
.arena-result  { background: #1c1c1e; border: 1px solid #2a2a2a; }

.arena-icon { font-size: 3rem; margin-bottom: 0.75rem; }

.arena-title {
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: -0.3px;
    color: #f0f0f0;
    margin-bottom: 0.4rem;
}
.arena-title.green  { color: #9FE1CB; font-size: 1.8rem; }
.arena-title.red    { color: #F5C4B3; }

.arena-sub { font-size: 0.85rem; color: #666; }
.arena-sub.green    { color: #5DCAA5; }
.arena-sub.red      { color: #F0997B; }

/* Reaction time display */
.rt-number {
    font-family: 'Space Mono', monospace;
    font-size: 3.5rem;
    font-weight: 700;
    color: #f0f0f0;
    letter-spacing: -2px;
    line-height: 1;
}
.rt-unit {
    font-family: 'Space Mono', monospace;
    font-size: 0.95rem;
    color: #666;
    margin-top: 4px;
}

/* Dots loader */
@keyframes blink {
    0%, 100% { opacity: 0.2; }
    50%       { opacity: 1;   }
}
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%;
       background: #444; margin: 0 3px; animation: blink 1.2s ease infinite; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

/* Badge */
.badge {
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    padding: 4px 14px;
    border-radius: 8px;
    margin-top: 10px;
}
.badge-best { background: #0F6E56; color: #9FE1CB; }
.badge-good { background: #0c447c; color: #B5D4F4; }

/* History */
.hist-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #666;
    margin-bottom: 8px;
}
.hist-item {
    display: flex;
    align-items: center;
    background: #1c1c1e;
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 6px;
}
.hist-rank  { font-size: 12px; color: #666; width: 22px; flex-shrink: 0; }
.hist-track { flex: 1; height: 4px; background: #2a2a2a;
              border-radius: 2px; margin: 0 12px; overflow: hidden; }
.hist-fill  { height: 100%; background: #1D9E75; border-radius: 2px; }
.hist-time  { font-family: 'Space Mono', monospace; font-size: 13px;
              font-weight: 700; color: #f0f0f0; min-width: 58px; text-align: right; }

/* Override Streamlit button style */
div[data-testid="stButton"] > button {
    width: 100%;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    padding: 0.75rem 1rem;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------

defaults = {
    "phase": "idle",       # idle | waiting | go | early | result
    "wait_until": 0.0,
    "start_time": 0.0,
    "last_rt": None,
    "times": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- HELPERS ----------------

def best_time():
    return min(st.session_state.times) if st.session_state.times else None

def avg_time():
    t = st.session_state.times
    return sum(t) / len(t) if t else None

def fmt_ms(sec):
    return f"{round(sec * 1000)} ms"

# ---------------- HEADER ----------------

st.markdown("""
<div class="game-header">
    <h1>⚡ Reaction Speed</h1>
    <p>Click the moment it turns green — how fast are you?</p>
</div>
""", unsafe_allow_html=True)

# ---------------- STAT CARDS ----------------

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Attempts</div>
        <div class="stat-value">{len(st.session_state.times)}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    b = best_time()
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Best Time</div>
        <div class="stat-value green">{fmt_ms(b) if b else "—"}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    a = avg_time()
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Average</div>
        <div class="stat-value">{fmt_ms(a) if a else "—"}</div>
    </div>""", unsafe_allow_html=True)

# ---------------- ARENA ----------------

phase = st.session_state.phase

if phase == "idle":
    st.markdown("""
    <div class="arena arena-idle">
        <div class="arena-icon">⚡</div>
        <div class="arena-title">Ready to test your reflexes?</div>
        <div class="arena-sub">Press Start to begin</div>
    </div>""", unsafe_allow_html=True)

elif phase == "waiting":
    st.markdown("""
    <div class="arena arena-waiting">
        <div class="arena-icon">⏳</div>
        <div class="arena-title">Get ready…</div>
        <div class="arena-sub">Wait for green — don't click early!</div>
        <div style="margin-top:14px">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
        </div>
    </div>""", unsafe_allow_html=True)

elif phase == "go":
    st.markdown("""
    <div class="arena arena-go">
        <div class="arena-icon">🟢</div>
        <div class="arena-title green">CLICK NOW!</div>
        <div class="arena-sub green">Go go go!</div>
    </div>""", unsafe_allow_html=True)

elif phase == "early":
    st.markdown("""
    <div class="arena arena-early">
        <div class="arena-icon">😬</div>
        <div class="arena-title red">Too early!</div>
        <div class="arena-sub red">Wait for it to turn green</div>
    </div>""", unsafe_allow_html=True)

elif phase == "result":
    rt = st.session_state.last_rt
    ms = round(rt * 1000)
    is_new_best = (
        len(st.session_state.times) > 1
        and rt == best_time()
    )
    badge_html = ""
    if is_new_best:
        badge_html = '<div class="badge badge-best">🏆 New Best!</div>'
    elif rt < 0.25:
        badge_html = '<div class="badge badge-good">⚡ Excellent!</div>'

    st.markdown(f"""
    <div class="arena arena-result">
        <div class="arena-icon">⏱️</div>
        <div class="rt-number">{ms}<span style="font-size:1.5rem">ms</span></div>
        <div class="rt-unit">{rt:.3f} seconds</div>
        {badge_html}
    </div>""", unsafe_allow_html=True)

# ---------------- PHASE TRANSITION (waiting → go) ----------------

if phase == "waiting":
    now = time.time()
    if now >= st.session_state.wait_until:
        st.session_state.phase = "go"
        st.session_state.start_time = time.time()
        st.rerun()
    else:
        time.sleep(0.15)
        st.rerun()

# ---------------- BUTTONS ----------------

if phase == "idle":
    if st.button("🎮  Start Game", use_container_width=True):
        st.session_state.phase = "waiting"
        st.session_state.wait_until = time.time() + random.uniform(1.5, 4.5)
        st.rerun()

elif phase == "waiting":
    if st.button("❌  Cancel", use_container_width=True):
        st.session_state.phase = "idle"
        st.rerun()

elif phase == "go":
    if st.button("⚡  CLICK!", use_container_width=True, type="primary"):
        rt = time.time() - st.session_state.start_time
        st.session_state.last_rt = rt
        st.session_state.times.append(rt)
        st.session_state.phase = "result"
        st.rerun()

elif phase == "early":
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄  Try Again", use_container_width=True, type="primary"):
            st.session_state.phase = "waiting"
            st.session_state.wait_until = time.time() + random.uniform(1.5, 4.5)
            st.rerun()
    with col_b:
        if st.button("🏠  Home", use_container_width=True):
            st.session_state.phase = "idle"
            st.rerun()

elif phase == "result":
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄  Play Again", use_container_width=True, type="primary"):
            st.session_state.phase = "waiting"
            st.session_state.wait_until = time.time() + random.uniform(1.5, 4.5)
            st.rerun()
    with col_b:
        if st.button("🗑️  Reset All", use_container_width=True):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.rerun()

# ---------------- HISTORY ----------------

times = st.session_state.times
if times:
    st.markdown("<div style='margin-top:1.5rem'>", unsafe_allow_html=True)
    st.markdown('<div class="hist-label">Last Attempts</div>', unsafe_allow_html=True)

    recent  = list(reversed(times[-5:]))
    max_t   = max(recent)
    min_t   = min(recent)

    for i, t in enumerate(recent):
        orig_idx = len(times) - i
        pct = int(((max_t - t) / (max_t - min_t) * 80 + 20)) if max_t != min_t else 60
        is_best = t == min(times) and len(times) > 1
        rank_html = "👑" if is_best else f"#{orig_idx}"

        st.markdown(f"""
        <div class="hist-item">
            <div class="hist-rank">{rank_html}</div>
            <div class="hist-track"><div class="hist-fill" style="width:{pct}%"></div></div>
            <div class="hist-time">{round(t*1000)} ms</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ----------------

st.markdown(
    "<div style='text-align:center; margin-top:2rem; font-size:0.8rem; color:#555;'>"
    "Made with ❤️ using Streamlit</div>",
    unsafe_allow_html=True
)