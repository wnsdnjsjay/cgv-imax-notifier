import os
import requests
from datetime import datetime, timedelta
import re

def send_telegram(message):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={'chat_id': chat_id, 'text': message})

def check_cgv():
    # 한국 시간 기준 오늘 날짜 구하기
    now_kst = datetime.utcnow() + timedelta(hours=9)
    target_date = now_kst.strftime("%Y%m%d") 
    
    print(f"--- [{target_date}] 용산 CGV 체크 시작 ---")

    # API 대신 실제 모바일 웹 페이지 주소 사용 (더 안정적임)
    url = f"http://m.cgv.co.kr/WebApp/Reservation/Schedule.aspx?theaterCode=0013&date={target_date}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
    }

    try:
        response = requests.get(url, headers=headers)
        html_content = response.text

        # 1. IMAX가 있는지 확인
        if "IMAX" in html_content:
            print(f"🚀 {target_date} IMAX 상영관 발견!")
            send_telegram(f"🔥 [용아맥 알림] {target_date} IMAX 예매 오픈!")
            return

        # 2. 영화 제목들 추출 (정규식 사용)
        # 모바일 페이지에서 영화 제목은 보통 <strong class="title"> 또는 특정 패턴 안에 있습니다.
        # 단순히 '상영 정보가 있는지'만 체크하기 위해 "영화상세" 같은 단어가 있는지 봅니다.
        if "영화상세" in html_content or "movie_info" in html_content.lower():
            print(f"✅ {target_date} 상영 정보는 불러왔으나, 아직 IMAX는 없습니다.")
        else:
            # 아예 정보가 없는 경우, CGV에서 아직 날짜를 안 열었을 수 있습니다.
            print(f"ℹ️ {target_date} 상영 정보 자체가 아직 등록되지 않았습니다.")
            
    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    check_cgv()
