FROM python:3.9-slim

ENV TZ="Asia/Bangkok"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ libgl1 libglib2.0-0

RUN pip install uvicorn

COPY requirements.txt ./ 

RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src

WORKDIR /app/src

EXPOSE 3015

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "3016","--reload"]
