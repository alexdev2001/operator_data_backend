import traceback
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from app.services import report_service

router = APIRouter(prefix="/report", tags=["Report"])

@router.get("/full")
def get_full_report(
    file_name: str,
    sheets: list[str] = Query(..., description="List of sheet names to include in the report")
):
    try:
        report_path = report_service.generate_full_report(file_name, sheets)
        return FileResponse(report_path, filename="full_report.pdf")
    except Exception as e:
        print("🔥 Error generating report:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))