import os
import asyncio
from playwright.async_api import async_playwright
import requests

def send_telegram(message):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={'chat_id': chat_id, 'text': message})

async def check_imax():
    target_date = "20260505"
    print(f"[{target_date}] 용아맥 체크 시작 (강화된 우회 모드)")

    async with async_playwright() as p:
        # 브라우저 실행 시 '자동화 흔적' 제거 옵션 추가
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()

        # 자바스크립트 변수 조작으로 봇 감지 우회
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        url = f"http://www.cgv.co.kr/common/showtimes/iframeTheater.aspx?theatercode=0013&date={target_date}"
        
        try:
            # 타임아웃을 15초로 늘리고 조금 더 여유 있게 기다립니다
            await page.goto(url, wait_until="load", timeout=30000)
            await asyncio.sleep(3) # 페이지 로드 후 데이터가 뿌려질 시간을 명시적으로 줌
            
            # 영화 제목이 있는지 확인 (실패해도 바로 종료되지 않게 함)
            movie_elements = await page.query_selector_all("div.info-movie strong")
            
            if movie_elements:
                movie_list = [await el.inner_text() for el in movie_elements]
                print(f"--- 발견된 영화 목록 ({len(movie_list)}개) ---")
                for m in movie_list: print(f"- {m.strip()}")
                
                page_content = await page.content()
                if "IMAX" in page_content:
                    print("🚀 IMAX 발견!")
                    send_telegram(f"🚀 [용아맥 알림] {target_date} IMAX 예매 오픈!")
                else:
                    print("결과: IMAX 없음")
            else:
                print("⚠️ 영화 목록을 찾지 못했습니다. CGV가 여전히 차단 중입니다.")
                # 디버깅을 위해 현재 페이지 텍스트 일부 출력
                text = await page.content()
                print(f"페이지 일부 내용: {text[:200]}")

        except Exception as e:
            print(f"실행 중 오류: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_imax())
