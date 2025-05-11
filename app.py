import math
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from supabase_auth import sign_in, sign_up, get_user_role, add_user_role

# -------------------------
# Core calculation functions
# -------------------------
def get_local_radius(latitude_deg):
    return 6371.0 * math.cos(math.radians(latitude_deg))

def calculate_angular_velocity(delta_T_hours):
    return 2 * math.pi / delta_T_hours

def calculate_linear_speed(radius_km, angular_velocity, latitude_deg):
    return radius_km * angular_velocity * math.cos(math.radians(latitude_deg))

# -------------------------
# Chart 1 – Speed vs Latitude
# -------------------------
def plot_speed_vs_latitude(omega, radius):
    latitudes = np.linspace(-90, 90, 181)
    speeds = radius * omega * np.cos(np.radians(latitudes))
    fig, ax = plt.subplots()
    ax.plot(latitudes, speeds)
    ax.set_xlabel("Latitude (°)")
    ax.set_ylabel("Speed (km/h)")
    ax.set_title("Speed vs Latitude")
    ax.grid(True)
    fig.tight_layout()
    fig.savefig("speed_vs_latitude.png")
    return fig

def download_speed_plot():
    with open("speed_vs_latitude.png", "rb") as f:
        st.download_button(
            label="Download Speed vs Latitude Image",
            data=f,
            file_name="speed_vs_latitude.png",
            mime="image/png"
        )

# -------------------------
# Chart 2 – Radius vs Latitude
# -------------------------
def plot_radius_vs_latitude():
    latitudes = np.linspace(-90, 90, 181)
    radii = 6371.0 * np.cos(np.radians(latitudes))
    fig, ax = plt.subplots()
    ax.plot(latitudes, radii)
    ax.set_xlabel("Latitude (°)")
    ax.set_ylabel("Radius (km)")
    ax.set_title("Earth Radius vs Latitude")
    ax.grid(True)
    fig.tight_layout()
    fig.savefig("radius_vs_latitude.png")
    return fig

def download_radius_plot():
    with open("radius_vs_latitude.png", "rb") as f:
        st.download_button(
            label="Download Radius vs Latitude Image",
            data=f,
            file_name="radius_vs_latitude.png",
            mime="image/png"
        )

# -------------------------
# UI Start
# -------------------------
st.set_page_config(page_title="SiderealLab Pro", layout="centered")
st.title("🌍 SiderealLab Pro – Authenticated Web App")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

tabs = st.tabs(["🔐 Login", "📝 Register"])

# Login tab
with tabs[0]:
    if not st.session_state.logged_in:
        st.subheader("Login to your account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            auth = sign_in(email, password)
            if auth:
                st.session_state.logged_in = True
                st.session_state.email = email
                st.session_state.user_id = auth["user"]["id"]
                st.session_state.role = get_user_role(st.session_state.user_id)
                st.success(f"Login successful! Role: {st.session_state.role.upper()}")
                st.experimental_rerun()
            else:
                st.error("Login failed. Check your credentials.")

# Register tab
with tabs[1]:
    st.subheader("Create a new account")
    new_email = st.text_input("New Email")
    new_password = st.text_input("New Password", type="password")
    if st.button("Register"):
        result = sign_up(new_email, new_password)
        if "user" in result:
            user_id = result["user"]["id"]
            add_user_role(user_id)
            st.success("Registration successful! Please log in now.")
        else:
            st.error(f"Registration failed: {result.get('msg', 'Unknown error')}")

# -------------------------
# Main UI after login
# -------------------------
if st.session_state.logged_in:
    role = st.session_state.role
    st.success(f"Welcome, {st.session_state.email} (Role: {role.upper()})")

    with st.form("input_form"):
        target = st.text_input("Target Name", "Sirius")
        lat = st.number_input("Latitude (°)", value=-33.86, step=0.01)
        T1_str = st.text_input("Observation T1", "2025-05-01 22:00:00")
        T2_str = st.text_input("Observation T2", "2025-05-02 22:00:00")
        submitted = st.form_submit_button("Calculate")

    if submitted:
        try:
            T1 = datetime.strptime(T1_str, "%Y-%m-%d %H:%M:%S")
            T2 = datetime.strptime(T2_str, "%Y-%m-%d %H:%M:%S")
            delta_sec = (T2 - T1).total_seconds()
            delta_hr = delta_sec / 3600
            if delta_hr <= 0:
                st.error("T2 must be later than T1.")
                st.stop()

            radius = get_local_radius(lat)
            omega = calculate_angular_velocity(delta_hr)
            speed_kmh = calculate_linear_speed(radius, omega, lat)
            speed_ms = speed_kmh * 1000 / 3600

            st.markdown("### 📊 Results")
            st.write(f"**Local Radius:** {radius:.2f} km")
            st.write(f"**Angular Velocity:** {omega:.6f} rad/hr")
            st.write(f"**Speed:** {speed_kmh:.2f} km/h | {speed_ms:.2f} m/s")

            st.markdown("### 📈 Charts")
            st.subheader("1. Speed vs Latitude")
            st.pyplot(plot_speed_vs_latitude(omega, radius))
            download_speed_plot()

            if role == "pro":
                if st.checkbox("2. Radius vs Latitude"):
                    st.pyplot(plot_radius_vs_latitude())
                    download_radius_plot()
            else:
                st.info("Upgrade to Pro to unlock additional chart downloads.")

        except Exception as e:
            st.error(f"Error: {e}")
