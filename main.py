from apscheduler.schedulers.background import BackgroundScheduler
from api.volunteer_api import get_volunteer_posts
from api.welfare_local_api import get_local_welfare
from api.welfare_central_api import get_central_welfare
from api.scholarship_api import get_scholarship
from api.public_service_api import get_public_service

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor
from database import get_connection
from dotenv import load_dotenv
import threading

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def update_all():
    try:
        print("데이터 수집 시작")
        get_volunteer_posts()
        print("봉사 완료")
        get_local_welfare()
        print("지자체 완료")
        get_central_welfare()
        print("중앙 완료")
        get_scholarship()
        print("장학금 완료")
        get_public_service()
        print("공공서비스 완료")
    except Exception as e:
        print(f"데이터 수집 오류: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(update_all, 'cron', hour=0, minute=0)
scheduler.start()

threading.Thread(target=update_all, daemon=True).start()


def region_keywords(region: str):
    # "서울특별시 종로구" -> ["서울", "종로"]
    return [w[:2] for w in region.split() if len(w) >= 2]


@app.get("/")
def root():
    return {"message": "지원금 캘린더 AI 서버 작동 중"}

@app.get("/db-test")
def db_test():
    try:
        conn = get_connection()
        conn.close()
        return {"message": "DB 연결 성공"}
    except Exception as e:
        return {"message": f"DB 연결 실패: {str(e)}"}

@app.get("/subsidies")
def get_subsidies(page: int = 1):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    offset = (page - 1) * 20
    cur.execute(
        "SELECT id, name, description, apply_url, source, target_region "
        "FROM subsidies ORDER BY id LIMIT 20 OFFSET %s", (offset,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"page": page, "data": rows}

@app.get("/subsidies/recommend")
def recommend_subsidies(region: str = "", age: int = 0, limit: int = 5):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT id, name, description, apply_url, source, target_region "
        "FROM subsidies WHERE name IS NOT NULL")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    keys = region_keywords(region)
    is_youth = 19 <= age <= 34

    for r in rows:
        text = f"{r['target_region'] or ''} {r['name'] or ''}"
        r["region_match"] = any(k in text for k in keys)
        r["youth"] = is_youth and ("청년" in text or "대학" in text or "장학" in text)

    rows.sort(key=lambda r: (r["region_match"], r["youth"]), reverse=True)
    result = rows[:limit]
    for r in result:
        r.pop("youth", None)
    return {"data": result}

@app.get("/volunteers")
def get_volunteers(region: str = "", page: int = 1):
    keys = region_keywords(region)
    pattern = f"%{keys[0]}%" if keys else "%"
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    offset = (page - 1) * 20
    cur.execute(
        "SELECT id, title, organization, region, apply_url, source "
        "FROM volunteer_posts "
        "ORDER BY (region ILIKE %s) DESC, id LIMIT 20 OFFSET %s",
        (pattern, offset))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"page": page, "data": rows}

@app.get("/fetch-data")
def fetch_data():
    threading.Thread(target=update_all, daemon=True).start()
    return {"message": "데이터 수집 시작됨"}
