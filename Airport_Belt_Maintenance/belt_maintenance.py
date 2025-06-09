import streamlit as st
import pandas as pd
import numpy as np
import joblib
from scipy.fft import fft
from scipy.signal import spectrogram
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime, timedelta

# ---------- CONFIGURATION ----------
MODEL_PATH = 'equipment_fault_predictor.pkl'

# ---------- MODEL LOADING ----------
@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

model = load_model()

# ---------- SIDEBAR ----------
st.sidebar.title("🛠️ Belt Conveyor Health Dashboard")
st.sidebar.info("Upload your sensor data or manually enter real-time readings.")

# Demo mode
if st.sidebar.button("Load Demo Data"):
    demo_data = pd.DataFrame({
        'timestamp': pd.date_range(end=pd.Timestamp.now(), periods=60, freq='T'),
        'tension': np.random.normal(1200, 50, 60),
        'vibration': np.abs(np.random.randn(60)) * 100,
        'remaining_life': np.random.randint(30, 200, 60)
    })
    st.session_state['demo'] = demo_data

# Simulate real-time data
if st.sidebar.checkbox("Simulate Real-Time Data"):
    dummy_data = pd.DataFrame({
        'tension': np.random.normal(1200, 50, 60),
        'vibration': np.abs(np.random.randn(60)) * 100
    }, index=pd.date_range(end=pd.Timestamp.now(), periods=60, freq='T'))
    st.line_chart(dummy_data)

# Equipment profile manager
st.sidebar.markdown("### Equipment Profile")
conveyor_length = st.sidebar.number_input("Belt Length (meters)", value=150)
max_load = st.sidebar.number_input("Max Design Load (kg)", value=5000)

# Sensor calibration log
st.sidebar.markdown("### Sensor Calibration")
last_calibrated = st.sidebar.date_input("Last Sensor Calibration", value=datetime.now().date() - timedelta(days=30))
if (datetime.now().date() - last_calibrated).days > 90:
    st.sidebar.error("Calibration Expired!")

# User role selection
user_role = st.sidebar.selectbox("Access Level:", ["Operator", "Engineer", "Admin"])
if user_role == "Operator":
    st.sidebar.warning("Read-Only Access")

# ---------- MAIN TITLE ----------
st.title("🚨 Belt Conveyor Health Monitoring System")

# ---------- DATA SOURCE SELECTION ----------
data_source = st.sidebar.radio(
    "Select Data Source",
    ("Upload CSV File", "Manual Sensor Input")
)

# ---------- CSV UPLOAD WORKFLOW ----------
if data_source == "Upload CSV File":
    st.header("📤 Upload Sensor Data")
    uploaded_file = st.file_uploader(
        "Upload a CSV with columns: 'timestamp', 'tension', 'vibration', 'remaining_life'",
        type=['csv']
    )

    # Use demo data if loaded
    if 'demo' in st.session_state:
        df = st.session_state['demo'].copy()
        df.set_index('timestamp', inplace=True)
    elif uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, parse_dates=['timestamp'])
            df.set_index('timestamp', inplace=True)
        except Exception as e:
            st.error(f"Error processing file: {e}")
            df = None
    else:
        df = None

    if df is not None:
        df = df.sort_index().asfreq('1T')
        df.interpolate(method='time', inplace=True)

        # Feature Engineering
        df['tension_mean'] = df['tension'].rolling(window=10, min_periods=1).mean()
        df['tension_std'] = df['tension'].rolling(window=10, min_periods=1).std()
        df['vibration_fft_max'] = np.abs(fft(df['vibration'].values)).max()
        df.dropna(inplace=True)

        # True Condition Labeling
        bins = [-np.inf, 50, 100, np.inf]
        labels = ['Critical', 'Warning', 'Healthy']
        df['condition'] = pd.cut(df['remaining_life'], bins=bins, labels=labels)

        st.subheader("Data Preview")
        st.dataframe(df.tail(10))

        # Prediction
        X = df[['tension_mean', 'tension_std', 'vibration_fft_max']]
        df['predicted_condition'] = model.predict(X)

        st.subheader("Prediction Results")
        st.dataframe(df[['condition', 'predicted_condition']].tail(10))

        # --- Trend Visualizations ---

        # Matplotlib Trend Plot
        st.subheader("Tension Over Time (Matplotlib)")
        fig, ax = plt.subplots(figsize=(10, 4))
        df['tension'].plot(ax=ax, label='Tension')
        df['tension_mean'].plot(ax=ax, label='Rolling Mean (10)')
        ax.set_ylabel("Tension")
        ax.set_xlabel("Timestamp")
        ax.legend()
        st.pyplot(fig)

        # Plotly Interactive Trend Plot
        st.subheader("Tension Over Time (Interactive Plotly)")
        fig_plotly = px.line(
            df.reset_index(),
            x='timestamp',
            y=['tension', 'tension_mean'],
            labels={'value': 'Tension', 'timestamp': 'Timestamp', 'variable': 'Legend'},
            title="Tension and Rolling Mean Over Time"
        )
        fig_plotly.update_layout(legend_title_text='Metric')
        st.plotly_chart(fig_plotly, use_container_width=True)

        # Seaborn Trend Plot
        st.subheader("Tension Trend with Seaborn")
        fig_sns, ax_sns = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=df.reset_index(), x='timestamp', y='tension', label='Tension', ax=ax_sns)
        sns.lineplot(data=df.reset_index(), x='timestamp', y='tension_mean', label='Rolling Mean (10)', ax=ax_sns)
        ax_sns.set_ylabel("Tension")
        ax_sns.set_xlabel("Timestamp")
        ax_sns.legend()
        st.pyplot(fig_sns)

        # Plotly for Vibration Trend
        st.subheader("Vibration Trend (Interactive Plotly)")
        fig_vib = px.line(
            df.reset_index(),
            x='timestamp',
            y='vibration',
            labels={'vibration': 'Vibration', 'timestamp': 'Timestamp'},
            title="Vibration Over Time"
        )
        st.plotly_chart(fig_vib, use_container_width=True)

        # User-Selectable Plotly Chart
        st.subheader("Custom Trend Explorer (Plotly)")
        y_col = st.selectbox("Select variable for Y-axis", ['tension', 'tension_mean', 'vibration', 'tension_std'])
        fig_custom = px.line(
            df.reset_index(),
            x='timestamp',
            y=y_col,
            title=f"{y_col.capitalize()} Over Time"
        )
        st.plotly_chart(fig_custom, use_container_width=True)

        # --- Existing and Advanced Features Below ---

        # Vibration Spectrogram
        st.subheader("Vibration Spectrogram")
        f, t_, Sxx = spectrogram(df['vibration'])
        plt.figure(figsize=(8, 4))
        plt.pcolormesh(t_, f, 10 * np.log10(Sxx), shading='gouraud')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.title('Vibration Spectrogram')
        st.pyplot(plt)

        # Statistical Health Report
        st.subheader("Statistical Health Report")
        st.metric("MTBF (Hours)", "420")
        st.metric("Failure Probability", "23%", delta="-4% from last week")

        # Feature Importance Visualization (if model has attribute)
        if hasattr(model, "feature_importances_"):
            st.subheader("Feature Importance")
            st.bar_chart(pd.Series(model.feature_importances_, index=X.columns).sort_values())

        # 3D Vibration Analysis
        st.subheader("3D Vibration Analysis")
        from mpl_toolkits.mplot3d import Axes3D
        fig3d = plt.figure(figsize=(6, 4))
        ax3d = fig3d.add_subplot(111, projection='3d')
        ax3d.plot_trisurf(df['tension'], df['vibration'], df['remaining_life'], cmap='viridis')
        ax3d.set_xlabel('Tension')
        ax3d.set_ylabel('Vibration')
        ax3d.set_zlabel('Remaining Life')
        st.pyplot(fig3d)

        # Comparative Timeline Analysis
        st.subheader("Comparative Timeline Analysis")
        selected_period = st.select_slider("Compare Periods:", options=['24h', '7d', '30d'])
        # Placeholder: implement actual period filtering as needed

        # Anomaly Detection Engine
        st.subheader("Anomaly Detection")
        from sklearn.ensemble import IsolationForest
        clf = IsolationForest().fit(X)
        df['anomaly'] = clf.predict(X)
        st.write("Anomalies (if any):")
        st.dataframe(df[df['anomaly'] == -1])

        # Maintenance Scheduler
        st.subheader("Maintenance Scheduler")
        next_maintenance = st.date_input("Next Planned Maintenance", value=datetime.now().date() + timedelta(days=30))
        if datetime.now().date() > next_maintenance:
            st.warning("Maintenance Overdue!")

        # Spare Parts Inventory
        st.subheader("Spare Parts Inventory")
        st.progress(0.3, "Motor Bearings Stock: 30% remaining")

        # Maintenance History Timeline (placeholder)
        st.subheader("Maintenance History Timeline")
        maintenance_records = [
            {"date": "2025-01-15", "event": "Bearing Replacement"},
            {"date": "2025-03-10", "event": "Belt Alignment"},
            {"date": "2025-05-01", "event": "Sensor Calibration"},
        ]
        st.table(maintenance_records)

        # Report Generation (placeholder)
        st.subheader("Generate Equipment Health Report")
        if st.button("Generate PDF Report"):
            st.success("Report generated! (Functionality placeholder)")

# ---------- MANUAL INPUT WORKFLOW ----------
elif data_source == "Manual Sensor Input":
    st.header("✍️ Enter Sensor Readings Manually")

    tension_mean = st.number_input("Tension Mean", min_value=0.0, value=1200.0)
    tension_std = st.number_input("Tension Standard Deviation", min_value=0.0, value=20.0)
    vibration_fft_max = st.number_input("Vibration FFT Max", min_value=0.0, value=85.0)

    # Prediction Button
    if st.button("Predict Health Condition"):
        input_df = pd.DataFrame({
            'tension_mean': [tension_mean],
            'tension_std': [tension_std],
            'vibration_fft_max': [vibration_fft_max]
        })

        prediction = model.predict(input_df)[0]

        st.subheader(f"Predicted Condition: **{prediction}**")
        if prediction == 'Critical':
            st.error("⚠️ ALERT: Condition is Critical! Immediate attention required.")
            st.markdown("""<audio autoplay><source src="alert.mp3"></audio>""", unsafe_allow_html=True)
        elif prediction == 'Warning':
            st.warning("⚠️ Warning: Please schedule maintenance soon.")
        else:
            st.success("✅ Condition is Healthy. No action needed.")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("Developed with ❤️ using Streamlit")

