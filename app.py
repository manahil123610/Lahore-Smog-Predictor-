import streamlit as st, pandas as pd, joblib
import matplotlib.pyplot as plt

st.set_page_config(page_title="Lahore Smog Predictor", page_icon="🌫️", layout="wide")

art = joblib.load("model.joblib")
model, FEATURES = art["model"], art["features"]

# (upper limit, name, color, advice) - US EPA PM2.5 bands
LEVELS = [
    (9,      "Good",                          "#2E9E5B", "Air is clean. Normal outdoor activity is fine."),
    (35.4,   "Moderate",                      "#E0B000", "Acceptable. Very sensitive people should limit long outdoor exertion."),
    (55.4,   "Unhealthy for sensitive groups","#F28C28", "Children, elderly and people with asthma should reduce time outdoors."),
    (125.4,  "Unhealthy",                     "#D93A3A", "Wear an N95 mask outside and avoid outdoor exercise."),
    (225.4,  "Very unhealthy",                "#8E3B9E", "Stay indoors, keep windows closed, use an air purifier if you have one."),
    (10**9,  "Hazardous",                     "#7E0023", "Emergency level. Avoid going outside."),
]
def level(v):
    for lim, name, color, tip in LEVELS:
        if v <= lim:
            return name, color, tip

# ---------- Styling ----------
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 1.5rem; max-width: 1150px;}
.hero {background: linear-gradient(135deg, #3A1C2B 0%, #E8447A 100%);
       padding: 2rem 2.2rem; border-radius: 18px; color: white; margin-bottom: 1.2rem;}
.hero h1 {margin: 0; font-size: 2.3rem; color: white;}
.hero p {margin: .4rem 0 0; opacity: .9;}
.card {border-radius: 16px; padding: 1.6rem; color: white; text-align: center;}
.card .big {font-size: 3.4rem; font-weight: 800; line-height: 1.1;}
.card .unit {font-size: 1rem; opacity: .9;}
.card .lvl {font-size: 1.3rem; font-weight: 700; margin-top: .4rem;}
.tip {background: #F7F2F4; border-left: 5px solid #E8447A; padding: .9rem 1rem;
      border-radius: 8px; margin-top: 1rem; color: #3A1C2B;}
.scale {height: 12px; border-radius: 6px; margin-top: 1.2rem; position: relative;
        background: linear-gradient(90deg,#2E9E5B,#E0B000,#F28C28,#D93A3A,#8E3B9E,#7E0023);}
.marker {position: absolute; top: -5px; width: 6px; height: 22px; background: #3A1C2B;
         border-radius: 3px; border: 1px solid white;}
div.stButton > button {background:#E8447A; color:white; border:none; border-radius:12px;
         padding:.7rem 1rem; font-weight:700; font-size:1.05rem; width:100%;}
div.stButton > button:hover {background:#3A1C2B; color:white;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🌫️ Lahore Smog Predictor</h1>
  <p>Enter today's air and weather readings to forecast tomorrow's PM2.5 in Lahore.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Presets ----------
PRESETS = {
    "Clean day":     dict(pm25=20.0,  l1=22.0,  l2=25.0,  l3=24.0,  pm10=45.0,  temp=28.0, hum=40.0, wind=14.0, pres=1005.0, month=4),
    "Typical winter":dict(pm25=80.0,  l1=75.0,  l2=70.0,  l3=65.0,  pm10=140.0, temp=18.0, hum=60.0, wind=6.0,  pres=1010.0, month=11),
    "Severe smog":   dict(pm25=220.0, l1=200.0, l2=185.0, l3=170.0, pm10=330.0, temp=12.0, hum=80.0, wind=2.0,  pres=1018.0, month=11),
}
for k, v in PRESETS["Typical winter"].items():
    st.session_state.setdefault(k, v)

def apply_preset():
    for k, v in PRESETS[st.session_state["preset"]].items():
        st.session_state[k] = v

with st.sidebar:
    st.header("Quick presets")
    st.radio("Load an example", list(PRESETS), index=1, key="preset", on_change=apply_preset)
    st.caption("Or adjust any value manually.")
    st.divider()
    st.markdown("**About**\n\nRandom Forest trained on daily Lahore data (Open-Meteo). "
                "Uses a time-based train/test split.")
    st.caption("Learning project, not an official alert.")

# ---------- Layout ----------
left, right = st.columns([1.1, 1], gap="large")

with left:
    tab1, tab2 = st.tabs(["🫁 Air quality", "🌤️ Weather"])
    with tab1:
        pm25 = st.slider("Today PM2.5 (µg/m³)", 0.0, 500.0, key="pm25", step=1.0)
        l1 = st.slider("Yesterday PM2.5", 0.0, 500.0, key="l1", step=1.0)
        l2 = st.slider("2 days ago PM2.5", 0.0, 500.0, key="l2", step=1.0)
        l3 = st.slider("3 days ago PM2.5", 0.0, 500.0, key="l3", step=1.0)
        pm10 = st.slider("Today PM10 (µg/m³)", 0.0, 800.0, key="pm10", step=1.0)
    with tab2:
        temp = st.slider("Temperature (°C)", -5.0, 50.0, key="temp", step=0.5)
        hum = st.slider("Humidity (%)", 0.0, 100.0, key="hum", step=1.0)
        wind = st.slider("Wind speed (km/h)", 0.0, 60.0, key="wind", step=0.5)
        pres = st.slider("Pressure (hPa)", 950.0, 1050.0, key="pres", step=1.0)
        month = st.select_slider("Month", options=list(range(1, 13)), key="month",
                                 format_func=lambda m: ["Jan","Feb","Mar","Apr","May","Jun",
                                                        "Jul","Aug","Sep","Oct","Nov","Dec"][m-1])
    go = st.button("Predict tomorrow")

with right:
    if go:
        row = pd.DataFrame([[pm25, pm10, temp, hum, wind, pres, l1, l2, l3, month]], columns=FEATURES)
        p = float(model.predict(row)[0])
        name, color, tip = level(p)

        st.markdown(f"""
        <div class="card" style="background:{color}">
          <div class="unit">Predicted PM2.5 tomorrow</div>
          <div class="big">{p:.0f}</div>
          <div class="unit">µg/m³</div>
          <div class="lvl">{name}</div>
        </div>
        <div class="scale"><div class="marker" style="left:{min(p/300,1)*100:.1f}%"></div></div>
        <div class="tip">💡 {tip}</div>
        """, unsafe_allow_html=True)

        vals = [l3, l2, l1, pm25, p]
        labels = ["3d ago", "2d ago", "Yesterday", "Today", "Tomorrow"]
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.bar(labels, vals, color=["#3A1C2B"]*4 + [color])
        ax.set_ylabel("PM2.5 (µg/m³)")
        ax.spines[["top", "right"]].set_visible(False)
        st.pyplot(fig)
    else:
        st.info("Set the values on the left (or pick a preset in the sidebar), then press **Predict tomorrow**.")
