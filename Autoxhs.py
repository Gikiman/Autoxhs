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

st.sidebar.success("Select A Function Above.")

st.write("# Welcome to Autoxhs! 👋")

st.image("assets/Autoxhs.png")

st.markdown(
"""
> Autoxsh 是一款开源工具，专为小红书（Xiaohongshu）内容创作而设计。借助 OpenAI 的 API，这款工具能够自动生成并发布图文内容，包括图片、标题、正文以及标签。
  
## 功能特色

- **主题生成贴文**: 用户仅需输入一个主题，Autoxsh 即可自动创作出完整的贴文内容和匹配的图片，让内容创作变得轻而易举。
- **图片生成贴文**: 用户上传自己的照片，Autoxsh 能够基于这些照片自动生成丰富有趣的贴文内容，无需再为文字苦恼。
"""
,unsafe_allow_html=True)