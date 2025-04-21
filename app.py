# app.py

import streamlit as st
from main import analyze_lead
import sys
import pysqlite3
sys.modules["sqlite3"] = pysqlite3


st.set_page_config(page_title="LinkedIn Lead Analyzer", layout="centered")
st.title("🔍 LinkedIn Lead Analyzer (User + Company)")

num_profiles = st.number_input("How many profiles do you want to analyze?", min_value=1, max_value=10, step=1)

inputs = []

for i in range(num_profiles):
    st.markdown(f"### Profile {i+1}")
    col1, col2 = st.columns([1, 3])
    with col1:
        profile_type = st.selectbox("Select Type", ["user", "company"], key=f"type_{i}")
    with col2:
        profile_url = st.text_input("LinkedIn Profile URL", key=f"url_{i}")
    inputs.append({"type": profile_type, "url": profile_url})

if st.button("Analyze Profiles"):
    with st.spinner("Running analysis..."):
        for idx, entry in enumerate(inputs):
            profile_type = entry["type"]
            profile_url = entry["url"]

            if not profile_url:
                st.warning(f"Profile {idx + 1}: URL is missing.")
                continue

            result, error = analyze_lead(profile_type, profile_url)
            if error:
                st.error(error)
                continue

            activity = result.tasks_output[0].pydantic.active
            summary = result.tasks_output[1].pydantic.summary_profile
            content = result.tasks_output[2].pydantic.summary_content
            alignment = result.tasks_output[3].pydantic.Alignment

            st.markdown("---")
            st.subheader(f"✅ Results for {profile_type.title()} {profile_url}")
            st.metric("📊 Activity Score", activity)
            st.markdown(f"**🧠 Profile Summary:**\n\n{summary}")
            st.markdown(f"**📝 Content Summary:**\n\n{content}")
            st.markdown(f"**🤝 HiDevs Alignment:**\n\n{alignment}")
