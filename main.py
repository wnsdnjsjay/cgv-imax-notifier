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
    
    print(f"--- [{target_date}] 용산 CGV 세션 우회 체크 ---")

    # 세션 객체 생성 (쿠키를 자동으로 관리해줍니다)
    session = requests.Session()
    
    # 1. 먼저 메인 페이지나 스케줄 페이지에 접속해서 기본 쿠키를 굽습니다.
    main_url = "http://m.cgv.co.kr/WebApp/Reservation/Schedule.aspx"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
    }
    session.get(main_url, headers=headers)

    # 2. 획득한 쿠키를 가지고 실제 데이터 API에 접근합니다.
    ajax_url = "http://m.cgv.co.kr/WebApp/Reservation/Common/ajaxShowTimes.aspx"
    params = {
        'theatercode': '0013',
        'date': target_date,
    }
    
    # AJAX 요청임을 알리는 헤더를 추가합니다.
    headers.update({
        'Referer': main_url,
        'X-Requested-With': 'XMLHttpRequest'
    })

    try:
        response = session.get(ajax_url, params=params, headers=headers)
        data = response.text
        
        # 로그 확인을 위해 수신 데이터가 에러 페이지인지 실제 데이터인지 판단
        if "errorPage" in data:
            print("❌ 실패: 여전히 에러 페이지(CSS)가 반환되었습니다.")
            print(f"데이터 일부: {data[:200]}")
        elif "IMAX" in data.upper():
            print("🚀 성공: IMAX 발견!")
            send_telegram(f"🔥 [용아맥 알림] {target_date} IMAX 예매 오픈!")
        elif "strong" in data:
            print("✅ 성공: 데이터를 가져왔으나 IMAX는 아직 없습니다.")
            # 성공했을 때만 데이터 원본을 살짝 보여줍니다.
            print(f"데이터 샘플: {data[:200]}")
        else:
            print("⚠️ 알 수 없는 응답입니다. 데이터가 비어있을 수 있습니다.")
            
    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    check_cgv()
