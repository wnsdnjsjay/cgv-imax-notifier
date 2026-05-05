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
    # CGV 용산아이파크몰 상영시간표 iframe URL
    url = f"http://www.cgv.co.kr/common/showtimes/iframeTheater.aspx?theatercode=0013&date={date}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 'IMAX' 텍스트를 포함하는 요소가 있는지 확인
        imax_elements = soup.find_all(string=lambda text: 'IMAX' in text)
        
        if imax_elements:
            return True
        return False
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    target_date = "20260404"  # 확인하고 싶은 날짜 (4월 4일)
    print(f"{target_date} 용아맥 체크 시작...")
    
    if check_imax(target_date):
        print("찾았다! 예매 오픈!")
        send_telegram(f"🚀 [용아맥 알림] {target_date} 예매가 열린 것 같습니다! 지금 확인하세요!")
    else:
        print("아직 열리지 않았습니다.")
