import math
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def get_local_radius(latitude_deg):
    return 6371.0 * math.cos(math.radians(latitude_deg))

def calculate_angular_velocity(delta_T_hours):
    return 2 * math.pi / delta_T_hours

def calculate_linear_speed(radius_km, angular_velocity, latitude_deg):
    return radius_km * angular_velocity * math.cos(math.radians(latitude_deg))

def plot_speed_vs_latitude(omega, radius):
    latitudes = np.linspace(-90, 90, 181)
    speeds = radius * omega * np.cos(np.radians(latitudes))
    fig, ax = plt.subplots()
    ax.plot(latitudes, speeds)
    ax.set_xlabel("Latitude (°)")
    ax.set_ylabel("Speed (km/h)")
    ax.set_title("Speed vs Latitude")
    ax.grid(True)
    return fig

st.set_page_config(page_title="SiderealLab Pro", layout="centered")
st.title("🌍 SiderealLab Pro – Web Estimator")

# Mock login system
with st.sidebar:
    st.header("User Login")
    username = st.text_input("Username", value="guest")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

if login_btn:
    st.session_state["logged_in"] = True
    st.session_state["username"] = username

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please login from the sidebar to begin.")
    st.stop()

st.success(f"Welcome, {st.session_state['username']}!")

with st.form("input_form"):
    target = st.text_input("Target name", "Sirius")
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

        st.write(f"**Local radius**: {radius:.2f} km")
        st.write(f"**Angular velocity**: {omega:.6f} rad/hr")
        st.write(f"**Speed**: {speed_kmh:.2f} km/h  |  {speed_ms:.2f} m/s")

        st.pyplot(plot_speed_vs_latitude(omega, radius))

    except Exception as e:
        st.error(f"Error: {e}")
