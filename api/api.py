import datetime

from fastapi import FastAPI
from typing import Any, List

from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

from models import Show, ShowsResponse
from functions import StreamingCommunityWorker


# New response structure: {"details": ..., "status_code": ..., "success": ...}
class ResponseStructure(BaseModel):
    details: Any
    success: bool = True
    status_code: int

# New response class
class CustomResponse(JSONResponse):
    def __init__(self, content: Any, status_code: int = 200, *args, **kwargs):
        # Customize content and pass my new content...
        content = ResponseStructure(details=content, success=False if status_code != 200 else True, status_code=status_code)
        super().__init__(content=content.dict(), status_code=status_code, *args, **kwargs)


app = FastAPI(default_response_class=CustomResponse, title="StreamingCommunity Unofficial API", description="An unofficial API for StreamingCommunity website", version="1.0.0")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UP_START_TIME = datetime.datetime.now() # For the uptime

streamingcommunityWorker = StreamingCommunityWorker()
# Handle the 404 error. Use HTTP_exception_handler to handle the error
@app.exception_handler(StarletteHTTPException)
async def my_custom_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(content={"message": "Not found", "success": False, "code": exc.status_code}, status_code=exc.status_code)
    elif exc.status_code == 405:
        return JSONResponse(content={"message": "Method not allowed", "success": False, "code": exc.status_code}, status_code=exc.status_code)
    else:
        # Just use FastAPI's built-in handler for other errors
        return await http_exception_handler(request, exc)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    status_code = 422
    print(exc.errors())

    if exc.errors()[0]["type"] == "value_error.any_str.max_length":
        limit = str(exc.errors()[0]["ctx"]["limit_value"])
        return JSONResponse(content={"message": "The value entered is too long. Max length is " + limit, "success": False, "code": status_code}, status_code=status_code)
    elif exc.errors()[0]["type"] == "value_error.missing":
        missing = []
        for error in exc.errors():
            try:
                missing.append(error["loc"][1])
            except:
                missing.append(error["loc"][0])

        return JSONResponse(content={"message": "One or more fields are missing: " + str(missing), "succes": False, "code": status_code}, status_code=status_code)
    else:
        return JSONResponse(content={"message": exc.errors()[0]["msg"], "success": False, "code": status_code}, status_code=status_code)

@app.get("/")
async def root():
    return "Welcome to StreamingCommunity Unofficial API! By @Matt0550 on GitHub"

@app.get("/status")
def api_status(request: Request):
    # Get the API uptime without microseconds
    uptime = datetime.datetime.now() - UP_START_TIME
    uptime = str(uptime).split(".")[0]

    url = request.url
    url = url.scheme + "://" + url.netloc

    return {"api": {"status": "online", "uptime": uptime, "url": url}, "streamingcommunity": {"online": streamingcommunityWorker.checkStatus()}}

@app.get("/home")
async def get_home():
    # Get the home page from the Eurostreaming website
    home = streamingcommunityWorker.getHome()
    
    # Return a list of ShowsResponse objects
    return home

@app.get("/show")
async def get_show(url: str):
    # Get the show page from the Eurostreaming website
    show = streamingcommunityWorker.getShow(url)
    
    # Return a Show object
    return show