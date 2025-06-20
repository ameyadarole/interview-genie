import streamlit as st
import hmac

st.set_page_config(page_title="Interview Genie Login", page_icon="🧞", layout="centered")

def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        st.image("D:\GenAI\interview_genie\genie.jpg", width=200)  # Replace with your image URL or local path
        st.markdown("### 🔐 Welcome to Interview Genie")
        st.markdown("Enter your credentials to unlock personalized interview prep magic!")

        with st.form("Credentials"):
            st.text_input("👤 Username", key="username")
            st.text_input("🔑 Password", type="password", key="password")
            st.form_submit_button("✨ Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets["passwords"] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


# ---- Page protection ----
if not check_password():
    st.stop()

# Continue with your app here
st.success("✅ Login successful! The genie is ready to help you crack your interviews.")
