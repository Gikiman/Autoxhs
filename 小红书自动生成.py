import streamlit as st
import subprocess
import sys

try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        chromium = playwright.chromium
        browser = chromium.launch(headless=True)
except Exception as e: 
    print(e)
    subprocess.check_call([sys.executable, "-m", "playwright", "install"])
    print("playwright已安装")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        chromium = playwright.chromium
        browser = chromium.launch(headless=True)
        
st.set_page_config(
    page_title="Autoxhs",
    page_icon="📛",
)

st.sidebar.success("Select a feature above.")

st.write("# Welcome to Autoxhs! 👋")

st.markdown(
    """
    Streamlit is an open-source app framework built specifically for
    Machine Learning and Data Science projects.
    **👈 Select a demo from the sidebar** to see some examples
    of what Streamlit can do!
    ### Want to learn more?
    - Check out [streamlit.io](https://streamlit.io)
    - Jump into our [documentation](https://docs.streamlit.io)
    - Ask a question in our [community
        forums](https://discuss.streamlit.io)
    ### See more complex demos
    - Use a neural net to [analyze the Udacity Self-driving Car Image
        Dataset](https://github.com/streamlit/demo-self-driving)
    - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
"""
)