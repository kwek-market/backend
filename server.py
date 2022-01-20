import uvicorn

if __name__ == "__main__":
    uvicorn.run('kwek.asgi:application', reload=True)