
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
from datetime import datetime

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Smart Irrigation Monitor",
    page_icon="🌱",
    layout="wide"
)

# ==========================================
# CUSTOM DESIGN
# ==========================================

st.markdown("""
<style>
.stApp {
    background: #101b18;
    color: white;
}
.block-container {
    padding-top: 2rem;
}
.metric-card {
    background: #1b2b24;
    border: 1px solid #344c3e;
    padding: 22px;
    border-radius: 15px;
    min-height: 135px;
}
.metric-label {
    color: #a5b8aa;
    font-size: 13px;
    font-weight: 600;
}
.metric-value {
    color: white;
    font-size: 34px;
    font-weight: bold;
    margin-top: 12px;
}
.metric-sub {
    color: #80e09b;
    font-size: 12px;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE
# ==========================================

if "history" not in st.session_state:
    st.session_state.history = []

if "condition" not in st.session_state:
    st.session_state.condition = "DRY SOIL"

if "counter" not in st.session_state:
    st.session_state.counter = 0

if "mode" not in st.session_state:
    st.session_state.mode = "AUTOMATIC"

if "pump_override" not in st.session_state:
    st.session_state.pump_override = False

# ==========================================
# SIMULATED SENSOR DATA
# ==========================================

def generate_sensor_data():

    st.session_state.counter += 1

    # Change soil condition every 5 seconds
    if st.session_state.counter % 5 == 0:

        st.session_state.condition = random.choices(
            ["OPEN AIR", "DRY SOIL", "WET SOIL"],
            weights=[2, 5, 4]
        )[0]

    condition = st.session_state.condition

    # Generate ADC values according to condition
    if condition == "OPEN AIR":
        raw = random.randint(950, 1024)

    elif condition == "DRY SOIL":
        raw = random.randint(501, 949)

    else:
        raw = random.randint(100, 500)

    # Generate simulated moisture percentage
    if condition == "OPEN AIR":
        moisture = 0

    elif condition == "DRY SOIL":
        moisture = int(
            max(0, min(49, (950 - raw) / 449 * 49))
        )

    else:
        moisture = int(
            max(50, min(100, 50 + (500 - raw) / 400 * 50))
        )

    # Pump logic
    if st.session_state.mode == "AUTOMATIC":
        pump = condition == "DRY SOIL"

    else:
        pump = (
            st.session_state.pump_override
            and condition == "DRY SOIL"
        )

    return {
        "raw": raw,
        "moisture": moisture,
        "condition": condition,
        "pump": pump,
        "mode": st.session_state.mode,
        "time": datetime.now()
    }

# ==========================================
# HEADER
# ==========================================

st.markdown("""
# 🌱 SMART IRRIGATION SYSTEM

### Intelligent Soil Monitoring & Water Management
""")

st.caption(
    "PYTHON SIMULATION MODE  |  LIVE SENSOR DATA  |  NO HARDWARE REQUIRED"
)

st.divider()

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("## ⚙️ System Settings")

    st.success("Simulation Active")

    st.session_state.mode = st.radio(
        "Operating Mode",
        ["AUTOMATIC", "MANUAL"]
    )

    if st.session_state.mode == "MANUAL":

        st.session_state.pump_override = st.toggle(
            "Manual Pump ON",
            value=st.session_state.pump_override
        )

        st.caption(
            "Manual pump ON is permitted only during simulated dry soil."
        )

    else:
        st.session_state.pump_override = False

    st.divider()

    st.markdown("### Sensor Thresholds")
    st.write("Open air: ADC ≥ 950")
    st.write("Dry soil: ADC 501–949")
    st.write("Wet soil: ADC ≤ 500")

    if st.button("Reset Sensor History"):
        st.session_state.history = []
        st.session_state.counter = 0
        st.rerun()

# ==========================================
# LIVE DASHBOARD
# ==========================================

@st.fragment(run_every="1s")
def live_dashboard():

    data = generate_sensor_data()

    raw = data["raw"]
    moisture = data["moisture"]
    condition = data["condition"]
    pump = data["pump"]
    mode = data["mode"]

    # Save history
    st.session_state.history.append({
        "Time": data["time"],
        "Moisture": moisture,
        "Raw ADC": raw,
        "Condition": condition,
        "Pump": "ON" if pump else "OFF"
    })

    st.session_state.history = (
        st.session_state.history[-120:]
    )

    # ======================================
    # CONNECTION STATUS
    # ======================================

    st.markdown(
        "🟢 **SIMULATION RUNNING — LIVE DATA GENERATED IN PYTHON**"
    )

    st.caption(
        "Last updated: " + data["time"].strftime("%H:%M:%S")
    )

    # ======================================
    # TOP METRICS
    # ======================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">SOIL MOISTURE</div>
            <div class="metric-value">{moisture}%</div>
            <div class="metric-sub">Simulated reading</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">RAW SENSOR VALUE</div>
            <div class="metric-value">{raw}</div>
            <div class="metric-sub">ADC reading</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:

        pump_color = "#80e09b" if pump else "#ff8585"
        pump_text = "ON" if pump else "OFF"

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">WATER PUMP</div>
            <div class="metric-value" style="color:{pump_color}">
                {pump_text}
            </div>
            <div class="metric-sub">Simulated pump status</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">CONTROL MODE</div>
            <div class="metric-value">{mode}</div>
            <div class="metric-sub">System operation</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # ======================================
    # SOIL CONDITION
    # ======================================

    st.markdown("### 🌿 SOIL CONDITION")

    if condition == "DRY SOIL":
        st.warning("DRY SOIL DETECTED — Pump ON in automatic mode.")

    elif condition == "WET SOIL":
        st.success("WET SOIL DETECTED — Pump OFF.")

    else:
        st.info("OPEN AIR DETECTED — Pump OFF.")

    # ======================================
    # GAUGE AND PUMP STATUS
    # ======================================

    left, right = st.columns(2)

    with left:

        st.markdown("### 💧 Soil Moisture Level")

        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=moisture,
                number={
                    "suffix": "%",
                    "font": {"color": "white"}
                },
                gauge={
                    "axis": {
                        "range": [0, 100],
                        "tickcolor": "white"
                    },
                    "bar": {"color": "#52d68a"},
                    "bgcolor": "#1b2b24",
                    "borderwidth": 0,
                    "steps": [
                        {
                            "range": [0, 50],
                            "color": "#713b3b"
                        },
                        {
                            "range": [50, 100],
                            "color": "#245b42"
                        }
                    ]
                }
            )
        )

        gauge.update_layout(
            height=280,
            paper_bgcolor="#101b18",
            font_color="white",
            margin=dict(t=20, b=10)
        )

        st.plotly_chart(
            gauge,
            use_container_width=True,
            key="moisture_gauge"
        )

    with right:

        st.markdown("### 🚰 Irrigation Status")

        if pump:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size:50px">🚿</div>
                <h2 style="color:#80e09b">PUMP RUNNING</h2>
                <p>Simulated irrigation is active.</p>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size:50px">🛑</div>
                <h2 style="color:#ff8585">PUMP STOPPED</h2>
                <p>Simulated irrigation is inactive.</p>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.write(f"**Soil condition:** {condition}")
        st.write(f"**Control mode:** {mode}")
        st.write(f"**Pump status:** {pump_text}")

    # ======================================
    # MOISTURE HISTORY CHART
    # ======================================

    st.divider()

    df = pd.DataFrame(st.session_state.history)

    st.markdown("### 📈 Live Moisture History")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Time"],
            y=df["Moisture"],
            mode="lines",
            name="Moisture",
            line=dict(color="#52d68a", width=3),
            fill="tozeroy"
        )
    )

    fig.update_layout(
        height=350,
        paper_bgcolor="#101b18",
        plot_bgcolor="#1b2b24",
        font_color="white",
        xaxis_title="Time",
        yaxis_title="Moisture (%)",
        yaxis=dict(range=[0, 100]),
        margin=dict(t=25, b=30)
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="moisture_history"
    )

    # ======================================
    # ADC CHART
    # ======================================

    st.markdown("### 📊 Raw Sensor Readings")

    raw_fig = go.Figure()

    raw_fig.add_trace(
        go.Scatter(
            x=df["Time"],
            y=df["Raw ADC"],
            mode="lines",
            name="Raw ADC",
            line=dict(color="#42b9e9", width=2)
        )
    )

    raw_fig.add_hline(
        y=950,
        line_dash="dash",
        line_color="#ff8585",
        annotation_text="Open air threshold"
    )

    raw_fig.add_hline(
        y=500,
        line_dash="dash",
        line_color="#80e09b",
        annotation_text="Dry / wet threshold"
    )

    raw_fig.update_layout(
        height=300,
        paper_bgcolor="#101b18",
        plot_bgcolor="#1b2b24",
        font_color="white",
        xaxis_title="Time",
        yaxis_title="ADC Value",
        yaxis=dict(range=[0, 1050]),
        margin=dict(t=30, b=30)
    )

    st.plotly_chart(
        raw_fig,
        use_container_width=True,
        key="raw_history"
    )

    # ======================================
    # RECENT SENSOR DATA
    # ======================================

    with st.expander("📋 Recent Sensor History"):

        st.dataframe(
            df.tail(20).iloc[::-1],
            use_container_width=True,
            hide_index=True
        )

    # ======================================
    # CSV DOWNLOAD
    # ======================================

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download Sensor Data CSV",
        data=csv,
        file_name="smart_irrigation_simulation.csv",
        mime="text/csv"
    )

# ==========================================
# RUN
# ==========================================

live_dashboard()

st.divider()

st.caption(
    "SMART IRRIGATION SYSTEM | PYTHON + STREAMLIT | SIMULATION MODE"
)
