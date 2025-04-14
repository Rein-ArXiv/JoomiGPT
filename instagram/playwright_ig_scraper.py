import asyncio
from playwright.async_api import async_playwright
import pickle

HASHTAG = "lee"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # GUI 확인용
        context = await browser.new_context()

        # 로그인된 세션 불러오기 (쿠키 기반)
        try:
            with open("insta_cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
                await context.add_cookies(cookies)
                print("✅ 쿠키 불러오기 성공")
        except:
            print("❌ 쿠키 불러오기 실패")

        page = await context.new_page()
        await page.goto(f"https://www.instagram.com/explore/tags/{HASHTAG}/", timeout=60000)
        await page.wait_for_timeout(5000)

        # 게시물 썸네일 링크들 수집
        posts = await page.query_selector_all('a[href^="/p/"]')
        print(f"📦 게시물 {len(posts)}개 발견됨")

        for i, post in enumerate(posts[:10]):
            href = await post.get_attribute("href")
            print(f"{i+1}: https://www.instagram.com{href}")

        await browser.close()

asyncio.run(main())
