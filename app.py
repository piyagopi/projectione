import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
import datetime
import plotly.express as px
from PIL import Image
import os

# --- Configuration & Setup ---
st.set_page_config(page_title="ShelfSense AI - Complete Bakery OS", layout="wide")

# Persistent API Key Setup
# Try to get the API key from Streamlit secrets first, then environment variables
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

# If no key is found automatically, provide a hardcoded fallback (Replace "YOUR_API_KEY_HERE" with your actual key before sharing)
if not api_key:
    # WARNING: Hardcoding keys is a security risk. Use Streamlit Secrets for production.
    api_key = "YOUR_API_KEY_HERE" 

if api_key == "YOUR_API_KEY_HERE" or not api_key:
     st.warning("⚠️ Gemini API Key is missing. The Vision AI features will run in Demo/Fallback mode.")
else:
    genai.configure(api_key=api_key)

# --- App Styling ---
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #E67E22; font-weight: bold; margin-bottom: 0px;}
    .sub-header { font-size: 1.2rem; color: #7F8C8D; margin-bottom: 20px;}
    .metric-card { background-color: #F8F9F9; padding: 20px; border-radius: 10px; border: 1px solid #EAEDED; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🥐 ShelfSense AI — Complete Bakery OS</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Venkateshwara Bakery Management Dashboard</p>', unsafe_allow_html=True)

# --- Sidebar Navigation ---
menu = ["📦 Dynamic Pricing Audit", "💰 Billing & Sales", "👥 HR Management", "📈 Analytics Dashboard"]
choice = st.sidebar.selectbox("Navigate OS", menu)

# --- Helper function for mock data ---
def get_mock_billing_data():
    dates = pd.date_range(end=datetime.date.today(), periods=30)
    data = []
    import random
    for date in dates:
        for _ in range(random.randint(10, 30)):
            item = random.choice(["Egg Puff", "Veg Puff", "Black Forest", "Milk Bread", "Tea Cake"])
            price = {"Egg Puff": 25, "Veg Puff": 20, "Black Forest": 70, "Milk Bread": 45, "Tea Cake": 35}[item]
            qty = random.randint(1, 5)
            data.append({"Date": date, "Item": item, "Quantity": qty, "Revenue": price * qty})
    return pd.DataFrame(data)

# --- Module 1: Dynamic Pricing (The Core Feature) ---
if choice == "📦 Dynamic Pricing Audit":
    st.subheader("📸 Evening Inventory & Pricing Engine")
    st.write("Upload a 7:00 PM photo of the display case to calculate sunk costs and generate WhatsApp flash sales.")
    
    uploaded_file = st.file_uploader("Upload Display Case Photo", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        col1, col2 = st.columns([1, 2])
        with col1:
            image = Image.open(uploaded_file)
            image.thumbnail((400, 400))
            st.image(image, caption="Current Display Status", use_container_width=True)
        
        with col2:
            if st.button("Run AI Audit", type="primary"):
                with st.spinner("Analyzing perishable shelf life & calculating optimal markdown..."):
                    
                    data = None
                    # Attempt AI Call if key exists and isn't the placeholder
                    if api_key and api_key != "YOUR_API_KEY_HERE":
                        prompt = """
                        You are an AI inventory and pricing auditor for Venkateshwara Bakery.
                        Analyze the uploaded photo of the bakery display case taken near closing time.
                        Identify unsold perishable items (e.g., veg puffs, egg puffs, pastries). 
                        Calculate the estimated sunk cost if these items spoil, and recommend a dynamic discount percentage.
                        
                        Return ONLY valid JSON (no markdown):
                        {
                          "inventory_summary": { "unsold_perishables_count": 24, "primary_items_detected": "Veg Puffs, Black Forest", "value_at_risk_inr": 850 },
                          "pricing_recommendation": { "suggested_discount_percentage": 30, "rationale": "High volume remaining." },
                          "whatsapp_alert": "30% OFF till 9 PM 🥐 Egg/Veg Puffs | Venkateshwara Bakery. Show this msg."
                        }
                        """
                        try:
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            response = model.generate_content([prompt, image])
                            clean_text = response.text.replace("```json", "").replace("```", "").strip()
                            data = json.loads(clean_text)
                        except Exception as e:
                            st.warning(f"AI API Call failed (using fallback data). Error: {e}")
                    
                    # Fallback data if API fails or key is missing
                    if not data:
                        data = {
                          "inventory_summary": {
                            "unsold_perishables_count": 18,
                            "primary_items_detected": "Egg Puffs, Paneer Puffs, Cream Buns",
                            "value_at_risk_inr": 630
                          },
                          "pricing_recommendation": {
                            "suggested_discount_percentage": 35,
                            "rationale": "Moderate volume of perishables. A 35% markdown clears inventory rapidly while recovering cost."
                          },
                          "whatsapp_alert": "🚨 35% OFF till 9 PM 🥐 Fresh Puffs & Buns! | Venkateshwara Bakery, Marathahalli. Show this msg."
                        }
                        
                    # --- Render Results ---
                    st.success("Audit Complete")
                    inv = data["inventory_summary"]
                    rec = data["pricing_recommendation"]
                    
                    m1, m2 = st.columns(2)
                    m1.metric("Value at Risk (Spoilage)", f"₹{inv['value_at_risk_inr']}")
                    m2.metric("Suggested Discount", f"{rec['suggested_discount_percentage']}%")
                    
                    st.info(f"**Strategy:** {rec['rationale']}")
                    
                    st.subheader("📱 WhatsApp Broadcast Alert")
                    st.text_input("Copy & Paste:", value=data["whatsapp_alert"])
                    st.caption("Keep it under 2 lines so customers can read it on their lock screens.")

# --- Module 2: Billing System ---
elif choice == "💰 Billing & Sales":
    st.subheader("🧾 Fast-Track Billing POS")
    
    # Simple Session State for Cart
    if 'cart' not in st.session_state:
        st.session_state.cart = []
        
    menu_items = {"Egg Puff": 25, "Veg Puff": 20, "Black Forest": 70, "Milk Bread": 45}
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("Add Items to Cart:")
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("Egg Puff (₹25)"): st.session_state.cart.append({"Item": "Egg Puff", "Price": 25})
        if c2.button("Veg Puff (₹20)"): st.session_state.cart.append({"Item": "Veg Puff", "Price": 20})
        if c3.button("Pastry (₹70)"): st.session_state.cart.append({"Item": "Black Forest", "Price": 70})
        if c4.button("Bread (₹45)"): st.session_state.cart.append({"Item": "Milk Bread", "Price": 45})
        
        if st.button("Clear Cart", type="secondary"):
            st.session_state.cart = []
            st.rerun()

    with col2:
        st.write("Current Cart:")
        total = 0
        if not st.session_state.cart:
            st.info("Cart is empty")
        else:
            for item in st.session_state.cart:
                st.write(f"- {item['Item']}: ₹{item['Price']}")
                total += item['Price']
            st.divider()
            st.subheader(f"Total: ₹{total}")
            if st.button("Complete Sale (UPI/Cash)", type="primary"):
                st.success(f"Sale of ₹{total} recorded!")
                st.session_state.cart = []
                st.rerun()

# --- Module 3: HR Management ---
elif choice == "👥 HR Management":
    st.subheader("👨‍🍳 Staff & Payroll Management")
    
    hr_data = pd.DataFrame({
        "Employee Name": ["Ramesh (Head Baker)", "Lakshmi (Cashier)", "Suresh (Asst Baker)", "Kumar (Helper)"],
        "Role": ["Production", "Front Counter", "Production", "Support"],
        "Base Salary (₹)": [18000, 15000, 15000, 12000],
        "Days Present": [28, 29, 26, 30],
        "7 PM Routine Bonus": ["No", "Yes (+₹500)", "No", "No"]
    })
    
    st.dataframe(hr_data, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Monthly Payroll", f"₹{hr_data['Base Salary (₹)'].sum() + 500}")
    with col2:
        st.metric("Total Staff", len(hr_data))

# --- Module 4: Analytics Dashboard ---
elif choice == "📈 Analytics Dashboard":
    st.subheader("📊 Business Intelligence")
    
    df = get_mock_billing_data()
    
    # Top Level Metrics
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("30-Day Revenue", f"₹{df['Revenue'].sum():,}")
    kpi2.metric("Total Items Sold", df['Quantity'].sum())
    kpi3.metric("Top SKU", df.groupby('Item')['Quantity'].sum().idxmax())
    
    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.write("Revenue Trend (Last 30 Days)")
        daily_rev = df.groupby('Date')['Revenue'].sum().reset_index()
        fig_line = px.line(daily_rev, x='Date', y='Revenue', color_discrete_sequence=['#E67E22'])
        st.plotly_chart(fig_line, use_container_width=True)
        
    with c2:
        st.write("Sales Distribution by Item")
        item_qty = df.groupby('Item')['Quantity'].sum().reset_index()
        fig_pie = px.pie(item_qty, values='Quantity', names='Item', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)
