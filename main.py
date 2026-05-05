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
    now_kst = datetime.utcnow() + timedelta(hours=9)
    target_date = now_kst.strftime("%Y%m%d") 
    
    print(f"--- [{target_date}] 데이터 원본 확인 모드 ---")

    url = "http://m.cgv.co.kr/WebApp/Reservation/Common/ajaxShowTimes.aspx"
    params = {'theatercode': '0013', 'date': target_date}
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
        'X-Requested-With': 'XMLHttpRequest'
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.text
        
        # --- 로그에서 읽기 쉽게 데이터 가공 ---
        # 1. HTML 태그 내부의 텍스트만 추출
        clean_text = re.sub(r'<[^>]+>', ' ', data) 
        # 2. 연속된 공백 줄이기
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        print("\n=== [수신 데이터 원본 시작] ===")
        print(clean_text)
        print("=== [수신 데이터 원본 끝] ===\n")

        # 키워드 체크
        if "IMAX" in data.upper():
            print("🚀 결과: IMAX 키워드 발견!")
            send_telegram(f"🔥 [용아맥 알림] {target_date} IMAX 발견!")
        else:
            print("결과: IMAX 키워드가 데이터에 없습니다.")
            
    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    check_cgv()
