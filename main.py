from apscheduler.schedulers.background import BackgroundScheduler
from api.volunteer_api import get_volunteer_posts
from api.welfare_local_api import get_local_welfare
from api.welfare_central_api import get_central_welfare
from api.scholarship_api import get_scholarship
from api.public_service_api import get_public_service

from fastapi import FastAPI
from database import get_connection
from dotenv import load_dotenv
import threading

load_dotenv()

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def update_all():
    try:
        get_volunteer_posts()
        get_local_welfare()
        get_central_welfare()
        get_scholarship()
        get_public_service()
    except Exception as e:
        print(f"데이터 수집 오류: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(update_all, 'cron', hour=0, minute=0)
scheduler.start()

# 서버 시작시 한번 실행
threading.Thread(target=update_all, daemon=True).start()

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
    cur = conn.cursor()
    offset = (page - 1) * 20
    cur.execute("SELECT * FROM subsidies ORDER BY id LIMIT 20 OFFSET %s", (offset,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"page": page, "data": rows}

@app.get("/volunteers")
def get_volunteers(page: int = 1):
    conn = get_connection()
    cur = conn.cursor()
    offset = (page - 1) * 20
    cur.execute("SELECT * FROM volunteer_posts ORDER BY id LIMIT 20 OFFSET %s", (offset,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"page": page, "data": rows}

    @app.get("/fetch-data")
def fetch_data():
    try:
        update_all()
        return {"message": "데이터 수집 완료"}
    except Exception as e:
        return {"message": f"오류: {str(e)}"}