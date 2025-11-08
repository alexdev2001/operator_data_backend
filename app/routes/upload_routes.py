from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services import upload_service
import pandas as pd
import os


router = APIRouter(prefix="/upload", tags=["Upload"])

@router.get("/sheets")
def get_sheet_names():
    file_name = upload_service.get_latest_file_name()
    if not file_name:
        raise HTTPException(status_code=404, detail="No file uploaded yet")

    file_path = os.path.join(upload_service.UPLOAD_DIR, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    try:
        xls = pd.ExcelFile(file_path)
        return {"sheets": xls.sheet_names}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dataset")
async def upload_dataset(file: UploadFile = File(...)):
    try:
        file_path = await upload_service.save_uploaded_file(file)
        parsed_message = upload_service.parse_dataset(file_path)
        return {"message": "File uploaded and parsed successfully", "details": parsed_message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))