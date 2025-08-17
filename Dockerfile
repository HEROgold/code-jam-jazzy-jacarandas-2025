# Build instructions:
# docker --build -t jazzy_jacarandas .
# docker run -it --rm -p 3000:3000 -p 8000:8000 jazzy_jacarandas
FROM python:3.13-slim
WORKDIR /app

ENV REFLEX_PORT=3000
ENV REFLEX_BACKEND_PORT=8000

# Install requirements and copy the code into the container
# python:3.13-slim doesn't include unzip or curl which are required by webapp
RUN apt-get update && apt-get install -y --no-install-recommends unzip curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# frontend, backend ports
EXPOSE 3000 8000

RUN groupadd -r appuser && useradd -r -g appuser -d /home/appuser -m appuser
RUN chown -R appuser:appuser /app /home/appuser
USER appuser

CMD ["reflex", "run", "--backend-host", "0.0.0.0", "--backend-port", "8000"]