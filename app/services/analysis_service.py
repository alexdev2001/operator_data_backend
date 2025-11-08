import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from prophet import Prophet
import os
import app.services.upload_service as upload_service  # Import the module, not the variable

UPLOAD_DIR = "app/uploads"
PLOTS_DIR = "app/plots"

os.makedirs(PLOTS_DIR, exist_ok=True)

def load_data(file_name: str | None = None, sheet_name: str | None = None):
    """
    Load the time series data from the latest uploaded Excel file (or specified one).
    Automatically cleans data, removes empty columns, and prepares GGR as a float time series.
    """
    if not file_name:
        file_name = upload_service.get_latest_file_name()
        print('latest file name', file_name)
        if not file_name:
            raise FileNotFoundError("No file has been uploaded yet.")

    file_path = os.path.join(UPLOAD_DIR, file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_name} not found in {UPLOAD_DIR}.")

    # Read Excel file
    df = pd.read_excel(file_path, sheet_name=sheet_name or 0, header=1)

    # Drop completely empty columns
    df = df.dropna(axis=1, how='all')

    # Ensure 'Date' column exists
    if 'Date' not in df.columns:
        raise ValueError("Expected a 'Date' column in the Excel sheet.")

    # Convert Date column to datetime and set as index
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)

    # Drop rows with NaN
    df = df.dropna(how='any')

    # Clean and convert GGR column
    if 'GGR' not in df.columns:
        raise ValueError("Expected a 'GGR' column in the Excel sheet.")

    df['GGR'] = (
        df['GGR']
        .replace({',': '', '\xa0': ''}, regex=True)
        .astype(float)
    )

    ts = df['GGR']
    return ts


def generate_time_series_chart(file_name: str | None = None, sheet_name: str | None = None):
    ts = load_data(file_name=file_name, sheet_name=sheet_name)
    print('finished generating time series chart')

    plt.figure(figsize=(12, 6))
    plt.plot(ts, label='GGR', color='steelblue')
    plt.title('Daily GGR Over Time')
    plt.xlabel('Date')
    plt.ylabel('GGR')
    plt.legend()

    # Include sheet name in filename if provided
    sheet_suffix = f"_{sheet_name}" if sheet_name else ""
    plot_path = os.path.join(PLOTS_DIR, f"time_series{sheet_suffix}.png")

    plt.savefig(plot_path, bbox_inches="tight")
    plt.close()
    return plot_path

def generate_seasonality_chart(file_name: str | None = None, sheet_name: str | None = None):
    ts = load_data(file_name=file_name, sheet_name=sheet_name)
    result = seasonal_decompose(ts, model='additive', period=7)
    result.plot()

    sheet_suffix = f"_{sheet_name}" if sheet_name else ""
    plot_path = os.path.join(PLOTS_DIR, f"seasonality{sheet_suffix}.png")

    plt.savefig(plot_path, bbox_inches="tight")
    plt.close()
    return plot_path


def generate_forecast_chart(file_name: str | None = None, sheet_name: str | None = None):
    ts = load_data(file_name=file_name, sheet_name=sheet_name)
    df_prophet = ts.reset_index().rename(columns={'Date': 'ds', 'GGR': 'y'})

    model = Prophet(daily_seasonality=True, weekly_seasonality=True)
    model.fit(df_prophet)

    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    fig = model.plot(forecast)

    sheet_suffix = f"_{sheet_name}" if sheet_name else ""
    plot_path = os.path.join(PLOTS_DIR, f"forecast{sheet_suffix}.png")

    fig.savefig(plot_path, bbox_inches="tight")
    plt.close(fig)
    return plot_path