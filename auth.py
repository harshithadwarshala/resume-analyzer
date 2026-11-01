import streamlit as st


def require_login():

    if st.session_state.get("recruiter_ok"):
        return

    try:
        correct = st.secrets["RECRUITER_PASSWORD"]
    except Exception:
        correct = None

    st.subheader("Recruiter login")

    pwd = st.text_input(
        "Recruiter password",
        type="password"
    )

    if pwd:
        if correct and pwd == correct:
            st.session_state["recruiter_ok"] = True
            st.rerun()
        else:
            st.error("Wrong password")

    st.stop()