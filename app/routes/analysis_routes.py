from fastapi import APIRouter, HTTPException
from app.services import analysis_service

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.get("/timeseries")
def get_time_series_chart(sheet_name: str | None = None):
    try:
        plot_path = analysis_service.generate_time_series_chart(sheet_name=sheet_name)
        return {"message": "Time series chart generated", "plot_path": plot_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/seasonality")
def get_seasonality_chart(sheet_name: str | None = None):
    try:
        plot_path = analysis_service.generate_seasonality_chart(sheet_name=sheet_name)
        return {"message": "Seasonality chart generated", "plot_path": plot_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast")
def get_forecast_chart(sheet_name: str | None = None):
    try:
        plot_path = analysis_service.generate_forecast_chart(sheet_name=sheet_name)
        return {"message": "Forecast chart generated", "plot_path": plot_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))