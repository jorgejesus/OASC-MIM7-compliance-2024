# docker build -t oasc-mim7-api:0.0.1 .
# docker run -p 8000:8000 oasc-mim7-api:0.0.1
# http://localhost:8000/docs
FROM docker.io/python:3.12.5-slim-bookworm@sha256:c24c34b502635f1f7c4e99dc09a2cbd85d480b7dcfd077198c6b5af138906390

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY API/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

COPY API /app

EXPOSE 8000

CMD ["hypercorn", "api:app", "--bind", "0.0.0.0:8000"]
