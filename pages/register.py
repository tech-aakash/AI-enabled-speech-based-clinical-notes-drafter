import streamlit as st
import requests

st.set_page_config(page_title="ABHA Registration - Eka Care")
st.title("Register with Aadhaar")

access_token = st.session_state.get("access_token", "").strip()
if not access_token:
    st.error("Access token is missing. Please visit the Token Manager page first.")
    st.stop()

# Step 1: Aadhaar Number Entry
aadhaar_number = st.text_input("Enter Aadhaar Number", max_chars=12)

if st.button("Send OTP to Aadhaar-linked Mobile"):
    init_url = "https://api.eka.care/abdm/na/v1/registration/aadhaar/init"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {"aadhaar_number": aadhaar_number}

    try:
        res = requests.post(init_url, json=payload, headers=headers)
        if res.status_code == 200:
            data = res.json()
            st.session_state.registration_txn_id = data.get("txn_id")
            st.success(data.get("hint", "OTP sent successfully."))
            st.toast("OTP sent to Aadhaar-linked mobile.")
        else:
            st.error(f"Failed to send OTP: {res.text}")
    except Exception as e:
        st.error(f"Error: {e}")

# Step 2: OTP Verification
if "registration_txn_id" in st.session_state:
    st.divider()
    st.subheader("Verify OTP")
    otp = st.text_input("Enter OTP", max_chars=6)
    mobile = st.text_input("Enter Registered Mobile Number", max_chars=10)

    if st.button("Verify and Register"):
        verify_url = "https://api.eka.care/abdm/na/v1/registration/aadhaar/verify"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "mobile": mobile,
            "otp": otp,
            "txn_id": st.session_state.registration_txn_id
        }

        try:
            res = requests.post(verify_url, json=payload, headers=headers)
            if res.status_code == 200:
                data = res.json()
                st.session_state.user_profile = data.get("profile")
                st.session_state.user_token = data.get("token")

                st.success("Account created successfully.")
                profile = st.session_state.user_profile
                st.subheader("Registered Profile")
                st.write(f"**Name:** {profile.get('first_name')} {profile.get('middle_name')} {profile.get('last_name')}")
                st.write(f"**ABHA Address:** {profile.get('abha_address')}")
                st.write(f"**ABHA Number:** {profile.get('abha_number')}")
                st.write(f"**DOB:** {profile.get('day_of_birth')}-{profile.get('month_of_birth')}-{profile.get('year_of_birth')}")
                st.write(f"**Gender:** {profile.get('gender')}")
                st.write(f"**Mobile:** {profile.get('mobile')}")
                st.write(f"**Pincode:** {profile.get('pincode')}")
                st.write("**Address:**")
                st.markdown(f"> {profile.get('address')}")

                st.toast("User token stored.")
            else:
                st.error(f"OTP verification failed: {res.text}")
        except Exception as e:
            st.error(f"Exception during verification: {e}")