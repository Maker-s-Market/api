FROM python:3.10-alpine

RUN mkdir app

WORKDIR /app

ADD requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app/.


# It's necessary to expose the port used in the api on the dockerfile 
EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]