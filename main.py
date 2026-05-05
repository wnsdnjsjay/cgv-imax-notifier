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
    now_kst = datetime.utcnow() + timedelta(hours=9)
    target_date = now_kst.strftime("%Y%m%d") 
    
    print(f"--- [{target_date}] 용산 CGV 정밀 체크 시작 ---")

    # CGV에서 상영 시간표를 가져오는 가장 원천 데이터 주소 (JSON 방식)
    url = "http://m.cgv.co.kr/WebApp/Reservation/Common/ajaxShowTimes.aspx"
    
    params = {
        'theatercode': '0013', # 용산아이파크몰
        'date': target_date,
        'screencode': '',
        'moviecode': ''
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
        'Referer': f'http://m.cgv.co.kr/WebApp/Reservation/Schedule.aspx?theaterCode=0013&date={target_date}',
        'X-Requested-With': 'XMLHttpRequest'
    }

    try:
        # 이 주소는 HTML이 아니라 데이터 조각(HTML snippets)을 줍니다.
        response = requests.get(url, params=params, headers=headers)
        data = response.text

        # 로그에 데이터가 조금이라도 찍히는지 확인 (디버깅용)
        print(f"데이터 수신 길이: {len(data)}")

        if "IMAX" in data:
            print(f"🚀 {target_date} IMAX 상영관 발견!")
            send_telegram(f"🔥 [용아맥 알림] {target_date} IMAX 예매 오픈!")
        elif "strong" in data or "theater_info" in data:
            print(f"✅ {target_date} 상영 정보 수신 성공! (하지만 IMAX는 없음)")
            # 어떤 영화가 있는지 샘플로 하나만 출력해봅니다.
            if "<strong>" in data:
                sample_title = data.split("<strong>")[1].split("</strong>")[0]
                print(f"확인된 영화 예시: {sample_title}")
        else:
            print(f"⚠️ {target_date} 여전히 데이터를 가져오지 못했습니다. (CGV 차단 중)")
            
    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    check_cgv()
