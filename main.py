import streamlit as st
import requests
import time
import os
from dotenv import load_dotenv


# Set page configuration
st.set_page_config(page_title="Eka Care App", layout="wide", initial_sidebar_state="collapsed")
st.logo(image="ekacare logo.png",size="large")
st.subheader("Revolutionizing Healthcare with Health AI")
st.text("Eka Care provides integrated solutions for Doctor, Patients, Developers & Hospitals.")
# Initialize session state
if "access_token" not in st.session_state:
    st.session_state.access_token = ""
if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = ""
if "last_refresh_time" not in st.session_state:
    st.session_state.last_refresh_time = 0

load_dotenv() 

client_id = os.getenv("EKA_CARE_CLIENT_ID")
client_secret = os.getenv("EKA_CARE_CLIENT_SECRET")

# --- API Functions ---
def get_new_tokens():
    url = "https://api.eka.care/connect-auth/v1/account/login"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data.get("access_token", "")
            st.session_state.refresh_token = data.get("refresh_token", "")
            st.session_state.last_refresh_time = time.time()
            st.toast("Access & Refresh tokens fetched successfully!")
        else:
            st.error("Failed to fetch tokens: " + str(response.text))
    except Exception as e:
        st.error(f"Token fetch error: {e}")

def refresh_tokens():
    url = "https://api.eka.care/connect-auth/v1/account/refresh"
    payload = {
        "access_token": st.session_state.access_token,
        "refresh_token": st.session_state.refresh_token
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data.get("access_token", "")
            st.session_state.refresh_token = data.get("refresh_token", "")
            st.session_state.last_refresh_time = time.time()
            st.toast("Access token refreshed successfully!")
        else:
            st.error("Token refresh failed: " + str(response.text))
    except Exception as e:
        st.error(f"Token refresh error: {e}")

# --- Token Validation Wrapper ---
def get_valid_access_token():
    now = time.time()

    if not st.session_state.access_token or not st.session_state.refresh_token:
        get_new_tokens()
    elif now - st.session_state.last_refresh_time > 540:
        refresh_tokens()

    return st.session_state.access_token

# --- Automatically check & maintain token ---
get_valid_access_token()  # This keeps the token valid at all times


#2 column layout
col1, col2 = st.columns(2)

#Left column content
with col1:
    #Button for login page redirect
    if st.button("Login to Eka Care"):
        st.switch_page("pages/login.py")

with col2:
    #Button for registration page redirect
    if st.button("Register on Eka Care"):
        st.switch_page("pages/register.py")