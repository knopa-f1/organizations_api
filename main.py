import uvicorn
from fastapi import FastAPI

from app.api.endpoints import buildings, activities, organizations

app = FastAPI()

app.include_router(buildings.router)
app.include_router(activities.router)
app.include_router(organizations.router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Organization API server"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
