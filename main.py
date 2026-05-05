import os
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta

async def send_telegram(message):
    import requests
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={'chat_id': chat_id, 'text': message})

async def check_cgv():
    now_kst = datetime.utcnow() + timedelta(hours=9)
    target_date = now_kst.strftime("%Y%m%d")
    print(f"--- [{target_date}] 용산 CGV 브라우저 우회 체크 ---")

    async with async_playwright() as p:
        # 브라우저 실행 (사람처럼 보이기 위해 헤더 설정)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        )
        page = await context.new_page()

        # 실제 모바일 예약 페이지 접속
        url = f"http://m.cgv.co.kr/WebApp/Reservation/Schedule.aspx?theaterCode=0013&date={target_date}"
        await page.goto(url, wait_until="networkidle")

        # 영화 목록이 로드될 때까지 잠시 대기
        await page.wait_for_timeout(3000)

        # 페이지 전체 텍스트 가져오기
        content = await page.content()

        if "IMAX" in content.upper():
            print("🚀 결과: IMAX 발견!")
            await send_telegram(f"🔥 [용아맥 알림] {target_date} IMAX 오픈!")
        elif "영화상세" in content or "시간표" in content:
            print("✅ 성공: 상영 정보 읽기 완료 (IMAX는 아직 없음)")
        else:
            print("⚠️ 확인 실패: 데이터를 불러왔으나 영화 정보가 보이지 않습니다.")
            # 디버깅을 위해 페이지 제목 출력
            title = await page.title()
            print(f"현재 페이지 제목: {title}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_cgv())
