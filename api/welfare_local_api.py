import requests
import os
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

load_dotenv()
API_KEY = os.getenv("PUBLIC_API_KEY")

def get_local_welfare():
    url = "https://apis.data.go.kr/B554287/LocalGovernmentWelfareInformations/LcgvWelfarelist"
    conn = get_connection()
    cur = conn.cursor()
    page = 1
    while True:
        params = {"serviceKey": API_KEY, "numOfRows": "100", "pageNo": str(page)}
        response = requests.get(url, params=params)
        root = ET.fromstring(response.text)
        items = root.findall('.//servList')
        if not items:
            break
        for item in items:
            name = item.findtext('servNm')
            description = item.findtext('servDgst')
            apply_url = item.findtext('servDtlLink')
            region = item.findtext('sigunguNm')
            cur.execute("""
                INSERT INTO subsidies (name, description, apply_url, target_region, source)
                VALUES (%s, %s, %s, %s, '복지로_지자체')
                ON CONFLICT DO NOTHING
            """, (name, description, apply_url, region))
        page += 1
    conn.commit()
    cur.close()
    conn.close()