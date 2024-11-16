FROM python:3.10-slim

WORKDIR /code 

COPY requirements.txt . /code/

RUN pip install --no-cache-dir -r requirements.txt 

COPY . /code/

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]