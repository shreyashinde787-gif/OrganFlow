from pathlib import Path
import streamlit as st
import pandas as pd
from dsa import OrganFlow, MAX_HOURS, BLOOD, URG_RANK, fmt_min

st.set_page_config(page_title="OrganFlow", page_icon="🫀", layout="wide")
st.markdown("""<style>
[data-testid=stSidebar]{background:linear-gradient(180deg,#0b4a8f,#052a5c)}
[data-testid=stSidebar] *{color:#fff !important}
[data-testid=stSidebar] input,[data-testid=stSidebar] textarea{color:#111 !important}
.hero{background:#fff;border-left:6px solid #f59e0b;border-radius:14px;padding:22px 28px;box-shadow:0 4px 18px #0001;margin-bottom:12px}
.hero h1{margin:0;color:#0b2a4a}.hero p{margin:6px 0 0;color:#555}
</style>""", unsafe_allow_html=True)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ICON = {"SAFE": "🟢", "WARNING": "🟡", "CRITICAL": "🔴", "EXPIRED": "⚫"}

@st.cache_data
def load_csv():
    """Load CSVs from the project-level data folder, not the frontend folder."""
    frames = []
    for name in ("organs", "recipients", "hospitals"):
        path = DATA / f"{name}.csv"
        if not path.exists():
            st.error(f"Missing dataset: {path}. Keep the data folder beside frontend.")
            st.stop()
        frames.append(pd.read_csv(path).fillna(""))
    return frames

def system():
    if "sys" not in st.session_state:
        o, r, h = load_csv()
        st.session_state.sys = OrganFlow(o.to_dict("records"), r.to_dict("records"), h.to_dict("records"))
    return st.session_state.sys

S = system()
hosp_names = [h["name"] for h in S.hospitals] or ["Demo Hospital"]
def df(rows, cols=None):
    d = pd.DataFrame(rows)
    return d[cols] if cols and not d.empty else d

def organ_label(oid):
    o = S.find_organ(oid)
    return f"{oid} — {o['organ_type']} {o['blood_group']} ({o['status']})" if o else oid

with st.sidebar:
    st.markdown("<div style='text-align:center;font-size:56px'>🫀</div><h2 style='text-align:center'>OrganFlow</h2><p style='text-align:center;font-size:13px'>Smart Organ Match & Cold-Chain Tracker</p>", unsafe_allow_html=True)
    user = st.text_input("User name")
    page = st.radio("MENU", ["Dashboard", "Register Organ", "Recipient Registry", "Smart Matching", "Transit & Journey", "Viability & Emergency", "Audit Trail", "About / DSA"])
    st.caption(f"🕒 Sim clock: {S.now().strftime('%d-%b %H:%M')}")
    c1, c2 = st.columns(2)
    if c1.button("+30 min"):
        S.advance_clock(30); st.rerun()
    if c2.button("+2 hrs"):
        S.advance_clock(120); st.rerun()
    if st.button("Reset demo data"):
        st.session_state.pop("sys", None); st.rerun()
    st.caption("Educational prototype • Synthetic data only")

if page == "Dashboard":
    st.markdown(f"<div class='hero'><h1>Dear {user or 'Donor'} 👋</h1><p>Welcome to OrganFlow — your DSA-powered coordination dashboard.</p></div>", unsafe_allow_html=True)
    st.subheader("Dashboard Overview")
    cnt = lambda status: sum(o["status"] == status for o in S.organs)
    m = st.columns(5)
    m[0].metric("Organs", len(S.organs)); m[1].metric("Available", cnt("AVAILABLE")); m[2].metric("In transit", cnt("IN_TRANSIT"))
    m[3].metric("Waiting recipients", sum(r["status"] == "WAITING" for r in S.recipients)); m[4].metric("Audit entries", len(S.audit))
    a, b = st.columns([3, 2])
    a.subheader("Registered Organs"); a.dataframe(df(S.organs, ["organ_id", "organ_type", "blood_group", "donor_hospital", "status"]), use_container_width=True, height=340)
    b.subheader("Recent Audit Actions"); b.dataframe(df(S.audit.to_list()[:10]), use_container_width=True, height=340)
    st.info("Demo data is fictional. This tool demonstrates logistics and DSA concepts; it is not a clinical allocation system.")

elif page == "Register Organ":
    st.header("🧬 Register Donated Organ")
    with st.form("org"):
        t = st.selectbox("Organ type", list(MAX_HOURS)); bg = st.selectbox("Blood group", BLOOD)
        h = st.selectbox("Donor hospital", hosp_names); el = st.number_input("Minutes since harvest", 0, 600, 0)
        submitted = st.form_submit_button("Register")
    if submitted:
        st.success(f"Registered {S.register_organ(t, bg, h, int(el))} (demo viability window: {MAX_HOURS[t]} h)")
        st.rerun()

elif page == "Recipient Registry":
    st.header("📋 Recipient Registry")
    with st.expander("➕ Add recipient"):
        with st.form("rec"):
            n = st.text_input("Display name")
            c = st.columns(4); o = c[0].selectbox("Organ needed", list(MAX_HOURS)); b = c[1].selectbox("Blood", BLOOD)
            u = c[2].selectbox("Urgency", list(URG_RANK)); d = c[3].number_input("Waiting days", 0, 3000, 30)
            h = st.selectbox("Hospital", hosp_names)
            submitted = st.form_submit_button("Add recipient")
        if submitted:
            if not n.strip(): st.error("Please enter a display name.")
            else:
                st.success(f"Added {S.add_recipient(n.strip(), o, b, u, int(d), h)}")
                st.rerun()
    f = st.columns(3); fo = f[0].multiselect("Organ", list(MAX_HOURS)); fb = f[1].multiselect("Blood", BLOOD); fu = f[2].multiselect("Urgency", list(URG_RANK))
    rows = [r for r in S.recipients if (not fo or r["organ_needed"] in fo) and (not fb or r["blood_group"] in fb) and (not fu or r["urgency"] in fu)]
    st.caption(f"{len(rows)} recipients shown")
    st.dataframe(df(rows), use_container_width=True, height=450)

elif page == "Smart Matching":
    st.header("🧠 Smart Recipient Matching")
    st.info("Decision support only — final allocation remains with authorized medical authorities. All records are synthetic.")
    av = [o["organ_id"] for o in S.organs if o["status"] == "AVAILABLE"]
    if not av: st.warning("No available organs. Register a demo organ or reset demo data.")
    else:
        oid = st.selectbox("Available organ", av, format_func=organ_label)
        organ = S.find_organ(oid); v = S.viability(organ)
        st.write(f"{ICON[v['status']]} Remaining viability: **{fmt_min(v['remaining'])}**")
        ranked, rejected = S.match(oid)
        st.subheader(f"Eligible ({len(ranked)}) — ranked by urgency, then waiting duration")
        if ranked:
            e = df(ranked, ["recipient_id", "name", "blood_group", "urgency", "waiting_days", "hospital"])
            e.insert(0, "rank", range(1, len(e) + 1)); st.dataframe(e.head(20), use_container_width=True)
            st.caption("Unique demo feature: every non-eligible record is accompanied by a rejection reason, making matching more explainable.")
            rid = st.selectbox("Select a candidate to simulate transit", [r["recipient_id"] for r in ranked[:20]], format_func=lambda x: f"{x} — {S.find_recipient(x)['name']}")
            if st.button("🚑 Start transit"):
                S.start_transit(oid, rid); st.success("Demo transit started."); st.rerun()
        else: st.warning("No currently eligible waiting recipients for this organ.")
        with st.expander(f"❌ Ineligible candidates ({len(rejected)}) — why they were filtered"):
            st.dataframe(df(rejected[:100]), use_container_width=True)

elif page == "Transit & Journey":
    st.header("📍 Cold-Chain Journey Tracking")
    ids = [o["organ_id"] for o in S.organs if o["status"] in ("IN_TRANSIT", "INTERRUPTED")]
    if not ids: st.warning("No organs in transit. Start transit from Smart Matching first.")
    else:
        oid = st.selectbox("Organ", ids, format_func=organ_label); o = S.find_organ(oid)
        st.write(f"**{o['organ_type']} {o['blood_group']}** → recipient **{o.get('recipient_id') or 'Not assigned'}** • status **{o['status']}**")
        st.write("Queue (remaining route):", " ➜ ".join(S.route[oid].to_list()) or "—")
        st.dataframe(df(S.journey[oid].to_list()), use_container_width=True)
        if o["status"] == "INTERRUPTED":
            st.error("TRANSPORT INTERRUPTED — flagged for urgent handling")
            if st.button("Resume transit"): S.resume(oid); st.rerun()
        else:
            t = st.slider("Temperature at next checkpoint (°C)", 0.0, 15.0, 5.0, 0.5)
            if t > 8 or t < 2: st.warning("⚠ COLD-CHAIN ALERT — temperature is outside the demo safe range of 2–8 °C")
            c = st.columns(2)
            if c[0].button("➡ Advance checkpoint"):
                cp = S.advance(oid, float(t))
                if cp is None: st.warning("All route checkpoints have already been processed.")
                else: st.success(f"Checkpoint recorded: {cp['location']} — {cp['status']}")
                st.rerun()
            reason = c[1].text_input("Interruption reason", "Vehicle breakdown")
            if c[1].button("⛔ Report interruption"):
                S.interrupt(oid, reason.strip() or "Unspecified interruption"); st.rerun()

elif page == "Viability & Emergency":
    st.header("⏳ Viability Countdown & Emergency Queue")
    st.caption("Priority is simulated from interruption state and remaining demo viability; it is not medical advice.")
    rows = S.emergency_board()
    if not rows: st.info("No organs in transit.")
    for o, v, urgent in rows:
        c = st.columns([2, 3, 2, 2]); c[0].markdown(f"**{o['organ_id']}** {o['organ_type']} {o['blood_group']}")
        c[1].progress(float(v["pct"]), text=f"{ICON[v['status']]} {v['status']} — {fmt_min(v['remaining'])} left")
        c[2].write(o["status"]); c[3].write("🚨 URGENT" if urgent else "Normal")
    st.subheader("Route-risk summary")
    risks = []
    for o in S.organs:
        if o["status"] in ("IN_TRANSIT", "INTERRUPTED"):
            v = S.viability(o); checkpoints = S.journey.get(o["organ_id"])
            history = checkpoints.to_list() if checkpoints else []
            alerts = sum(cp.get("status") != "SAFE" for cp in history)
            risks.append({"organ_id": o["organ_id"], "status": o["status"], "viability": v["status"], "minutes_left": round(v["remaining"]), "temperature_alerts": alerts, "risk_flag": "HIGH" if o["status"] == "INTERRUPTED" or v["status"] in ("CRITICAL", "EXPIRED") or alerts else "MONITOR"})
    if risks: st.dataframe(df(risks).sort_values(["risk_flag", "minutes_left"], ascending=[True, True]), use_container_width=True)

elif page == "Audit Trail":
    st.header("📋 Audit Trail (Stack — newest on top)")
    st.dataframe(df(S.audit.to_list()), use_container_width=True, height=550)
    st.caption("Audit entries are held in a hand-written LIFO stack for this session. Resetting the demo clears session changes.")

else:
    st.header("🎯 About / DSA Mapping")
    st.write("OrganFlow demonstrates the logistics around donated-organ transport using fictional records. It does not make medical allocation decisions.")
    st.table(pd.DataFrame([
        ["Organ records", "List / array-like collection"], ["Recipient lookup", "Linear Search"],
        ["Eligibility filtering", "Linear Search + conditional logic"], ["Candidate ordering", "Stable Merge Sort: urgency, then waiting days"],
        ["Planned route", "Hand-written Queue (FIFO)"], ["Organ journey", "Hand-written Linked List"],
        ["Recent activity / audit", "Hand-written Stack (LIFO)"], ["Emergency handling", "Priority Queue / min-heap"],
        ["Viability countdown", "Time arithmetic + conditional logic"], ["Cold-chain alerts", "Temperature range validation"],
        ["Explainable rejection reasons", "Rule-based filtering with recorded reason"],
        ["Route-risk summary", "Combines interruptions, viability, and checkpoint alerts"]], columns=["Requirement / feature", "DSA or logic used"]))
    st.info("Synthetic educational prototype only. No real patient data is used. Eligibility ranking is illustrative and must never be used for real-world organ allocation.")
    st.markdown("**Architecture note:** This Streamlit demo executes the DSA implementation in `frontend/dsa.py`. The original Java lab program is preserved separately in `java-lab/SmartOrganTracker.java`; it is not yet wired to this UI through a Java API.")
