from apscheduler.schedulers.background import BackgroundScheduler
from api.volunteer_api import get_volunteer_posts
from api.welfare_local_api import get_local_welfare
from api.welfare_central_api import get_central_welfare
from api.scholarship_api import get_scholarship
from api.public_service_api import get_public_service

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', hour=0, minute=0)
def update_all():
    get_volunteer_posts()
    get_local_welfare()
    get_central_welfare()
    get_scholarship()
    get_public_service()

scheduler.start()

from fastapi import FastAPI
from database import get_connection
from dotenv import load_dotenv

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