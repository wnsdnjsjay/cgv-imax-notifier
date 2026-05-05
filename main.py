import os
import requests
from datetime import datetime, timedelta

def send_telegram(message):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    if not token or not chat_id: return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={'chat_id': chat_id, 'text': message})

def check_cgv():
    # --- 날짜 자동 설정 부분 ---
    # GitHub Actions 서버는 보통 UTC 기준이므로, 한국 시간(KST)으로 맞추기 위해 9시간을 더합니다.
    now_kst = datetime.utcnow() + timedelta(hours=9)
    target_date = now_kst.strftime("%Y%m%d") 
    # -----------------------
    
    print(f"--- [{target_date}] 용산 CGV 체크 시작 (자동 날짜 모드) ---")

    url = f"http://m.cgv.co.kr/WebApp/Reservation/Common/ajaxShowTimes.aspx?theatercode=0013&date={target_date}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'http://m.cgv.co.kr/WebApp/Reservation/Schedule.aspx'
    }

    try:
        response = requests.get(url, headers=headers)
        html_content = response.text

        if "IMAX" in html_content:
            print(f"🚀 {target_date} IMAX 발견!")
            send_telegram(f"🔥 [용아맥 알림] {target_date} IMAX 예매가 확인되었습니다!")
        elif "strong" in html_content:
            print(f"{target_date} 상영 정보는 있으나 아직 IMAX는 없습니다.")
        else:
            print(f"⚠️ {target_date} 영화 정보가 비어 있습니다.")
            
    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    check_cgv()
