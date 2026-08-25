from fastapi import FastAPI # Import FastAPI
from fastapi.responses import HTMLResponse # Import HTMLResponse

app = FastAPI() # Create an instance of FastAPI

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

@app.get("/",response_class=HTMLResponse) # Decorator to create a route 
def home():
    return f"<h1>{posts[0]["content"]}</h1>"

@app.get("/api/posts")
def get_posts():
    return {"data": posts}

# we can view the api documentation at http://localhost:8000/docs