import requests
import os
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

load_dotenv()
API_KEY = os.getenv("PUBLIC_API_KEY")

def get_volunteer_posts():
    url = "https://apis.data.go.kr/1741000/volunteerPartcptnService/getVltrSearchWordList"
    conn = get_connection()
    cur = conn.cursor()
    page = 1
    while True:
        params = {"serviceKey": API_KEY, "numOfRows": "100", "pageNo": str(page), "schSign": "1"}
        response = requests.get(url, params=params)
        root = ET.fromstring(response.text)
        items = root.findall('.//item')
        if not items:
            break
        for item in items:
            title = item.findtext('progrmSj')
            organization = item.findtext('nanmmbyNm')
            region = item.findtext('actPlace')
            apply_url = item.findtext('url')
            cur.execute("""
                INSERT INTO volunteer_posts (title, organization, region, apply_url, source)
                VALUES (%s, %s, %s, %s, '1365')
                ON CONFLICT DO NOTHING
            """, (title, organization, region, apply_url))
        page += 1
    conn.commit()
    cur.close()
    conn.close()