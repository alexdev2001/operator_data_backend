FROM condaforge/mambaforge:latest

WORKDIR /app

# Create env
RUN mamba create -n ggr python=3.11 -y

# Activate env and install dependencies (all prebuilt)
RUN mamba run -n ggr mamba install -y \
    fastapi uvicorn pandas matplotlib statsmodels reportlab \
    apscheduler python-multipart openpyxl prophet=1.1

# Copy app files
COPY ./app ./app

EXPOSE 8000

# Run the app
CMD ["conda", "run", "-n", "ggr", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]