from fastapi import FastAPI, Request # Import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

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

@app.get("/api/posts")
def get_posts():
    return {"data": posts}

