import requests
from bs4 import BeautifulSoup
import os

def send_telegram(message):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    if not token or not chat_id:
        print("토큰이나 채팅 ID가 설정되지 않았습니다.")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {'chat_id': chat_id, 'text': message}
    try:
        requests.post(url, json=params)
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")

def check_imax(date):
    # CGV 용산아이파크몰 상영시간표 데이터 URL (새로운 방식)
    url = f"http://www.cgv.co.kr/common/showtimes/iframeTheater.aspx?theatercode=0013&date={date}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Referer': 'http://www.cgv.co.kr/theaters/?theaterCode=0013'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8' # 한글 깨짐 방지
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # [디버깅] 현재 상영 중인 모든 영화 제목 추출
        movies = soup.select('div.info-movie > a > strong')
        movie_list = [m.text.strip() for m in movies]
        
        print(f"--- 현재 검색된 영화 목록 ({len(movie_list)}개) ---")
        for m in movie_list:
            print(f"- {m}")
        print("------------------------------------------")

        # 'IMAX' 텍스트가 포함된 영화나 상영관 정보 찾기
        # CGV는 상영관 종류를 span.kind 또는 i.imax 등의 클래스로 표시함
        imax_found = False
        if "IMAX" in response.text:
            imax_found = True
            
        return imax_found
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    target_date = "20260509" # 테스트 날짜
    print(f"{target_date} 용아맥 체크 시작...")
    
    if check_imax(target_date):
        print("결과: IMAX 상영 정보 발견!")
        send_telegram(f"🚀 [용아맥 알림] {target_date} 예매 정보가 확인되었습니다!")
    else:
        print("결과: 아직 IMAX 정보를 찾지 못했습니다.")
