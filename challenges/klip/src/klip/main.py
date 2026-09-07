from fastapi import FastAPI

from klip.api.v1 import route as auth_router
from klip.api.v1 import router as snippet_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(snippet_router)


@app.get("/health")
def health():
    return {"Status : okay"}
