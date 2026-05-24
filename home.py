import streamlit as st

st.set_page_config(page_title="PPE Auditor Gateway", page_icon="🏗️", layout="centered")

# Welcome Header
st.markdown("<h1 style='text-align: center;'>🏗️ Civil Safety PPE Compliance Audit Platform</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>An IoT & Deep Learning Distributed Solution for Modern Construction Management</p>", unsafe_allow_html=True)
st.write("---")

st.write("### Project Evaluation Portal")
st.write("""
This platform uses a custom-trained **YOLOv8 neural network** paired with spatial bounding box 
intersection filters to monitor real-time safety compliance on industrial jobsites. 
""")

st.write("")

# Dynamic Landing Page Columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📲 Field Capture Node")
    st.info("Designed for **Smartphones / Site Engineers**. Activates device camera feeds or image uploads to scan workers and transmit data logs to the cloud backend.")
    if st.button("Launch Mobile Scanner 🚀", use_container_width=True, type="primary"):
        st.switch_page("pages/1_📲_Mobile_Scanner.py")

with col2:
    st.markdown("### 🖥️ Management Control Center")
    st.success("Designed for **Laptops / Projector Displays**. Accesses the cloud database registry to review live metrics, risk assessments, and historical data logs.")
    if st.button("Open Control Center 📊", use_container_width=True, type="secondary"):
        st.switch_page("pages/2_🖥️_Control_Center.py")

st.write("---")
st.markdown("""
<div style='text-align: center; font-size: 13px; color: gray;'>
    <strong>IDT II Semester Evaluation Project</strong><br>
    Developed with Streamlit Cloud Engine & Ultralytics YOLOv8 Architecture
</div>
""", unsafe_allow_html=True)