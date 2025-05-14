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

# -------------------------
# Streamlit App UI & Navigation
# -------------------------
st.set_page_config(page_title="SiderealLab Pro", layout="centered")

# -------------------------
# Initialize Session State Defaults
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
    st.session_state.role = "lite"


# 页面导航菜单（只在已登录后可见）
if st.session_state.get("logged_in", False):
    page = st.selectbox("📂 Navigate to", ["Home", "Calculator", "Charts", "Report"])

# ✅ 自动跳转逻辑（未登录则强制跳转登录页）
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.session_state.page = "login"

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
    ax.grid(True)
    fig.tight_layout()
    fig.savefig("radius_vs_latitude.png")
    return fig

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

# -------------------------
# Export Functions
# -------------------------
def download_image(file, label):
    with open(file, "rb") as f:
        st.download_button(label, f, file_name=file, mime="image/png")

def generate_csv(data_dict):
    df = pd.DataFrame([data_dict])
    df.to_csv("sidereallab_output.csv", index=False)

def download_csv():
    with open("sidereallab_output.csv", "rb") as f:
        st.download_button("Download Results as CSV", f, "sidereallab_output.csv", "text/csv")

def generate_pdf_report(data_dict, chart_path="speed_vs_latitude.png", output_path="sidereallab_report.pdf"):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    margin = 50

    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, height - margin, "SiderealLab Pro Report")

    c.setFont("Helvetica", 12)
    c.drawString(margin, height - margin - 30, "Earth Rotation Speed Estimation")

    y = height - margin - 60
    c.setFont("Helvetica", 10)
    for key, value in data_dict.items():
        c.drawString(margin, y, f"{key}: {value}")
        y -= 14

    try:
        c.drawImage(chart_path, margin, y - 220, width=500, height=200, preserveAspectRatio=True)
    except:
        c.drawString(margin, y - 30, "Chart image not found.")

    c.setFont("Helvetica-Oblique", 8)
    c.drawString(margin, 30, "Generated by SiderealLab")
    c.save()
    return output_path

# -------------------------
# Page Functions
# -------------------------
def show_home_page():
    role = st.session_state.get("role", "lite")

    st.markdown("### 👋 Welcome to **SiderealLab**")
    st.markdown("""
SiderealLab is a lightweight scientific tool that calculates the Earth's rotational speed at your latitude,  
based on actual observation intervals. Whether you're an amateur astronomer, educator, or data enthusiast —  
you're in the right place.
""")

    if role == "lite":
        st.info("You're currently using the **Lite version**. Some features are locked. Upgrade to Pro for full access.")

    with st.expander("🆚 Free vs Pro Comparison"):
        st.markdown("""
| Feature                          | Free Version | Pro Version |
|----------------------------------|:------------:|:-----------:|
| Local speed calculator           | ✅            | ✅           |
| Annotated chart (your latitude)  | ✅            | ✅           |
| Speed vs. Latitude plot          | ✅            | ✅           |
| Earth cross-section diagram      | ❌            | ✅           |
| Polar velocity distribution      | ❌            | ✅           |
| Export PDF report                | ✅            | ✅           |
| Export CSV data                  | ✅            | ✅           |
| High-resolution chart download   | ❌            | ✅           |
""")

    if role == "lite":
        with st.expander("🚀 Unlock the Full Experience"):
            st.markdown("""
Upgrade to **SiderealLab Pro** to access all scientific tools and export features:

- Downloadable high-resolution charts (PNG, PDF)  
- Detailed Earth cross-section & polar velocity maps  
- Custom observation periods & comparative tools  
- Personalised data reports for scientific records  
- Premium feature access for educators & researchers
""")
            upgrade_url = "https://your-upgrade-link.com"  # Replace with actual URL
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("**Ready to unlock the stars?**")
            with col2:
                st.markdown(f"[💎 Upgrade Now]({upgrade_url})", unsafe_allow_html=True)

    with st.expander("🌏 Why Does Earth's Rotation Speed Matter?"):
        st.markdown("""
Every place on Earth is spinning — but not at the same speed.  
Your latitude determines your velocity through space.

- At the equator: ~1670 km/h  
- In Sydney: ~1380 km/h  
- In Reykjavík: ~800 km/h

This tool lets you visualize and calculate your local motion —  
**You're not standing still. You're moving with the Earth.**
""")

    st.markdown("### 🧭 Features at a Glance")
    cols = st.columns(3)
    features = [
        ("🌀", "Local Speed Calculation", "Instant speed based on latitude & time"),
        ("📈", "Latitude Speed Chart", "Visualize how speed varies with latitude"),
        ("📤", "PDF/CSV Export", "Download reports for research or class"),
    ]
    for i, (icon, title, desc) in enumerate(features):
        with cols[i]:
            st.markdown(f"{icon} **{title}**  \n{desc}")

    st.markdown("---")
    st.markdown("📬 Want to receive updates about SiderealLab Pro? Join our [mailing list](https://example.com)!")


def show_calculator_page():
    if "email" not in st.session_state:
        st.warning("Please login to use the calculator.")
        return

    role = st.session_state.get("role", "lite")
    st.subheader("🧮 Local Rotational Speed Calculator")

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
                return

            radius = get_local_radius(lat)
            omega = calculate_angular_velocity(delta_hr)
            speed_ms = calculate_linear_speed(radius, omega)
            speed_kmh = speed_ms * 3600 / 1000

            st.markdown("### 📊 Results")
            st.write(f"**Local Radius:** {radius:.2f} km")
            st.write(f"**Angular Velocity:** {omega:.6e} rad/s")
            st.write(f"**Speed:** {speed_kmh:.2f} km/h | {speed_ms:.2f} m/s")

            data_dict = {
                "Target": target,
                "Latitude": lat,
                "Local Radius (km)": radius,
                "Observation T1": T1_str,
                "Observation T2": T2_str,
                "Delta T (hrs)": delta_hr,
                "Delta T (secs)": delta_sec,
                "Angular Velocity (rad/s)": omega,
                "Speed (km/h)": speed_kmh,
                "Speed (m/s)": speed_ms
            }

            generate_csv(data_dict)
            generate_pdf_report(data_dict)
            download_csv()
            with open("sidereallab_report.pdf", "rb") as f:
                st.download_button("Download PDF Report", f, "sidereallab_report.pdf", "application/pdf")

            st.markdown("### 📈 Charts")
            st.pyplot(plot_speed_vs_latitude(omega, radius, user_lat=lat))

            if role == "pro":
                download_image("speed_vs_latitude.png", "Download Speed vs Latitude Image")

                if st.checkbox("Radius vs Latitude"):
                    st.pyplot(plot_radius_vs_latitude())
                    download_image("radius_vs_latitude.png", "Download Radius Image")

                if st.checkbox("Equator vs Local Speed"):
                    st.pyplot(plot_speed_comparison(omega, lat))
                    download_image("speed_comparison.png", "Download Speed Comparison")

                if st.checkbox("Earth Cross Section"):
                    st.pyplot(plot_earth_cross_section(lat, radius))
                    download_image("cross_section.png", "Download Earth Cross Section")

                if st.checkbox("Polar Velocity Distribution"):
                    st.pyplot(plot_polar_velocity_distribution(omega))
                    download_image("polar_velocity.png", "Download Polar Velocity")

            else:
                st.info("Upgrade to Pro to unlock all chart downloads and advanced reports.")

        except Exception as e:
            st.error(f"Error: {e}")

# -------------------------
# Page Router (after login)
# -------------------------
if st.session_state.page == "main":
    role = st.session_state.get("role", "lite")
    st.success(f"Welcome, {st.session_state.email} (Role: {role.upper()})")

    if page == "Home":
        show_home_page()
    elif page == "Calculator":
        show_calculator_page()
    elif page == "Charts":
        st.info("Charts module coming soon...")  # 可占位或引入 show_charts_page()
    elif page == "Report":
        st.info("Report module coming soon...")


# -------------------------
# Page: Login or Register
# -------------------------
if st.session_state.page == "login":
    st.markdown("""
    # 🌍 **SiderealLab**
    #### _Discover how fast you're spinning on Earth_
    """)

    if st.session_state.auth_mode == "login":
        st.subheader("🔐 Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            auth = sign_in(email, password)
            if auth:
                st.session_state.logged_in = True
                st.session_state.email = email
                st.session_state.user_id = auth.id
                st.session_state.role = get_user_role(auth.id)
                st.session_state.page = "main"
                st.success(f"Login successful! Role: {st.session_state.role.upper()}")
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
            if result is not None and hasattr(result, "id"):
                user_id = result.id
                add_user_role(user_id)
                st.success("✅ Registration successful! You can now log in.")
                st.session_state.auth_mode = "login"
            else:
                st.error(f"Registration may have failed: {result}")
        st.button("Back to Login", on_click=lambda: st.session_state.update(auth_mode="login"))
        st.stop()

# -------------------------
# Logout and Footer
# -------------------------
if st.session_state.get("logged_in", False):
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔓 Log Out"):
            st.session_state.clear()
            st.experimental_rerun()
    with col2:
        st.caption("Made with 🌎 by Elliott • [GitHub](https://github.com/yourname/sidereallab)")

else:
    st.info("Please log in above to access all features.")


