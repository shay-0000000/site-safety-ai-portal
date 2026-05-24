import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Safety Control Center", page_icon="🖥️", layout="wide")

if st.button("⬅️ Return to Home Gateway", type="secondary"):
    st.switch_page("home.py")

st.title("🖥️ Central Site Safety Audit Control Center")
st.write("Presentation Monitor Screen — Synchronized to cloud data feeds with integrated geo-tags.")
st.write("---")

# 🚨 PASTE THE EXACT SAME NEW NPOINT URL LINK HERE AS WELL
BIN_URL = "https://api.npoint.io/f3612bdbb4c148d88d74"

metric_col, table_col = st.columns([1, 3])

try:
    response = requests.get(BIN_URL, verify=False)
    logs = response.json() if response.status_code == 200 else []
    if not isinstance(logs, list):
        logs = []
except:
    logs = []

with metric_col:
    st.subheader("📊 Latest Node Activity")
    if st.button("🔄 Sync Live Database Data", type="primary"):
        st.rerun()
        
    if logs:
        latest = logs[0]
        st.metric(label="Latest Compliance Rating", value=latest["Compliance"])
        
        if latest["Status"] == "Safe": st.success(f"✅ Site status clear at {latest['Timestamp']}")
        elif latest["Status"] == "Warning": st.warning(f"⚠️ Safety warning active at {latest['Timestamp']}")
        else: st.error(f"🚨 Critical PPE violation logged at {latest['Timestamp']}")
        
        st.write(f"**Workers Counted:** {latest['Workers']}")
        st.write(f"**Verified Helmets:** {latest['Helmets']}")
        st.write(f"**Verified Vests:** {latest['Vests']}")
        st.write(f"📍 **Captured Location Coordinates:** {latest.get('Location (Lat, Lon)', 'Not Tracked')}")
        
        if "Preview" in latest and latest["Preview"]:
            st.write("---")
            st.write("**Latest Processed Feed Live View:**")
            st.image(latest["Preview"], use_container_width=True, caption="Latest Cloud Entry")
    else:
        st.info("Awaiting incoming camera streams from mobile node...")

with table_col:
    st.subheader("🗄️ Full Operational Database History Logs (With AI Images & GPS Coordinates)")
    if logs:
        df = pd.DataFrame(logs)
        
        cols = ['Preview'] + [col for col in df.columns if col != 'Preview']
        df = df[cols]
        
        st.dataframe(
            df, 
            width="stretch", 
            hide_index=True,
            column_config={
                "Preview": st.column_config.ImageColumn(
                    "Processed Frame Thumbnail", 
                    help="AI processed detection image with bounding boxes",
                    width="large"
                )
            }
        )
            
        st.write("---")
        if st.button("🗑️ Reset Remote Cloud Database"):
            requests.post(BIN_URL, json=[], verify=False)
            st.rerun()
    else:
        st.warning("No data entries found in the cloud server.")