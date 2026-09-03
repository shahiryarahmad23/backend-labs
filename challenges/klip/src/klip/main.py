from fastapi import FastAPI

from klip.api.v1 import route as auth_router

app = FastAPI()

app.include_router(auth_router)


@app.get("/health")
def health():
    return {"Status : okay"}
