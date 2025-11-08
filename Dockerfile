# Use conda-forge Miniforge image (prebuilt binaries for arm64)
FROM condaforge/mambaforge:latest

# Set working directory
WORKDIR /app

# Create and activate environment
RUN mamba create -n ggr python=3.11 -y
SHELL ["conda", "run", "-n", "ggr", "/bin/bash", "-c"]

# Install dependencies in environment
RUN mamba install -n ggr -y \
    fastapi uvicorn pandas matplotlib statsmodels prophet reportlab apscheduler python-multipart openpyxl

# Copy application files
COPY ./app ./app

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["conda", "run", "-n", "ggr", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]