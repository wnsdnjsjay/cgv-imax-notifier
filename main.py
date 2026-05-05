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
    # 실제 사용자가 브라우저로 접속하는 것처럼 보이게 하는 위장용 헤더
    url = f"http://www.cgv.co.kr/common/showtimes/iframeTheater.aspx?theatercode=0013&date={date}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Referer': 'http://www.cgv.co.kr/theaters/?theaterCode=0013',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        # 1. 텍스트 전체에서 'IMAX'가 있는지 먼저 확인 (가장 확실)
        if "IMAX" in response.text:
            return True
        
        # 2. 만약 안 나온다면, 영화 제목이라도 긁어지는지 확인
        soup = BeautifulSoup(response.text, 'html.parser')
        movies = soup.select('div.info-movie > a > strong')
        if not movies:
            print("⚠️ 영화 목록을 가져오지 못했습니다. CGV에서 접속을 제한했을 수 있습니다.")
            return False
            
        return False
    except Exception as e:
        print(f"오류 발생: {e}")
        return False

if __name__ == "__main__":
    # 테스트를 위해 '오늘' 날짜나 상영이 확실히 있는 날짜로 먼저 해보세요.
    target_date = "20260505" 
    print(f"{target_date} 용아맥 체크 시작...")
    
    if check_imax(target_date):
        print("결과: IMAX 상영 정보 발견!")
        send_telegram(f"🚀 [용아맥 알림] {target_date} 예매 정보가 확인되었습니다!")
    else:
        print("결과: 아직 정보를 찾지 못했습니다.")
