# use_cookies.py

import time
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 필요시 주석 처리해서 눈으로 확인 가능
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--lang=ko-KR")
# options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
options.binary_location = "/usr/bin/google-chrome"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # 먼저 인스타 메인 페이지 로딩
    driver.get("https://www.instagram.com/")
    time.sleep(3)

    # 쿠키 로드
    with open("insta_cookies.pkl", "rb") as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)

    # 새로고침하여 쿠키 적용
    driver.refresh()
    time.sleep(5)

    print("📍 현재 URL:", driver.current_url)
    if "login" in driver.current_url:
        print("❌ 쿠키 로그인 실패")
    else:
        print("✅ 쿠키 로그인 성공!")

    # 예시: 해시태그 페이지 접근
    driver.get("https://www.instagram.com/explore/tags/food/")
    time.sleep(5)
    print("✅ 해시태그 페이지 접근 완료")

finally:
    driver.quit()
