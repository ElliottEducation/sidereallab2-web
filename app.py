# -------------------------
# Imports and Setup
# -------------------------
import math
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from supabase_auth import sign_in, sign_up, get_user_role, add_user_role


from supabase import create_client

SUPABASE_URL = "https://zhlhqutkuvoxlxiiulrj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpobGhxdXRrdXZveGx4aWl1bHJqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY5MzEwNTQsImV4cCI6MjA2MjUwNzA1NH0.6IMR_vD9rYr3IAwsdfCznxlu5I2ATtIAqSJvZ_3TO3s"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# -------------------------
# Streamlit App UI & Navigation
# -------------------------
st.set_page_config(page_title="SiderealLab Pro", layout="centered")

# -------------------------
# Initialize Session State Defaults and Permissions
# -------------------------
if "page" not in st.session_state:
    st.session_state.page = "login"
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = None
if "role" not in st.session_state:
    st.session_state.role = "basic"
if "is_pro" not in st.session_state:
    st.session_state.is_pro = False

# -------------------------
# Login / Sign-up Interface
# -------------------------
if not st.session_state.logged_in:
    st.title("SiderealLab Login")

    st.markdown("Please log in or sign up to continue.")

    with st.form("auth_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        auth_mode = st.radio("Action", ["Login", "Sign up"])
        submitted = st.form_submit_button("Submit")

        if submitted:
            if auth_mode == "Login":
                result = sign_in(email, password)
                if result:
                    st.session_state.logged_in = True
                    st.session_state.email = email
                    st.rerun()
                else:
                    st.error("Login failed. Please check credentials.")
            else:
                result = sign_up(email, password)
                if result:
                    add_user_role(email, "basic")  # 默认注册为 basic 用户
                    st.success("Sign-up successful! Please login now.")
                else:
                    st.error("Sign-up failed. Email may already be registered.")

    st.stop()


# 登录后获取用户权限
if st.session_state.logged_in:
    try:
        response = supabase.auth.get_user()
        user = response.get("user") if isinstance(response, dict) else getattr(response, "user", None)

        if user and isinstance(user, dict):
            role = user.get("user_metadata", {}).get("role", "basic")
        else:
            role = "basic"
    except Exception as e:
        st.error(f"Error loading user info: {e}")
        role = "basic"

    st.session_state.role = role
    st.session_state.is_pro = (role == "pro")




# 未登录禁止访问任何功能
if not st.session_state.get("logged_in", False):
    st.warning("Please log in to use SiderealLab.")
    st.stop()

# 页面导航菜单（登录后显示）
page = st.selectbox("📂 Navigate to", ["Home", "Calculator", "Charts", "Report"])

# -------------------------
# Sidebar: 当前用户权限标识
# -------------------------
st.sidebar.markdown("### Account Status")
if st.session_state.is_pro:
    st.sidebar.success("Pro Account")
else:
    st.sidebar.info("Basic Account (Free)")

# -------------------------
# Calculation Functions
# -------------------------
def get_local_radius(latitude_deg):
    return 6371.0 * math.cos(math.radians(latitude_deg))

def calculate_angular_velocity(delta_T_hours):
    return 2 * math.pi / (delta_T_hours * 3600)

def calculate_linear_speed(radius_km, angular_velocity):
    return radius_km * 1000 * angular_velocity

# -------------------------
# Chart Functions
# -------------------------
def plot_speed_vs_latitude(omega, radius, user_lat=None):
    latitudes = np.linspace(-90, 90, 181)
    speeds = radius * omega * np.cos(np.radians(latitudes))

    fig, ax = plt.subplots()
    ax.plot(latitudes, speeds, label="Speed vs Latitude", color="blue")

    if user_lat is not None:
        user_speed = radius * omega * math.cos(math.radians(user_lat))
        ax.axvline(user_lat, color="red", linestyle="--", label=f"Your Latitude: {user_lat:.2f}°")
        ax.plot(user_lat, user_speed, "ro")
        ax.annotate(f"{user_speed:.2f} km/h",
                    xy=(user_lat, user_speed),
                    xytext=(user_lat + 2, user_speed + 0.02),
                    arrowprops=dict(arrowstyle="->", color="gray"),
                    fontsize=10)

    ax.set_xlabel("Latitude (°)")
    ax.set_ylabel("Speed (km/h)")
    ax.set_title("Speed vs Latitude")
    ax.grid(True)
    ax.legend()
    fig.tight_layout()
    fig.savefig("speed_vs_latitude.png")
    return fig

def plot_radius_vs_latitude():
    latitudes = np.linspace(-90, 90, 181)
    radii = 6371.0 * np.cos(np.radians(latitudes))
    fig, ax = plt.subplots()
    ax.plot(latitudes, radii)
    ax.set_xlabel("Latitude (°)")
    ax.set_ylabel("Radius (km)")
    ax.set_title("Earth Radius vs Latitude")
    fig.tight_layout()
    return fig

# -------------------------
# PDF & CSV Export Functions (Pro only)
# -------------------------
def generate_pdf_report(latitude, delta_T, speed):
    file_path = "sidereal_report.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "SiderealLab Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Latitude: {latitude}°")
    c.drawString(50, height - 120, f"Rotation Period T: {delta_T} hours")
    c.drawString(50, height - 140, f"Calculated Speed: {speed:.2f} m/s")

    c.drawString(50, height - 180, "This report was generated using SiderealLab Pro.")
    c.save()
    return file_path

def generate_csv_data(latitude, delta_T, speed):
    df = pd.DataFrame({
        "Latitude": [latitude],
        "Rotation_Period_T": [delta_T],
        "Linear_Speed_mps": [speed]
    })
    file_path = "sidereal_data.csv"
    df.to_csv(file_path, index=False)
    return file_path

# -------------------------
# Page: Home
# -------------------------
if page == "Home":
    st.title("Welcome to SiderealLab")
    st.markdown("This tool allows you to calculate the Earth's rotational speed at any latitude.")
    
    if not st.session_state.is_pro:
        with st.expander("Why upgrade to Pro?"):
            st.markdown("""
            **Pro Features Include:**
            - Export detailed PDF reports
            - Download CSV raw data
            - Ideal for researchers, educators, and students
            """)
            st.button("Upgrade to Pro (Coming Soon)", disabled=True)

# -------------------------
# Page: Calculator
# -------------------------
elif page == "Calculator":
    st.header("Earth Rotation Speed Calculator")

    # 两列输入：纬度 与 自转周期
    col1, col2 = st.columns(2)
    with col1:
        latitude_deg = st.number_input("Latitude (°)", min_value=-90.0, max_value=90.0, value=0.0)
    with col2:
        delta_T_hours = st.number_input("Rotation Period T (hours)", min_value=20.0, max_value=30.0, value=24.0)

    # 半径与角速度计算
    radius_km = get_local_radius(latitude_deg)
    omega = calculate_angular_velocity(delta_T_hours)
    speed_mps = calculate_linear_speed(radius_km, omega)

    # 输出线速度
    st.success(f"Linear speed at {latitude_deg:.2f}°: {speed_mps:.2f} m/s")

    # 输出 local radius
    st.info(f"Local Earth Radius at {latitude_deg:.2f}°: {radius_km:.2f} km")

    # 日期时间输入
    st.subheader("Optional: Calculate ΔT between two observations")

    col3, col4 = st.columns(2)
    with col3:
        date1 = st.date_input("Observation Time 1 – Date")
        time1 = st.time_input("Observation Time 1 – Time")
    with col4:
        date2 = st.date_input("Observation Time 2 – Date")
        time2 = st.time_input("Observation Time 2 – Time")

    # 组合成 datetime 对象
    dt1 = datetime.combine(date1, time1)
    dt2 = datetime.combine(date2, time2)

    # 自动计算 ΔT 秒数（避免负值）
    delta_seconds = abs((dt2 - dt1).total_seconds())

    st.success(f"ΔT between observations: {delta_seconds:.2f} seconds")

    # 补充说明文字
    with st.expander("What is ΔT?"):
        st.markdown("ΔT is the time difference (in seconds) between two observations. "
                    "You can use it to estimate a more realistic rotation period `T` for local velocity calculations.")


# -------------------------
# Page: Charts
# -------------------------
elif page == "Charts":
    st.header("Speed vs Latitude Chart")
    latitude_deg = st.slider("Your Latitude", min_value=-90, max_value=90, value=0)
    delta_T = 24  # default for chart

    radius_km = get_local_radius(latitude_deg)
    omega = calculate_angular_velocity(delta_T)

    fig = plot_speed_vs_latitude(omega, radius_km, user_lat=latitude_deg)
    st.pyplot(fig)

    with open("speed_vs_latitude.png", "rb") as f:
        st.download_button("Download Chart as PNG", f, file_name="chart.png")

    if not st.session_state.is_pro:
        st.warning("Upgrade to Pro to export detailed PDF or CSV data.")

# -------------------------
# Page: Report (Pro Only)
# -------------------------
elif page == "Report":
    st.header("Generate Report")

    if not st.session_state.is_pro:
        st.error("This page is only available for Pro users.")
    else:
        latitude = st.number_input("Latitude (°)", min_value=-90.0, max_value=90.0, value=0.0)
        delta_T = st.number_input("Rotation Period T (hours)", min_value=20.0, max_value=30.0, value=24.0)

        radius_km = get_local_radius(latitude)
        omega = calculate_angular_velocity(delta_T)
        speed = calculate_linear_speed(radius_km, omega)

        st.success(f"Speed = {speed:.2f} m/s at latitude {latitude:.2f}°")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate PDF"):
                pdf_path = generate_pdf_report(latitude, delta_T, speed)
                with open(pdf_path, "rb") as f:
                    st.download_button("Download PDF", f, file_name="sidereal_report.pdf")

        with col2:
            if st.button("Generate CSV"):
                csv_path = generate_csv_data(latitude, delta_T, speed)
                with open(csv_path, "rb") as f:
                    st.download_button("Download CSV", f, file_name="sidereal_data.csv")


