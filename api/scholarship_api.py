import requests
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

load_dotenv()
API_KEY = os.getenv("PUBLIC_API_KEY")

def get_scholarship():
    url = "https://api.odcloud.kr/api/15028252/v1/uddi:3b2a715a-b097-4a7f-838e-da2e5b9ba8e8"
    conn = get_connection()
    cur = conn.cursor()
    page = 1
    while True:
        params = {"serviceKey": API_KEY, "numOfRows": "100", "page": str(page)}
        response = requests.get(url, params=params)
        data = response.json()
        items = data.get('data', [])
        if not items:
            break
        for item in items:
            name = item.get('장학금명')
            description = item.get('장학금설명')
            cur.execute("""
                INSERT INTO subsidies (name, description, source)
                VALUES (%s, %s, '한국장학재단')
                ON CONFLICT DO NOTHING
            """, (name, description))
        page += 1
    conn.commit()
    cur.close()
    conn.close()