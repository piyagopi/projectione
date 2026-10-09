import streamlit as st
import google.generativeai as genai
import json
from PIL import Image

st.set_page_config(page_title="ShelfSense AI", layout="centered")
st.title("📦 ShelfSense AI — Retail Audit")
st.write("Upload a photo of a retail shelf for instant inventory analysis.")

# Load API key from Secrets or Sidebar
api_key = st.secrets.get("GEMINI_API_KEY", None)

if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if not api_key:
    st.info("👈 Please enter your Gemini API Key in the sidebar or save it in Streamlit Secrets.")
    st.stop()

# Configure Google Gemini SDK
genai.configure(api_key=api_key)

uploaded_file = st.file_uploader("Upload Store Shelf Photo", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Field Rep Upload", use_container_width=True)
    
    if st.button("Run AI Audit"):
        with st.spinner("Analyzing shelf space & calculating inventory metrics..."):
            prompt = """
            You are ShelfSense AI, an enterprise computer vision auditor.
            Analyze the uploaded retail shelf image and return ONLY a valid JSON object matching this exact structure (no markdown formatting):
            {
              "audit_summary": {
                "total_items_detected": 14,
                "target_brand_share_percentage": 65,
                "out_of_stock_gaps": 2,
                "planogram_compliance_score": "88%"
              },
              "shelf_anomalies": [
                "Empty gap detected on Tier 2."
              ],
              "recommended_action": {
                "restock_sku": "Target Brand 250ml Pack",
                "suggested_reorder_qty": 24
              }
            }
            """
            
            try:
                # Use Gemini 1.5 Flash Vision
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content([prompt, image])
                
                # Clean JSON string response
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_text)
                
                st.success("Audit Complete")
                m = data["audit_summary"]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Target Share of Shelf", f"{m['target_brand_share_percentage']}%")
                    st.metric("Out of Stock Gaps", m['out_of_stock_gaps'])
                with col2:
                    st.metric("Total Items Detected", m['total_items_detected'])
                    st.metric("Planogram Compliance", m['planogram_compliance_score'])
                    
                st.subheader("⚠️ Shelf Anomalies")
                for anomaly in data["shelf_anomalies"]:
                    st.warning(anomaly)
                    
                st.subheader("🛒 Automated Restock Order")
                rec = data["recommended_action"]
                st.info(f"Reorder **{rec['suggested_reorder_qty']} units** of {rec['restock_sku']}")
                
            except Exception as e:
                st.error(f"Error details: {e}")
