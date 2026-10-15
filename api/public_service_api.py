import requests
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

load_dotenv()
API_KEY = os.getenv("PUBLIC_API_KEY")

def get_public_service():
    url = "https://api.odcloud.kr/api/15069932/v1/uddi:c93f0a5a-8d1d-4fc4-83fc-2df7e4e5b3c1"
    conn = get_connection()
    cur = conn.cursor()
    for page in range(1, 6):
        try:
            params = {"serviceKey": API_KEY, "numOfRows": "100", "page": str(page)}
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            items = data.get('data', [])
            if not items:
                break
            for item in items:
                name = item.get('서비스명')
                description = item.get('서비스목적')
                apply_url = item.get('신청방법URL')
                cur.execute("INSERT INTO subsidies (name, description, apply_url, source) VALUES (%s, %s, %s, '공공서비스') ON CONFLICT DO NOTHING", (name, description, apply_url))
        except Exception as e:
            print(f"공공서비스 오류: {e}")
            break
    conn.commit()

    cur.close()
    conn.close()
