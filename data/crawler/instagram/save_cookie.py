import time
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# 크롬 옵션 최소화 (root + VNC 환경 안정용)
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--lang=ko-KR")
options.add_argument("start-maximized")
options.add_argument("window-size=1280,800")
options.binary_location = "/usr/bin/google-chrome"

# Chrome 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)

    username = input("Instagram username: ")
    password = input("Instagram password: ")

    driver.find_element(By.NAME, "username").send_keys(username) # ID: joomidang.ai@gmail.com
    driver.find_element(By.NAME, "password").send_keys(password) # PW: Jmd0504!
    driver.find_element(By.NAME, "password").send_keys(Keys.ENTER)

    time.sleep(20)  # 로그인 및 2FA 시간 대기

    with open("insta_cookies.pkl", "wb") as f:
        pickle.dump(driver.get_cookies(), f)
    print("✅ 쿠키 저장 완료!")

finally:
    driver.quit()
