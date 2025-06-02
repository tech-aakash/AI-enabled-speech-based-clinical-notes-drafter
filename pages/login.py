import streamlit as st
import requests

st.set_page_config(page_title="Login via Mobile/ABHA - Eka Care")
st.title("ABHA Login (New Flow)")

# --- Access token ---
access_token = st.session_state.get("access_token", "").strip()
if not access_token:
    st.error("Access token is missing. Please visit the Token Manager page first.")
    st.stop()

# --- Step 1: Choose login method and enter identifier ---
method = st.selectbox("Select login method", options=["mobile", "abha_number", "phr_address", "aadhaar_number"])
identifier = st.text_input("Enter your identifier (e.g. mobile no, abha no, abha address, or aadhaar no)")

if st.button("Send OTP"):
    init_url = "https://api.eka.care/abdm/na/v1/profile/login/init"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "identifier": identifier,
        "method": method
    }
    try:
        response = requests.post(init_url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            st.session_state.login_txn_id = data.get("txn_id")
            st.success(data.get("hint", "OTP sent."))
            st.toast("OTP has been sent.")
        else:
            st.error(f"Failed to send OTP: {response.text}")
    except Exception as e:
        st.error(f"Exception occurred: {e}")

# --- Step 2: Enter OTP ---
if "login_txn_id" in st.session_state:
    st.divider()
    st.subheader("Verify OTP")
    otp = st.text_input("Enter OTP")

    if st.button("Verify OTP"):
        verify_url = "https://api.eka.care/abdm/na/v1/profile/login/verify"
        payload = {
            "otp": otp,
            "txn_id": st.session_state.login_txn_id
        }
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(verify_url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                st.session_state.abha_profiles = data.get("abha_profiles", [])
                st.session_state.skip_state = data.get("skip_state")
                st.session_state.verified_txn_id = data.get("txn_id")
                st.success(data.get("hint", "OTP verified."))
                st.toast("OTP verified successfully.")

                # If no further step needed and token is available, store it
                if "token" in data:
                    st.session_state.user_token = data["token"]
                    st.session_state.user_refresh_token = data.get("refresh_token")
                    st.toast("User token received.")
                    st.code(data["token"], language="text")
            else:
                st.error(f"OTP verification failed: {response.text}")
        except Exception as e:
            st.error(f"Exception occurred: {e}")

# --- Step 3: Complete login if phr_address method ---
if st.session_state.get("skip_state") == "abha_select":
    st.divider()
    st.subheader("Complete Login via ABHA Address")
    phr_address = st.selectbox("Select ABHA Address", [p.get("abha_address") for p in st.session_state.abha_profiles])

    if st.button("Complete Login"):
        complete_url = "https://api.eka.care/abdm/na/v1/profile/login/phr"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "method": "phr_address",
            "phr_address": phr_address,
            "txn_id": st.session_state.verified_txn_id
        }
        try:
            response = requests.post(complete_url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                st.session_state.user_profile = data.get("profile")
                st.session_state.user_token = data.get("token")
                st.session_state.user_refresh_token = data.get("refresh_token")
                st.success("Login successful.")

                # Display parsed user profile details nicely
                profile = st.session_state.user_profile
                with st.container():
                    st.subheader("User Profile")
                    st.write(f"**Name:** {profile.get('first_name', '')} {profile.get('middle_name', '')} {profile.get('last_name', '')}")
                    st.write(f"**ABHA Address:** {profile.get('abha_address', '')}")
                    st.write(f"**ABHA Number:** {profile.get('abha_number', '')}")
                    st.write(f"**Date of Birth:** {profile.get('day_of_birth', '')}-{profile.get('month_of_birth', '')}-{profile.get('year_of_birth', '')}")
                    st.write(f"**Gender:** {profile.get('gender', '')}")
                    st.write(f"**Mobile:** {profile.get('mobile', '')}")
                    st.write(f"**Pincode:** {profile.get('pincode', '')}")
                    st.write(f"**KYC Verified:** {profile.get('kyc_verified', '')}")
                    st.write("**Address:**")
                    st.markdown(f"> {profile.get('address', '')}")

                st.session_state.user_token = data.get("token")
                st.toast("User token stored.")
                st.write("Token stored in session_state:", st.session_state.user_token)
            else:
                st.error(f"Login failed: {response.text}")
        except Exception as e:
            st.error(f"Error during login: {e}")