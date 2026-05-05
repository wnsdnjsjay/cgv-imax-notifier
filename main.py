import os
import requests
import json

def send_telegram(message):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={'chat_id': chat_id, 'text': message})

def check_imax():
    target_date = "20260505" # 오늘 날짜
    # CGV 모바일 용산아이파크몰(0013) 상영시간표 API
    url = f"http://m.cgv.co.kr/WebApp/Reservation/Common/ajaxShowTimes.aspx?theatercode=0013&date={target_date}&screencode=&moviecode="
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
        'Referer': 'http://m.cgv.co.kr/WebApp/Reservation/Schedule.aspx',
        'X-Requested-With': 'XMLHttpRequest'
    }

    try:
        response = requests.get(url, headers=headers)
        # API 응답에서 영화 제목들 추출
        # 모바일 API는 HTML 조각을 반환하므로 'IMAX' 글자가 있는지 바로 확인하는 게 빠릅니다.
        
        if "IMAX" in response.text:
            print(f"🚀 [{target_date}] IMAX 상영 정보 발견!")
            send_telegram(f"🚀 [용아맥 알림] {target_date} IMAX 예매가 열렸습니다!")
            return True
        else:
            print(f"[{target_date}] 아직 IMAX 상영 정보가 없습니다.")
            # 데이터가 아예 안 오는지 확인하기 위해 응답 길이를 출력해봅니다.
            if len(response.text) < 100:
                print("⚠️ 응답 데이터가 너무 짧습니다. 차단되었을 가능성이 있습니다.")
            return False

    except Exception as e:
        print(f"오류 발생: {e}")
        return False

if __name__ == "__main__":
    check_imax()
