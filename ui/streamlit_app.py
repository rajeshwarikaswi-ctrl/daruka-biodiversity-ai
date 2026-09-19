import streamlit as st
import requests, json

API = "http://localhost:8000"

st.set_page_config(page_title="Darukaa Biodiversity AI", layout="wide")
st.title("Darukaa.Earth - Biodiversity Intelligence")

if "sid" not in st.session_state:
    st.session_state.sid = None
if "msgs" not in st.session_state:
    st.session_state.msgs = []

with st.sidebar:
    st.subheader("Structured land context")
    soc   = st.number_input("Soil organic carbon %", 0.0, 20.0, 0.3, 0.05)
    ph    = st.number_input("Soil pH", 3.0, 10.0, 6.5, 0.1)
    rain  = st.number_input("Annual rainfall (mm)", 0.0, 4000.0, 350.0, 10.0)
    temp  = st.number_input("Mean temp (C)", -10.0, 50.0, 27.0, 0.5)
    land  = st.text_input("Land use / crop", "monoculture wheat")
    reg   = st.text_input("Region / climate", "semi-arid")
    lat   = st.number_input("Latitude (optional)", -90.0, 90.0, 0.0)
    lon   = st.number_input("Longitude (optional)", -180.0, 180.0, 0.0)
    use_geo = st.checkbox("Include coordinates", value=False)

ctx = {
    "soil_organic_carbon_pct": soc,
    "soil_ph": ph,
    "rainfall_mm_annual": rain,
    "temperature_c_avg": temp,
    "land_use": land,
    "region": reg,
}
if use_geo and (lat != 0 or lon != 0):
    ctx["latitude"], ctx["longitude"] = lat, lon

user_msg = st.chat_input("Describe your land or ask a question...")
if user_msg:
    st.session_state.msgs.append(("user", user_msg))
    payload = {"message": user_msg, "session_id": st.session_state.sid, "context": ctx}
    try:
        r = requests.post(f"{API}/chat", json=payload, timeout=180).json()
        st.session_state.sid = r["session_id"]
        st.session_state.msgs.append(("assistant", r["reply"]))
        with st.expander("Evidence retrieved (RAG)"):
            for e in r.get("retrieved_evidence", []):
                st.markdown(f"**{e.get('source')}** (score {round(e.get('score',0),2)})")
                st.caption(e.get("text", ""))
        with st.expander("Metrics snapshot"):
            st.json(r.get("metrics_snapshot", {}))
    except Exception as ex:
        st.error(f"Backend error: {ex}")

for role, msg in st.session_state.msgs:
    with st.chat_message(role):
        st.markdown(msg)
