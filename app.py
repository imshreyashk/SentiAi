import streamlit as st
import json
import time
from stadium_engine import StadiumOperationsEngine, TelemetryPayload

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SentinAI-Pitch · FIFA 2026",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Dark Control-Room Theme ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #080c14;
    color: #e2e8f0;
}
.stApp { background: linear-gradient(135deg, #080c14 0%, #0d1525 50%, #080c14 100%); }

/* Banner */
.banner-wrap {
    background: linear-gradient(90deg, #00153a 0%, #001f55 40%, #00153a 100%);
    border: 1px solid #1e3a6e;
    border-radius: 12px;
    padding: 22px 32px;
    margin-bottom: 24px;
    text-align: center;
    box-shadow: 0 0 40px rgba(0,100,255,0.15);
}
.banner-title {
    font-size: 1.6rem; font-weight: 900; letter-spacing: 0.12em;
    background: linear-gradient(90deg, #38bdf8, #818cf8, #e879f9);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0; line-height: 1.2;
}
.banner-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; color: #64748b; letter-spacing: 0.15em;
    margin-top: 6px;
}
.live-dot {
    display: inline-block; width: 8px; height: 8px;
    background: #22c55e; border-radius: 50%;
    box-shadow: 0 0 8px #22c55e;
    animation: pulse 1.4s infinite;
    margin-right: 6px; vertical-align: middle;
}
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

/* Section headers */
.section-hdr {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.2em;
    padding: 6px 14px; border-radius: 4px; margin-bottom: 14px;
    display: inline-block;
}
.hdr-tele { background: rgba(56,189,248,0.08); color: #38bdf8; border-left: 3px solid #38bdf8; }
.hdr-miti { background: rgba(250,204,21,0.08); color: #facc15; border-left: 3px solid #facc15; }

/* Incident cards */
.card {
    background: linear-gradient(135deg, #0f1c33 0%, #0a1628 100%);
    border: 1px solid #1e3a6e;
    border-radius: 10px; padding: 16px 20px; margin-bottom: 16px;
    transition: border-color 0.2s;
}
.card:hover { border-color: #3b82f6; }
.card-low  { border-left: 4px solid #22c55e; }
.card-med  { border-left: 4px solid #facc15; }
.card-high { border-left: 4px solid #ef4444; box-shadow: 0 0 20px rgba(239,68,68,0.12); }

.phase-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem; font-weight: 600; letter-spacing: 0.18em;
    padding: 2px 8px; border-radius: 3px;
}
.tag-past   { background: #1e293b; color: #64748b; }
.tag-live   { background: rgba(34,197,94,0.15); color: #22c55e; }
.tag-upcoming { background: rgba(250,204,21,0.12); color: #facc15; }
.tag-fault  { background: rgba(239,68,68,0.15); color: #ef4444; }

.match-label { font-size: 0.95rem; font-weight: 700; color: #e2e8f0; margin: 8px 0 2px; }
.result-text { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #94a3b8; }

.metric-row { display: flex; gap: 20px; margin: 12px 0; }
.metric-box { flex: 1; background: #0a1222; border-radius: 6px; padding: 8px 12px; }
.metric-lbl { font-size: 0.6rem; color: #64748b; letter-spacing: 0.12em; text-transform: uppercase; }
.metric-val { font-size: 1.1rem; font-weight: 700; }
.clr-low  { color: #22c55e; }
.clr-med  { color: #facc15; }
.clr-high { color: #ef4444; }
.clr-gray { color: #94a3b8; }

/* Mitigation cards */
.mcard {
    background: linear-gradient(135deg, #10190e 0%, #0c1a0a 100%);
    border: 1px solid #1a3320; border-left: 4px solid #22c55e;
    border-radius: 10px; padding: 16px 20px; margin-bottom: 16px;
}
.mcard-med { background: linear-gradient(135deg, #1a1700 0%,#100f00 100%); border-color: #3a3000; border-left-color: #facc15; }
.mcard-high { background: linear-gradient(135deg, #1a0a0a 0%,#110505 100%); border-color: #3a1010; border-left-color: #ef4444; }
.mcard-fault { background: linear-gradient(135deg, #1a0500 0%,#110200 100%); border-color: #3a1500; border-left-color: #f97316; }

.action-row { margin: 8px 0; font-size: 0.85rem; }
.action-lbl { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; font-weight: 600; letter-spacing: 0.15em; }
.action-val { color: #e2e8f0; }
.lbl-route { color: #38bdf8; }
.lbl-staff { color: #facc15; }
.lbl-bcast { color: #e879f9; }
.broadcast-text { font-style: italic; color: #c084fc; }

/* Filter box */
div[data-testid="stTextInput"] input {
    background: #0f1c33 !important; border: 1px solid #1e3a6e !important;
    color: #e2e8f0 !important; border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
}
div[data-testid="stTextInput"] input:focus { border-color: #3b82f6 !important; }

/* Progress bar override */
div[data-testid="stProgressBar"] > div > div { border-radius: 4px; }

/* Divider */
hr { border-color: #1e3a6e !important; }

/* Metric tiles */
div[data-testid="metric-container"] {
    background: #0f1c33; border: 1px solid #1e3a6e;
    border-radius: 8px; padding: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Engine ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_engine() -> StadiumOperationsEngine:
    return StadiumOperationsEngine()

engine = get_engine()

# ── FIFA WC 2026 Dataset ───────────────────────────────────────────────────────
# crowd_temperament accepts: calm | anxious | angry | violent
# "Celebratory" post-match egress → mapped to "calm" (orderly dispersal)
SCENARIOS = [
    # ── PAST ──────────────────────────────────────────────────────────────────
    {"phase":"PAST",     "label":"R16 · Seattle · Belgium vs USA",             "result":"Belgium 4–1 USA",          "date":"COMPLETED",     "mood_display":"Celebratory (Orderly Egress)",
     "payload":{"gate_id":"SEA-N","current_occupancy":950,"max_capacity":1000,"transit_status":"normal","crowd_temperament":"calm","active_language":"en"}},
    {"phase":"PAST",     "label":"R16 · New York/NJ · Norway vs Brazil",       "result":"Norway 2–1 Brazil",        "date":"COMPLETED",     "mood_display":"Calm",
     "payload":{"gate_id":"NYN-E","current_occupancy":880,"max_capacity":1000,"transit_status":"normal","crowd_temperament":"calm","active_language":"en"}},
    {"phase":"PAST",     "label":"R32 · Mexico City · Mexico vs Ecuador",      "result":"Mexico 2–0 Ecuador",       "date":"COMPLETED",     "mood_display":"Celebratory (Orderly Egress)",
     "payload":{"gate_id":"MEX-S","current_occupancy":1000,"max_capacity":1000,"transit_status":"normal","crowd_temperament":"calm","active_language":"es"}},

    # ── LIVE ──────────────────────────────────────────────────────────────────
    {"phase":"LIVE",     "label":"R16 · Atlanta · Argentina vs Egypt",          "result":"ONGOING — Kick-off 20:00 EST", "date":"JUL 07 2026", "mood_display":"Calm",
     "payload":{"gate_id":"ATL-W","current_occupancy":320,"max_capacity":1000,"transit_status":"normal","crowd_temperament":"calm","active_language":"en"}},
    {"phase":"LIVE",     "label":"R16 · Vancouver · Switzerland vs Colombia",   "result":"ONGOING — Kick-off 22:00 EST", "date":"JUL 07 2026", "mood_display":"Anxious (Shuttle Delay)",
     "payload":{"gate_id":"VAN-A","current_occupancy":760,"max_capacity":1000,"transit_status":"delayed","crowd_temperament":"anxious","active_language":"fr"}},

    # ── UPCOMING ──────────────────────────────────────────────────────────────
    {"phase":"UPCOMING", "label":"QF · Boston · France vs Morocco",             "result":"SCHEDULED",                "date":"JUL 09 2026",   "mood_display":"Anxious (Pre-match Transit Delay)",
     "payload":{"gate_id":"BOS-C","current_occupancy":850,"max_capacity":1000,"transit_status":"delayed","crowd_temperament":"anxious","active_language":"fr"}},
    {"phase":"UPCOMING", "label":"QF · SoFi LA · Spain vs Belgium",             "result":"SCHEDULED — CRITICAL RISK", "date":"JUL 10 2026",  "mood_display":"Violent (Non-linear Compounding Risk)",
     "payload":{"gate_id":"LAX-B","current_occupancy":980,"max_capacity":1000,"transit_status":"blocked","crowd_temperament":"violent","active_language":"es"}},
    {"phase":"UPCOMING", "label":"FINAL · MetLife NJ · Finalist Slot Allocation","result":"PREVIEW — Pre-gate Intake","date":"JUL 19 2026",  "mood_display":"Calm (Early Structural Load)",
     "payload":{"gate_id":"MET-VIP","current_occupancy":150,"max_capacity":1000,"transit_status":"normal","crowd_temperament":"calm","active_language":"en"}},
]

# ── Helpers ────────────────────────────────────────────────────────────────────
PHASE_TAG  = {"PAST":"tag-past","LIVE":"tag-live","UPCOMING":"tag-upcoming","FAULT":"tag-fault"}
PHASE_DISP = {"PAST":"■ PAST","LIVE":"◉ LIVE","UPCOMING":"◆ UPCOMING","FAULT":"⚠ FAULT"}

def threat_meta(score: float) -> tuple:
    if score < 40.0:   return "LOW",    "low",  "#22c55e", "clr-low",  "card-low",  "mcard"
    elif score < 70.0: return "MED",    "med",  "#facc15", "clr-med",  "card-med",  "mcard mcard-med"
    else:              return "HIGH",   "high", "#ef4444", "clr-high", "card-high", "mcard mcard-high"

def process(sc: dict):
    try:
        p = sc["payload"]
        payload = TelemetryPayload(
            gate_id=p["gate_id"], current_occupancy=int(p["current_occupancy"]),
            max_capacity=int(p["max_capacity"]), transit_status=p["transit_status"],
            crowd_temperament=p["crowd_temperament"], active_language=p["active_language"],
        )
        score = engine.evaluate_threat_score(payload)
        mitigation = json.loads(engine.broker_mitigation(payload))
        return payload, score, mitigation, None
    except Exception as exc:
        return None, None, None, str(exc)

# ── Session State: auto-refresh tick ──────────────────────────────────────────
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# ── Banner ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="banner-wrap">
  <div class="banner-title">🏟️ FIFA 2026 STADIUM COMMAND NETWORK — SENTINAI-PITCH</div>
  <div class="banner-sub">
    <span class="live-dot"></span>
    REAL-TIME CROWD DYNAMICS ENGINE &nbsp;·&nbsp; COGNITIVE MITIGATION ACTIVE &nbsp;·&nbsp; WC2026 FIXTURE FEED
  </div>
</div>
""", unsafe_allow_html=True)

# ── Top control bar ────────────────────────────────────────────────────────────
ctrl_l, ctrl_m, ctrl_r = st.columns([3, 1, 1])
with ctrl_l:
    query = st.text_input("", placeholder="🔍  Filter by team, stadium or gate ID…", label_visibility="collapsed")
with ctrl_m:
    st.metric("Total Fixtures", len(SCENARIOS))
with ctrl_r:
    live_cnt = sum(1 for s in SCENARIOS if s["phase"] == "LIVE")
    st.metric("Live Now", live_cnt, delta="◉ Active", delta_color="normal")

st.markdown("---")

# ── Filter ─────────────────────────────────────────────────────────────────────
q = query.strip().lower()
filtered = [s for s in SCENARIOS if not q or q in s["label"].lower() or q in s["payload"]["gate_id"].lower()]

if not filtered:
    st.warning(f"No fixtures match **\"{query}\"**. Try a team name, stadium, or gate ID.")
    st.stop()

# ── Phase summary pills ────────────────────────────────────────────────────────
phase_counts = {}
for s in filtered:
    phase_counts[s["phase"]] = phase_counts.get(s["phase"], 0) + 1

pill_html = ""
pill_cls  = {"PAST":"tag-past","LIVE":"tag-live","UPCOMING":"tag-upcoming"}
for ph, cnt in phase_counts.items():
    pill_html += f'<span class="phase-tag {pill_cls.get(ph,"tag-past")}" style="margin-right:8px;">{PHASE_DISP[ph]} ({cnt})</span>'
st.markdown(pill_html + "<br>", unsafe_allow_html=True)

# ── Split Column Layout ────────────────────────────────────────────────────────
col_tele, col_miti = st.columns(2, gap="large")

with col_tele:
    st.markdown('<div class="section-hdr hdr-tele">📡 &nbsp; LIVE TELEMETRY INCIDENTS</div>', unsafe_allow_html=True)

with col_miti:
    st.markdown('<div class="section-hdr hdr-miti">⚡ &nbsp; AUTOMATED COGNITIVE MITIGATION ACTIONS</div>', unsafe_allow_html=True)

# ── Render each fixture ────────────────────────────────────────────────────────
for sc in filtered:
    payload, score, mitigation, error = process(sc)
    phase      = sc["phase"]
    tag_cls    = PHASE_TAG.get(phase, "tag-past")
    phase_disp = PHASE_DISP.get(phase, phase)

    # ── TELEMETRY CARD ─────────────────────────────────────────────────────────
    with col_tele:
        if error:
            st.markdown(f"""
            <div class="card card-high">
              <span class="phase-tag {tag_cls}">{phase_disp}</span>
              <div class="match-label">{sc['label']}</div>
              <div class="result-text">{sc['date']} &nbsp;·&nbsp; {sc['result']}</div>
              <div style="margin-top:12px; padding:10px; background:rgba(239,68,68,0.08); border-radius:6px; border:1px solid rgba(239,68,68,0.3);">
                <span style="color:#ef4444; font-family:JetBrains Mono,monospace; font-size:0.75rem;">⚠ FAULT: {error}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            lbl, css, hex_c, clr_cls, card_cls, _ = threat_meta(score)
            occ_pct = payload.current_occupancy / payload.max_capacity
            transit_color = {"normal":"#22c55e","delayed":"#facc15","blocked":"#ef4444"}.get(payload.transit_status,"#94a3b8")
            mood_color    = {"calm":"#22c55e","anxious":"#facc15","angry":"#f97316","violent":"#ef4444"}.get(payload.crowd_temperament,"#94a3b8")

            st.markdown(f"""
            <div class="card {card_cls}">
              <span class="phase-tag {tag_cls}">{phase_disp}</span>
              <div class="match-label">{sc['label']}</div>
              <div class="result-text">{sc['date']} &nbsp;·&nbsp; {sc['result']}</div>
              <div class="metric-row">
                <div class="metric-box">
                  <div class="metric-lbl">Threat Score</div>
                  <div class="metric-val {clr_cls}">{score:.1f}<span style="font-size:0.65rem;color:#64748b;">/100</span></div>
                </div>
                <div class="metric-box">
                  <div class="metric-lbl">Threat Level</div>
                  <div class="metric-val {clr_cls}">{lbl}</div>
                </div>
                <div class="metric-box">
                  <div class="metric-lbl">Gate ID</div>
                  <div class="metric-val clr-gray" style="font-family:JetBrains Mono,monospace;font-size:0.9rem;">{payload.gate_id}</div>
                </div>
              </div>
              <div style="font-size:0.7rem;color:#64748b;margin-bottom:4px;">Occupancy &nbsp; {int(occ_pct*100)}% &nbsp; ({payload.current_occupancy:,}/{payload.max_capacity:,})</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(min(occ_pct, 1.0))
            st.markdown(f"""
            <div style="display:flex;gap:16px;margin-bottom:16px;font-size:0.78rem;">
              <span>🚌 <span style="color:{transit_color};font-weight:600;">{payload.transit_status.upper()}</span></span>
              <span>😤 <span style="color:{mood_color};font-weight:600;">{sc['mood_display']}</span></span>
              <span>🌐 <span style="color:#818cf8;font-weight:600;">{payload.active_language.upper()}</span></span>
            </div>
            """, unsafe_allow_html=True)

    # ── MITIGATION CARD ────────────────────────────────────────────────────────
    with col_miti:
        if error:
            st.markdown(f"""
            <div class="mcard mcard-fault" style="border-left-color:#f97316;">
              <span class="phase-tag tag-fault">{phase_disp}</span>
              <div class="match-label" style="color:#f97316;margin-top:8px;">⚠ FAULT INTERCEPT ACTIVE</div>
              <div class="action-row"><span class="action-lbl" style="color:#f97316;">▶ STATUS &nbsp;&nbsp;&nbsp;</span><span class="action-val">Pipeline caught corrupted telemetry packet safely.</span></div>
              <div class="action-row"><span class="action-lbl" style="color:#f97316;">▶ ACTION &nbsp;&nbsp;&nbsp;</span><span class="action-val">Packet discarded. Sensor reset queued.</span></div>
              <div class="action-row"><span class="action-lbl" style="color:#f97316;">▶ BROADCAST</span><span class="broadcast-text"> "Control room standby. Signal integrity check in progress."</span></div>
            </div>
            <div style="height:46px;"></div>
            """, unsafe_allow_html=True)
        else:
            _, css, _, _, _, mcard_cls = threat_meta(score)
            st.markdown(f"""
            <div class="{mcard_cls}">
              <span class="phase-tag {tag_cls}">{phase_disp}</span>
              <div class="match-label" style="margin-top:8px;">Gate {payload.gate_id} — Mitigation Issued</div>
              <div class="action-row">
                <div><span class="action-lbl lbl-route">▶ DYNAMIC ROUTING &nbsp;&nbsp;</span></div>
                <div class="action-val" style="padding-left:4px;">{mitigation['dynamic_routing']}</div>
              </div>
              <div class="action-row" style="margin-top:8px;">
                <div><span class="action-lbl lbl-staff">▶ STAFF ALLOCATION &nbsp;</span></div>
                <div class="action-val" style="padding-left:4px;">{mitigation['staff_allocation']}</div>
              </div>
              <div class="action-row" style="margin-top:8px;">
                <div><span class="action-lbl lbl-bcast">▶ FAN BROADCAST &nbsp;&nbsp;&nbsp;&nbsp;</span></div>
                <div class="broadcast-text" style="padding-left:4px;">"{mitigation['broadcast_msg']}"</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
ts = time.strftime("%Y-%m-%d %H:%M:%S UTC")
st.markdown(f"""
<div style="text-align:center;font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#334155;padding:8px 0;">
  SENTINAI-PITCH &nbsp;·&nbsp; FIFA WORLD CUP 2026 &nbsp;·&nbsp; STADIUM COMMAND NETWORK &nbsp;·&nbsp;
  LAST RENDERED: {ts} &nbsp;·&nbsp; ENGINE: StadiumOperationsEngine v1.0
</div>
""", unsafe_allow_html=True)

# ── Auto-refresh via query param (non-blocking, Streamlit-native) ──────────────
st.markdown("""
<script>
setTimeout(function(){ window.location.reload(); }, 30000);
</script>
""", unsafe_allow_html=True)
