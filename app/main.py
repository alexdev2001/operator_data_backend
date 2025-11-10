import os
import shutil
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from app.routes import upload_routes, analysis_routes, report_routes

app = FastAPI(title="GGR Analysis API", version="1.0")

# Allow frontend (React/Next.js) access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/plots", StaticFiles(directory="app/plots"), name="plots")

app.include_router(upload_routes.router)
app.include_router(analysis_routes.router)
app.include_router(report_routes.router)

@app.get("/")
def root():
    return {"message": "Welcome to the GGR Analysis API"}


# ------------------- CLEANUP FUNCTION -------------------
def clear_directories():
    dirs_to_clear = ["app/data", "app/plots", "app/reports", "app/uploads"]
    for dir_path in dirs_to_clear:
        if os.path.exists(dir_path):
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # remove file or symlink
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # remove folder
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")
    print("Cleanup job completed.")


# ------------------- SCHEDULER -------------------
scheduler = BackgroundScheduler()
scheduler.add_job(clear_directories, "interval", hours=6, id="cleanup_job", replace_existing=True)
scheduler.start()