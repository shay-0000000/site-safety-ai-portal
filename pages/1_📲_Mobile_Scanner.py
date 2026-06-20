import streamlit as st
from ultralytics import YOLO
from PIL import Image
import io
import base64
from datetime import datetime
import requests
import torch
import cv2
import numpy as np
from streamlit_geolocation import streamlit_geolocation # 👈 Swapped module

st.set_page_config(page_title="PPE Data Collector", page_icon="📲", layout="centered")

if st.button("⬅️ Return to Home Gateway", type="secondary"):
    st.switch_page("home.py")

st.title("📲 Universal PPE Data Collector")
st.write("Stream metrics, crisp HD processed frames, and GPS telemetry live to the control center.")
st.write("---")

# 🚨 PASTE YOUR EXACT NPOINT URL LINK HERE
BIN_URL = "https://api.npoint.io/f3612bdbb4c148d88d74"

# 🌍 AUTOMATIC GPS LOCATION CAPTURE 
st.write("### 📍 Location Telemetry")
location = streamlit_geolocation() # 👈 Simple, lightweight execution button element layer

gps_coordinates = "Not Available"
if location and location.get('latitude') is not None:
    gps_coordinates = f"{round(location['latitude'], 5)}, {round(location['longitude'], 5)}"
    st.success(f"✅ GPS Position Locked: {gps_coordinates}")
else:
    st.info("💡 Click the tracking location element module above to pass geo-tags to your table registry.")

st.write("---")

@st.cache_resource
def load_model():
    loaded_model = YOLO("best.pt")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    loaded_model.to(device)
    return loaded_model

try: 
    model = load_model()
except Exception as e: 
    st.error(f"Missing 'best.pt' file in project directory! Error: {e}"); st.stop()

def is_overlapping(gear_box, person_box):
    gx1, gy1, gx2, gy2 = gear_box
    px1, py1, px2, py2 = person_box
    return max(gx1, px1) < min(gx2, px2) and max(gy1, py1) < min(gy2, py2)

input_mode = st.radio("Select Input Source:", ["📸 Live Camera", "📁 File Upload"], horizontal=True)

source_image = None
if input_mode == "📸 Live Camera":
    picture = st.camera_input("Capture active site frame")
    if picture is not None:
        source_image = Image.open(picture)
else:
    uploaded_file = st.file_uploader("Upload a site image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        source_image = Image.open(uploaded_file)

if source_image is not None:
    with st.spinner("AI Engine running inference & rendering HD frames..."):
        results = model.predict(source_image, conf=0.40)
        result = results[0]
        names = model.names  
        
        # 🎨 GENERATE HIGH-QUALITY PROCESSED IMAGE
        processed_img_bgr = result.plot()  
        processed_img_rgb = cv2.cvtColor(processed_img_bgr, cv2.COLOR_BGR2RGB)
        processed_pil_image = Image.fromarray(processed_img_rgb)

        st.image(processed_pil_image, caption="AI Processed Live Stream Preview", width="stretch")
        
        boxes = result.boxes.xyxy.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy()
        
        people_boxes, helmet_boxes, vest_boxes = [], [], []
        for box, cls_idx in zip(boxes, classes):
            class_name = names[int(cls_idx)].lower()
            if 'person' in class_name or 'worker' in class_name: people_boxes.append(box)
            elif 'helmet' in class_name and 'no' not in class_name: helmet_boxes.append(box)
            elif 'vest' in class_name and 'no' not in class_name: vest_boxes.append(box)
                
        total_workers = len(people_boxes) or max(len(helmet_boxes), len(vest_boxes))
        protected_helmets = sum(1 for p in people_boxes if any(is_overlapping(h, p) for h in helmet_boxes)) if people_boxes else len(helmet_boxes)
        protected_vests = sum(1 for p in people_boxes if any(is_overlapping(v, p) for v in vest_boxes)) if people_boxes else len(vest_boxes)
        
        compliance_pct = int(((protected_helmets + protected_vests) / (total_workers * 2)) * 100) if total_workers > 0 else 0
        compliance_pct = min(compliance_pct, 100)
        safety_status = "Safe" if compliance_pct >= 85 else ("Warning" if compliance_pct >= 50 else "Critical")

        # 🖼️ HIGH RETENTION IMAGE STORAGE COMPRESSION ENGINE
        try:
            img_buffer = io.BytesIO()
            preview_img = processed_pil_image.copy()
            preview_img.thumbnail((800, 800)) 
            preview_img.save(img_buffer, format="JPEG", quality=85)
            base64_str = "data:image/jpeg;base64," + base64.b64encode(img_buffer.getvalue()).decode("utf-8")
        except:
            base64_str = ""

        current_time = datetime.now().strftime("%H:%M:%S (%Y-%m-%d)")
        new_log = {
            "Preview": base64_str,
            "Timestamp": current_time,
            "Location (Lat, Lon)": gps_coordinates, # 👈 Added Location metric field row to data block
            "Workers": total_workers,
            "Helmets": protected_helmets,
            "Vests": protected_vests,
            "Compliance": f"{compliance_pct}%",
            "Status": safety_status
        }
        
        # Pull Down Current Ledger
        try:
            response = requests.get(BIN_URL, verify=False)
            existing_logs = response.json() if response.status_code == 200 else []
            if not isinstance(existing_logs, list):
                existing_logs = []
        except:
            existing_logs = []
            
        existing_logs.insert(0, new_log)
        
        # Write Updated Ledger Back
        try:
            put_response = requests.post(BIN_URL, json=existing_logs[:5], verify=False)
            if put_response.status_code == 200:
                st.success(f"⚡ Successfully uploaded high-clarity data packet! Score: {compliance_pct}%")
            else:
                st.error(f"⚠️ Database rejected update. Server Code: {put_response.status_code}")
        except Exception as e:
            st.error(f"❌ Network transmission error: {e}")
