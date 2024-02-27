import streamlit as st
import datetime
from config.settings import chat_model,images_model
from dotenv import load_dotenv
from time import sleep
from api.xhs_api import QRCode_sign_streamlit
from api.openai_api import OpenAIClient
from content.content_generator import *
from image.image_generator import get_image_openai
from utils import *
import subprocess
import sys

load_dotenv(override=True)
api_key = os.environ.get("OPENAI_API_KEY")

# 尝试导入playwright，如果失败，则安装浏览器依赖
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    subprocess.check_call([sys.executable, "-m", "playwright", "install"])
    from playwright.sync_api import sync_playwright

st.set_page_config(
    page_title="Autoxhs",
    page_icon="📕",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.sidebar.title('登陆小红书')
col1, col2 = st.columns([1,1],gap='large') 
# 将登录逻辑移至边栏
def check_user_login():
    # 这里只是一个示例，实际应用中应该替换为真实的登录状态检查
    # 例如，检查session或者某个状态标志等
    if 'user_logged_in' not in st.session_state:
        st.session_state['user_logged_in'] = False
    return st.session_state['user_logged_in']

if check_user_login():
    st.sidebar.success("您已登录，欢迎！")
else:
    st.session_state.xhs_client, qr_img, qr_res = QRCode_sign_streamlit()
    st.sidebar.image(qr_img, caption='请扫描二维码登录',width =200)
    qr_id = qr_res["qr_id"]
    qr_code = qr_res["code"]
    while True:
        check_qrcode = st.session_state.xhs_client.check_qrcode(qr_id, qr_code)
        print(check_qrcode)
        sleep(1)
        if check_qrcode["code_status"] == 2:
            print(json.dumps(check_qrcode["login_info"], indent=4))
            print("当前 cookie：" + st.session_state.xhs_client.cookie)
            break
    st.session_state['user_logged_in'] = True
    st.rerun()
# 用户输入和内容生成逻辑移到边栏
with col1:
    theme = st.text_input('请输入贴文主题：')

    if 'generate_clicked' not in st.session_state:
        st.session_state.generate_clicked = False  # 初始化点击状态

    class Args:
        def __init__(self, theme):
            self.theme = theme
            # self.llm = "gpt-3.5-turbo-0125"  # 默认使用的模型
            self.llm = chat_model
            self.prompt_version = "v1"  # 默认提示词版本
    args = Args(theme)

    openai_client = OpenAIClient(api_key)

    if st.button("生成标题列表") and 'user_logged_in' in st.session_state and st.session_state['user_logged_in']:
        st.session_state.generate_clicked = True
        st.session_state.title_list, st.session_state.messages = get_title_openai(openai_client, args)

    if st.session_state.generate_clicked:
        selected_option = st.radio('请挑选一条标题', st.session_state.title_list)
        if selected_option:
            st.session_state.messages[-1]["content"] = selected_option
            
    if st.button("根据标题生成贴文") and st.session_state.generate_clicked:
        with st.spinner('请稍候，自动发布中...'):
            content = get_content_from_message_openai(openai_client, args, st.session_state.messages)
            st.success('文本内容生成成功！')

            save_path = create_directory_for_post()

            images = [
                get_image_openai(openai_client, images_model,content['标题'], save_path)
            ]
            st.success('图片内容生成成功！')

            topics = get_topics(st.session_state.xhs_client, content['Tags'])
            topics_suffix = get_topics_suffix(topics)
            content['正文'] = content['正文'] + topics_suffix

            note_info = st.session_state.xhs_client.create_image_note(
                content['标题'], content['正文'], images, topics=topics, 
                is_private=True, post_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            beauty_print(note_info)

            note_data = {
                "title": content['标题'],
                "description": content['正文'],
                "topics": topics_suffix,
                # 添加其他任何您想保存的信息
            }
            note_md = trans_into_md(note_data)
            # 保存贴文数据到文件
            save_post_to_file(note_data, save_path)
        col2_1, col2_2,col2_3 = col2.columns([2,4,2])  
        with col2_2:
        # 将发布的贴文详情显示在主页面的右侧
            st.subheader("发布的贴文详情")

            for image_path in images:
                st.image(image_path, caption="生成的图片", use_column_width=True)
            st.markdown(note_md, unsafe_allow_html=True)


