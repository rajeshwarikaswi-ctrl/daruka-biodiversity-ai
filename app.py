import streamlit as st
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from app.schemas import LandContext
from app.reasoning.engine import reason
from app.conversation.clarifier import clarifying_questions

st.set_page_config(page_title="Darukaa Biodiversity AI", layout="wide")
st.title("Darukaa.Earth - Biodiversity Intelligence")
st.caption("Evidence-grounded AI for land managers. Every recommendation cites FAO/IPCC/IPBES sources.")

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

ctx = {
    "soil_organic_carbon_pct": soc,
    "soil_ph": ph,
    "rainfall_mm_annual": rain,
    "temperature_c_avg": temp,
    "land_use": land,
    "region": reg,
}

user_msg = st.chat_input("Describe your land or ask a question...")
if user_msg:
    st.session_state.msgs.append(("user", user_msg))
    with st.spinner("Reasoning over soil-water-biodiversity dynamics..."):
        try:
            land_ctx = LandContext(**ctx)
            result = reason(land_ctx, user_msg)
            questions = clarifying_questions(land_ctx)
            lines = []
            if questions:
                lines.append("**To sharpen my advice, I need a bit more context:**")
                lines += [f"- {q}" for q in questions]
                lines.append("")
            for i, r in enumerate(result["recommendations"], 1):
                lines.append(f"### {i}. {r.action}")
                lines.append(f"*Confidence: {r.confidence} | Horizon: {r.time_horizon}*")
                lines.append(f"**Why:** {r.rationale}")
                lines.append(f"**Impacted metrics:** {', '.join(r.impacted_metrics)}")
                lines.append(f"**Expected effect:** {r.expected_effect}")
                lines.append(f"**References:** {'; '.join(r.references)}")
                lines.append("")
            reply = "\n\n".join(lines) if lines else "Please share more context about your land."
            st.session_state.msgs.append(("assistant", reply))
            st.session_state["last_evidence"] = result["retrieved_evidence"]
            st.session_state["last_snapshot"] = result["metrics_snapshot"]
        except Exception as e:
            st.session_state.msgs.append(("assistant", f"Error: {e}"))

for role, msg in st.session_state.msgs:
    with st.chat_message(role):
        st.markdown(msg)

if st.session_state.get("last_evidence"):
    with st.expander("Evidence retrieved (RAG)"):
        for e in st.session_state["last_evidence"]:
            st.markdown(f"**{e.get('source')}** (score {round(e.get('score',0), 2)})")
            st.caption(e.get("text", ""))

if st.session_state.get("last_snapshot"):
    with st.expander("Metrics snapshot"):
        st.json(st.session_state["last_snapshot"])
