import streamlit as st

st.title("Hello World")


def display_name(name: str):
    st.info(f"Hello {name}, I am really happy to see you here")


name = st.text_input("Please enter your name")

if not name:
    st.error("no name entered")
    # stop this run, please note that the main application is still running
    # and we only stop this specific run.
    st.stop()

display_name(name)
