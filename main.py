import requests
from bs4 import BeautifulSoup
import os

def send_telegram(message):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={'chat_id': chat_id, 'text': message})

def check_imax(date):
    # 세션을 사용해 쿠키를 자동으로 관리하게 합니다.
    session = requests.Session()
    
    url = f"http://www.cgv.co.kr/common/showtimes/iframeTheater.aspx?theatercode=0013&date={date}"
    
    # 브라우저인 척 위장하는 더 강력한 헤더
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Referer': 'http://www.cgv.co.kr/theaters/?theaterCode=0013',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive'
    }
    
    try:
        # 먼저 메인 페이지에 한 번 접속해서 쿠키를 굽습니다.
        session.get("http://www.cgv.co.kr/theaters/?theaterCode=0013", headers=headers)
        
        # 그 다음 실제 데이터 페이지(iframe)를 요청합니다.
        response = session.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        if "IMAX" in response.text:
            return True
            
        soup = BeautifulSoup(response.text, 'html.parser')
        movies = soup.select('div.info-movie > a > strong')
        
        if movies:
            print(f"--- 현재 검색된 영화 목록 ({len(movies)}개) ---")
            for m in movies:
                print(f"- {m.text.strip()}")
        else:
            print("⚠️ 여전히 목록을 가져오지 못했습니다. CGV 보안이 강화된 것 같네요.")
            
        return False
    except Exception as e:
        print(f"오류 발생: {e}")
        return False

if __name__ == "__main__":
    target_date = "20260505" # 오늘 날짜로 테스트
    print(f"{target_date} 용아맥 체크 시작...")
    
    if check_imax(target_date):
        print("결과: IMAX 상영 정보 발견!")
        send_telegram(f"🚀 [용아맥 알림] {target_date} 예매 정보가 확인되었습니다!")
    else:
        print("결과: 아직 정보를 찾지 못했습니다.")
