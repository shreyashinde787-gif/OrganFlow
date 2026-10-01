import streamlit as st, pandas as pd
from dsa import OrganFlow, MAX_HOURS, BLOOD, URG_RANK, fmt_min

st.set_page_config(page_title="OrganFlow", page_icon="🫀", layout="wide")
st.markdown("""<style>
[data-testid=stSidebar]{background:linear-gradient(180deg,#0b4a8f,#052a5c)}
[data-testid=stSidebar] *{color:#fff !important}
[data-testid=stSidebar] input{color:#111 !important}
.hero{background:#fff;border-left:6px solid #f59e0b;border-radius:14px;padding:22px 28px;box-shadow:0 4px 18px #0001;margin-bottom:12px}
.hero h1{margin:0;color:#0b2a4a}.hero p{margin:6px 0 0;color:#555}
</style>""", unsafe_allow_html=True)
ICON = {"SAFE": "🟢", "WARNING": "🟡", "CRITICAL": "🔴", "EXPIRED": "⚫"}

@st.cache_data
def load_csv():
    return [pd.read_csv(f"{n}.csv").fillna("") for n in ("organs", "recipients", "hospitals")]

def system():
    if "sys" not in st.session_state:
        o, r, h = load_csv()
        st.session_state.sys = OrganFlow(o.to_dict("records"), r.to_dict("records"), h.to_dict("records"))
    return st.session_state.sys

S = system(); hosp_names = [h["name"] for h in S.hospitals]
def df(rows, cols=None):
    d = pd.DataFrame(rows); return d[cols] if cols and len(d) else d

# ---------- sidebar ----------
with st.sidebar:
    st.markdown("<div style='text-align:center;font-size:56px'>🫀</div><h2 style='text-align:center'>OrganFlow</h2>"
                "<p style='text-align:center;font-size:13px'>Smart Organ Match & Cold-Chain Tracker</p>", unsafe_allow_html=True)
    user = st.text_input("User name")
    page = st.radio("MENU", ["Dashboard", "Register Organ", "Recipient Registry", "Smart Matching",
                             "Transit & Journey", "Viability & Emergency", "Audit Trail", "About / DSA"])
    st.caption(f"🕒 Sim clock: {S.now().strftime('%d-%b %H:%M')}")
    c1, c2 = st.columns(2)
    if c1.button("+30 min"): S.advance_clock(30); st.rerun()
    if c2.button("+2 hrs"): S.advance_clock(120); st.rerun()
    if st.button("Reset data"): del st.session_state["sys"]; st.rerun()
    st.caption("Educational prototype • Synthetic data only")

# ---------- pages ----------
if page == "Dashboard":
    st.markdown(f"<div class='hero'><h1>Dear {user or 'Donor'} 👋</h1><p>Welcome to OrganFlow — your DSA-powered coordination dashboard.</p></div>", unsafe_allow_html=True)
    st.subheader("Dashboard Overview")
    cnt = lambda s: sum(o["status"] == s for o in S.organs)
    m = st.columns(5)
    m[0].metric("Organs", len(S.organs)); m[1].metric("Available", cnt("AVAILABLE"))
    m[2].metric("In transit", cnt("IN_TRANSIT")); m[3].metric("Waiting recipients", sum(r["status"] == "WAITING" for r in S.recipients))
    m[4].metric("Audit entries", len(S.audit))
    a, b = st.columns([3, 2])
    a.subheader("Registered Organs"); a.dataframe(df(S.organs, ["organ_id", "organ_type", "blood_group", "donor_hospital", "status"]), use_container_width=True, height=340)
    b.subheader("Recent Audit Actions"); b.dataframe(df(S.audit.to_list()[:10]), use_container_width=True, height=340)

elif page == "Register Organ":
    st.header("🧬 Register Donated Organ")
    with st.form("org"):
        t = st.selectbox("Organ type", list(MAX_HOURS)); bg = st.selectbox("Blood group", BLOOD)
        h = st.selectbox("Donor hospital", hosp_names); el = st.number_input("Minutes since harvest", 0, 600, 0)
        if st.form_submit_button("Register"):
            st.success(f"Registered {S.register_organ(t, bg, h, el)} (max viability {MAX_HOURS[t]} h)")

elif page == "Recipient Registry":
    st.header("📋 Recipient Registry")
    with st.expander("➕ Add recipient"):
        with st.form("rec"):
            n = st.text_input("Name"); c = st.columns(4)
            o = c[0].selectbox("Organ needed", list(MAX_HOURS)); b = c[1].selectbox("Blood", BLOOD)
            u = c[2].selectbox("Urgency", list(URG_RANK)); d = c[3].number_input("Waiting days", 0, 3000, 30)
            h = st.selectbox("Hospital", hosp_names)
            if st.form_submit_button("Add") and n: st.success(f"Added {S.add_recipient(n, o, b, u, d, h)}")
    f = st.columns(3)
    fo = f[0].multiselect("Organ", list(MAX_HOURS)); fb = f[1].multiselect("Blood", BLOOD); fu = f[2].multiselect("Urgency", list(URG_RANK))
    rows = [r for r in S.recipients if (not fo or r["organ_needed"] in fo) and (not fb or r["blood_group"] in fb) and (not fu or r["urgency"] in fu)]
    st.caption(f"{len(rows)} recipients"); st.dataframe(df(rows), use_container_width=True, height=450)

elif page == "Smart Matching":
    st.header("🧠 Smart Recipient Matching")
    st.info("Decision support only — final allocation remains with authorized medical authorities.")
    av = [o["organ_id"] for o in S.organs if o["status"] == "AVAILABLE"]
    if not av: st.warning("No available organs.")
    else:
        oid = st.selectbox("Available organ", av, format_func=lambda i: f"{i} — {S.find_organ(i)['organ_type']} {S.find_organ(i)['blood_group']}")
        v = S.viability(S.find_organ(oid)); st.write(f"{ICON[v['status']]} Remaining viability: **{fmt_min(v['remaining'])}**")
        ranked, rejected = S.match(oid)
        st.subheader(f"Eligible ({len(ranked)}) — ranked by urgency, then waiting time")
        if ranked:
            e = df(ranked, ["recipient_id", "name", "blood_group", "urgency", "waiting_days", "hospital"]); e.insert(0, "rank", range(1, len(e) + 1))
            st.dataframe(e.head(15), use_container_width=True)
            rid = st.selectbox("Select recipient", [r["recipient_id"] for r in ranked[:15]])
            if st.button("🚑 Start transit"): S.start_transit(oid, rid); st.success("Transit started"); st.rerun()
        with st.expander(f"❌ Rejected ({len(rejected)}) — first 30"): st.dataframe(df(rejected[:30]), use_container_width=True)

elif page == "Transit & Journey":
    st.header("📍 Cold-Chain Journey Tracking")
    ids = [o["organ_id"] for o in S.organs if o["status"] in ("IN_TRANSIT", "INTERRUPTED")]
    if not ids: st.warning("No organs in transit.")
    else:
        oid = st.selectbox("Organ", ids); o = S.find_organ(oid)
        st.write(f"**{o['organ_type']} {o['blood_group']}** → recipient **{o['recipient_id']}** • status **{o['status']}**")
        st.write("Queue (remaining route):", " ➜ ".join(S.route[oid].to_list()) or "—")
        st.dataframe(df(S.journey[oid].to_list()), use_container_width=True)
        if o["status"] == "INTERRUPTED":
            st.error("TRANSPORT INTERRUPTED — urgent handling"); 
            if st.button("Resume transit"): S.resume(oid); st.rerun()
        else:
            t = st.slider("Temperature at next checkpoint (°C)", 0.0, 15.0, 5.0, 0.5)
            if t > 8 or t < 2: st.warning("⚠ COLD-CHAIN ALERT — outside 2–8 °C")
            c = st.columns(2)
            if c[0].button("➡ Advance checkpoint"): S.advance(oid, t); st.rerun()
            r = c[1].text_input("Interruption reason", "Vehicle breakdown")
            if c[1].button("⛔ Report interruption"): S.interrupt(oid, r); st.rerun()

elif page == "Viability & Emergency":
    st.header("⏳ Viability Countdown & Emergency Queue")
    rows = S.emergency_board()
    if not rows: st.info("No organs in transit.")
    for o, v, urgent in rows:
        c = st.columns([2, 3, 2, 2])
        c[0].markdown(f"**{o['organ_id']}** {o['organ_type']} {o['blood_group']}")
        c[1].progress(float(v["pct"]), text=f"{ICON[v['status']]} {v['status']} — {fmt_min(v['remaining'])} left")
        c[2].write(o["status"]); c[3].write("🚨 EMERGENCY TRANSIT" if urgent else "Normal")

elif page == "Audit Trail":
    st.header("📋 Audit Trail (Stack — newest on top)")
    st.dataframe(df(S.audit.to_list()), use_container_width=True, height=550)

else:
    st.header("🎯 About / DSA Mapping")
    st.table(pd.DataFrame([
        ["Organ records", "Array / ArrayList"], ["Recipient records", "ArrayList"],
        ["Find compatible recipients", "Linear Search"], ["Candidate ordering", "Merge Sort"],
        ["Planned route / checkpoints", "Queue (linked list)"], ["Organ journey", "Linked List"],
        ["Recent activity / audit", "Stack"], ["Emergency handling", "Priority Queue (min-heap)"],
        ["Viability, cold-chain alert", "Computation + conditional logic"]], columns=["Requirement", "DSA"]))
    st.caption("The system generates an eligibility and priority list for simulation; final allocation remains with authorized medical authorities.")
