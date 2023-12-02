FROM python:3.10-alpine

RUN mkdir app

WORKDIR /app

ADD requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app/.


EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]