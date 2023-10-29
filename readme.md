# API Documentation


## Run API locally

```sh
    uvicorn main:app --reload
```


## Run API + DB with docker

```sh
   docker-compose up --build -d
```

## Run DB with docker

```sh
   docker-compose up db --build -d
```

## Run tests

```sh
    python3 -m pytest tests/
```