from time import sleep
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import asyncio
from xhs import XhsClient, DataFetchError
import qrcode
import json
import requests
from io import BytesIO
import time
import platform

def sign(uri, data=None, a1="", web_session=""):
    for _ in range(10):
        try:
            with sync_playwright() as playwright:
                stealth_js_path = "stealth.min.js"
                chromium = playwright.chromium

                # 如果一直失败可尝试设置成 False 让其打开浏览器，适当添加 sleep 可查看浏览器状态
                browser = chromium.launch(headless=True)

                browser_context = browser.new_context()
                browser_context.add_init_script(path=stealth_js_path)
                context_page = browser_context.new_page()
                context_page.goto("https://www.xiaohongshu.com")
                browser_context.add_cookies([
                    {'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}]
                )
                context_page.reload()
                # 这个地方设置完浏览器 cookie 之后，如果这儿不 sleep 一下签名获取就失败了，如果经常失败请设置长一点试试
                sleep(1)
                encrypt_params = context_page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
                return {
                    "x-s": encrypt_params["X-s"],
                    "x-t": str(encrypt_params["X-t"])
                }
        except Exception as e:
            print(e)
            # 这儿有时会出现 window._webmsxyw is not a function 或未知跳转错误，因此加一个失败重试趴
            pass
    raise Exception("未连接成功，请尝试刷新页面")

async def _sign(uri, data=None, a1="", web_session=""):
    for _ in range(10):
        try:
            async with async_playwright() as playwright:
                stealth_js_path = "stealth.min.js"
                chromium = playwright.chromium

                # 如果一直失败可尝试设置成 False 让其打开浏览器，适当添加 sleep 可查看浏览器状态
                browser = await chromium.launch(headless=True)

                browser_context = await browser.new_context()
                await browser_context.add_init_script(path=stealth_js_path)
                context_page = await browser_context.new_page()
                await context_page.goto("https://www.xiaohongshu.com")
                await browser_context.add_cookies([
                    {'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}]
                )
                await context_page.reload()
                # 这个地方设置完浏览器 cookie 之后，如果这儿不 sleep 一下签名获取就失败了，如果经常失败请设置长一点试试
                sleep(2)
                encrypt_params = await context_page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
                return {
                    "x-s": encrypt_params["X-s"],
                    "x-t": str(encrypt_params["X-t"])
                }
        except Exception as e:
            print(e)
            # 这儿有时会出现 window._webmsxyw is not a function 或未知跳转错误，因此加一个失败重试趴
            pass
    raise Exception("未连接成功，请尝试刷新页面")

def async_sign(uri, data=None, a1="", web_session=""):
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    result=loop.run_until_complete(_sign(uri, data, a1, web_session))
    return result

def cookie_sign(cookie):
    if platform.system().lower() == 'windows':
        xhs_client = XhsClient(cookie, sign=async_sign)
    else:
        xhs_client = XhsClient(cookie, sign=sign)
    return xhs_client

def phone_sign():
    if platform.system().lower() == 'windows':
        xhs_client = XhsClient(sign=async_sign)
    else:
        xhs_client = XhsClient(sign=sign)
    phone = input("请输入手机号码：")
    res = xhs_client.send_code(phone)
    print("验证码发送成功~")
    code = input("请输入验证码：")
    token = ""
    while True:
        try:
            check_res = xhs_client.check_code(phone, code)
            token = check_res["mobile_token"]
            break
        except DataFetchError as e:
            print(e)
            code = input("请输入验证码：")
    login_res = xhs_client.login_code(phone, token)
    print(json.dumps(login_res, indent=4))

def QRCode_sign():
    if platform.system().lower() == 'windows':
        xhs_client = XhsClient(sign=async_sign)
    else:
        xhs_client = XhsClient(sign=sign)
    qr_res = xhs_client.get_qrcode()
    qr_id = qr_res["qr_id"]
    qr_code = qr_res["code"]

    qr = qrcode.QRCode(version=1, error_correction=qrcode.ERROR_CORRECT_L,
                       box_size=50,
                       border=1)
    qr.add_data(qr_res["url"])
    qr.make()
    qr.print_ascii()

    while True:
        check_qrcode = xhs_client.check_qrcode(qr_id, qr_code)
        print(check_qrcode)
        sleep(1)
        if check_qrcode["code_status"] == 2:
            print(json.dumps(check_qrcode["login_info"], indent=4))
            # print("当前 cookie：" + xhs_client.cookie)
            break
    return xhs_client

def QRCode_sign_streamlit(xhs_client):
    qr_res = xhs_client.get_qrcode()
    qr = qrcode.make(qr_res["url"])
    img = BytesIO()
    qr.save(img, format='PNG')
    img.seek(0)  # 重置文件指针到开始
    return img, qr_res  # 返回二维码图片和相关信息

def create_client():
    if platform.system().lower() == 'windows':
        xhs_client = XhsClient(sign=async_sign)
    else:
        xhs_client = XhsClient(sign=sign)
    return xhs_client