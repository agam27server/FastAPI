from fastapi import FastAPI, Request, HTTPException, status # Import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException


app = FastAPI() # Create an instance of FastAPI
app.mount("/static", StaticFiles(directory="static"), name="static") # Mount static files (name must be "static" to match url_for("static", ...) in templates)
templates = Jinja2Templates(directory="templates")

posts: list[object] = [ # dummy list to return as response 
    
    {
        "id":1,
        "title":"Hello World",
        "content":"This is a post",
        "published":True,
        "author":"Agam"
    },
    {
        "id":2,
        "title":"Hello World2",
        "content":"This is a post2",
        "published":False,
        "author":"Agam2"
    }
    
]

@app.get("/",include_in_schema=False, name="home") # Decorator to create a route
@app.get("/posts",include_in_schema=False, name="posts") # include_in_schema is used to exclude the route from the api documentation(swagger/docs)
def home(request: Request):
    return templates.TemplateResponse(request,"home.html", {"posts": posts})

@app.get("/posts/{post_id}",include_in_schema=False, name="post_page")
def post_page(request: Request, post_id: int):
    for post in posts:
        title = post["title"][:50]
        if post["id"] == post_id:
            return templates.TemplateResponse(request,"post.html", {"post": post, "title": title})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.get("/api/posts")
def get_posts():
    return {"data": posts}

@app.get("/api/posts/{post_id}")
def get_post(post_id: int): 
    # type hint here help in handling
    # the error if the post_id is not an integer
    for post in posts:
        if post["id"] == post_id:
            return {"data": post}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )