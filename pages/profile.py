import streamlit as st

st.set_page_config(page_title="User Profile - Eka Care", page_icon="🩺",layout="wide", initial_sidebar_state="collapsed")

# --- Check login ---
if not st.session_state.get("is_logged_in"):
    st.error("You are not logged in. Please login first.")
    st.stop()

# --- Get full name ---
profile = st.session_state.get("user_profile", {})
full_name = f"{profile.get('first_name', '')} {profile.get('middle_name', '')} {profile.get('last_name', '')}".strip()

# --- Header and logout ---
col1, col2 = st.columns([8, 1])
with col1:
    st.markdown(f"### 👋 Welcome, **{full_name or 'User'}**!")
with col2:
    if st.button("Logout"):
        st.session_state.clear()
        st.toast("Logged out.")
        st.switch_page("main.py")

# --- Show profile info ---
with st.expander("View your ABHA profile details"):
    st.markdown(f"**ABHA Address:** {profile.get('abha_address', 'N/A')}")
    st.markdown(f"**ABHA Number:** {profile.get('abha_number', 'N/A')}")
    st.markdown(f"**DOB:** {profile.get('day_of_birth', '')}-{profile.get('month_of_birth', '')}-{profile.get('year_of_birth', '')}")
    st.markdown(f"**Gender:** {profile.get('gender', 'N/A')}")
    st.markdown(f"**Mobile:** {profile.get('mobile', 'N/A')}")
    st.markdown(f"**Pincode:** {profile.get('pincode', 'N/A')}")
    st.markdown(f"**KYC Verified:** {profile.get('kyc_verified', False)}")
    st.markdown("**Address:**")
    st.markdown(f"> {profile.get('address', 'N/A')}")