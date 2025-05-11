import math
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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
        st.download_button("Download Speed vs Latitude Image", f, "speed_vs_latitude.png", "image/png")

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
        st.download_button("Download Radius vs Latitude Image", f, "radius_vs_latitude.png", "image/png")

# -------------------------
# Chart 3 – Speed Comparison
# -------------------------
def plot_speed_comparison(omega, lat):
    R = 6371
    radius = R * math.cos(math.radians(lat))
    speed_local = radius * omega
    speed_equator = R * omega
    fig, ax = plt.subplots()
    ax.bar(["Local", "Equator"], [speed_local, speed_equator], color=["green", "blue"])
    ax.set_ylabel("Speed (km/h)")
    ax.set_title("Local vs Equator Speed")
    fig.tight_layout()
    fig.savefig("speed_comparison.png")
    return fig

def download_speed_comparison_plot():
    with open("speed_comparison.png", "rb") as f:
        st.download_button("Download Speed Comparison Image", f, "speed_comparison.png", "image/png")


# -------------------------
# Chart 4 – Earth Cross Section
# -------------------------
def plot_earth_cross_section(lat, radius):
    fig, ax = plt.subplots()
    earth = plt.Circle((0, 0), 6371, fill=False, linestyle="--", label="Earth")
    local = plt.Circle((0, 0), radius, fill=False, linestyle="-", label="Local Radius")
    ax.add_patch(earth)
    ax.add_patch(local)
    x = radius * np.cos(np.radians(lat))
    y = radius * np.sin(np.radians(lat))
    ax.plot([0, x], [0, y], color="red", label=f"Latitude {lat}°")
    ax.set_aspect('equal')
    ax.set_xlim(-6500, 6500)
    ax.set_ylim(-6500, 6500)
    ax.set_xlabel("km")
    ax.set_ylabel("km")
    ax.set_title("Earth Cross Section View")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    fig.savefig("cross_section.png")
    return fig

def download_cross_section_plot():
    with open("cross_section.png", "rb") as f:
        st.download_button("Download Earth Cross Section Image", f, "cross_section.png", "image/png")

# -------------------------
# Chart 5 – Polar Velocity Distribution
# -------------------------
def plot_polar_velocity_distribution(omega):
    latitudes = np.linspace(-90, 90, 360)
    radii = 6371.0 * np.cos(np.radians(latitudes))
    speeds = radii * omega
    theta = np.radians(latitudes)
    fig = plt.figure()
    ax = fig.add_subplot(111, polar=True)
    ax.plot(theta, speeds)
    ax.set_title("Polar Velocity Distribution")
    fig.tight_layout()
    fig.savefig("polar_velocity.png")
    return fig

def download_polar_velocity_plot():
    with open("polar_velocity.png", "rb") as f:
        st.download_button("Download Polar Velocity Image", f, "polar_velocity.png", "image/png")

# -------------------------
# CSV Export Functions
# -------------------------
def generate_csv(data_dict):
    df = pd.DataFrame([data_dict])
    df.to_csv("sidereallab_output.csv", index=False)

def download_csv():
    with open("sidereallab_output.csv", "rb") as f:
        st.download_button(
            label="Download Results as CSV",
            data=f,
            file_name="sidereallab_output.csv",
            mime="text/csv"
        )



# -------------------------
# Streamlit Login UI
# -------------------------
st.set_page_config(page_title="SiderealLab Pro", layout="centered")
st.title("🌍 SiderealLab Pro – Authenticated App")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if not st.session_state.logged_in:
    if st.session_state.auth_mode == "login":
        st.subheader("🔐 Login")
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
                st.error("Login failed.")
        st.button("Create new account", on_click=lambda: st.session_state.update(auth_mode="register"))
        st.stop()

    elif st.session_state.auth_mode == "register":
        st.subheader("📝 Register")
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Password", type="password")
        if st.button("Register"):
            result = sign_up(new_email, new_password)
            if "user" in result:
                user_id = result["user"]["id"]
                add_user_role(user_id)
                st.success("Registration successful! Please log in.")
                st.session_state.auth_mode = "login"
                st.experimental_rerun()
            else:
                st.error(f"Registration failed: {result.get('msg', 'Unknown error')}")
        st.button("Back to Login", on_click=lambda: st.session_state.update(auth_mode="login"))
        st.stop()

# -------------------------
# Main Calculation UI
# -------------------------
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

        # Prepare CSV export
        data_dict = {
            "Target": target,
            "Latitude": lat,
            "Local Radius (km)": radius,
            "Expected Radius (km)": radius,
            "Observation T1": T1_str,
            "Observation T2": T2_str,
            "Delta T (hrs)": delta_hr,
            "Delta T (secs)": delta_sec,
            "Angular Velocity (rad/hr)": omega,
            "Speed (km/h)": speed_kmh,
            "Speed (m/s)": speed_ms
        }
        generate_csv(data_dict)
        download_csv()

        st.markdown("### 📈 Charts")
        st.subheader("1. Speed vs Latitude")
        st.pyplot(plot_speed_vs_latitude(omega, radius))
        if role == "pro":
            download_speed_plot()

        if role == "pro" and st.checkbox("2. Radius vs Latitude"):
            st.pyplot(plot_radius_vs_latitude())
            download_radius_plot()

        if role == "pro" and st.checkbox("3. Local vs Equator Speed"):
            st.pyplot(plot_speed_comparison(omega, lat))
            download_speed_comparison_plot()

        if role == "pro" and st.checkbox("4. Earth Cross Section"):
            st.pyplot(plot_earth_cross_section(lat, radius))
            download_cross_section_plot()

        if role == "pro" and st.checkbox("5. Polar Velocity Distribution"):
            st.pyplot(plot_polar_velocity_distribution(omega))
            download_polar_velocity_plot()

        if role == "lite":
            st.info("Upgrade to Pro to download charts.")

    except Exception as e:
        st.error(f"Error: {e}")


