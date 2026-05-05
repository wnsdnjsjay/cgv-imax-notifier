import os
import asyncio
from playwright.async_api import async_playwright
import requests

# 텔레그램 알림 함수
def send_telegram(message):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    if not token or not chat_id:
        print("토큰이나 채팅 ID 설정이 누락되었습니다.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={'chat_id': chat_id, 'text': message})
    except Exception as e:
        print(f"텔레그램 전송 오류: {e}")

async def check_imax():
    target_date = "20260505" # 테스트를 위해 오늘 날짜로 설정
    print(f"[{target_date}] 용아맥 체크를 시작합니다 (Playwright 모드)")

    async with async_playwright() as p:
        # 브라우저 실행 (화면 없이 실행하는 headless 모드)
        browser = await p.chromium.launch(headless=True)
        # 실제 사람 브라우저처럼 보이게 컨텍스트 설정
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # CGV 용산아이파크몰 상영시간표 페이지 접속
        url = f"http://www.cgv.co.kr/common/showtimes/iframeTheater.aspx?theatercode=0013&date={target_date}"
        
        try:
            # 페이지 이동 및 네트워크 유휴 상태까지 대기 (데이터 로딩 시간 확보)
            await page.goto(url, wait_until="networkidle")
            
            # 영화 제목들이 나타날 때까지 최대 5초 대기
            await page.wait_for_selector("div.info-movie strong", timeout=5000)

            # 영화 제목들 추출
            movie_elements = await page.query_selector_all("div.info-movie strong")
            movie_list = []
            for el in movie_elements:
                title = await el.inner_text()
                movie_list.append(title.strip())

            print(f"--- 발견된 영화 목록 ({len(movie_list)}개) ---")
            for m in movie_list:
                print(f"- {m}")
            print("------------------------------------------")

            # 'IMAX' 글자가 포함되어 있는지 확인
            # 페이지 전체 텍스트에서 검색
            page_content = await page.content()
            if "IMAX" in page_content:
                print("🚀 결과: IMAX 상영 정보 발견!")
                send_telegram(f"🚀 [용아맥 알림] {target_date} IMAX 예매 정보가 확인되었습니다!")
            else:
                print("결과: 아직 IMAX 정보는 없습니다.")

        except Exception as e:
            print(f"실행 중 오류 발생: {e}")
            # 영화 목록을 아예 못 가져온 경우에만 출력
            if 'movie_list' not in locals() or len(movie_list) == 0:
                print("⚠️ 여전히 목록을 가져오지 못했습니다. CGV의 접근 차단이 강력합니다.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_imax())
