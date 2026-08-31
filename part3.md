# Part 3 — Changes Since Part 2 (per `git-diff.txt`)

> Sequel to `part2.md`. This time an actual diff was available in
> `git-diff.txt` (git is still not initialized in this project's working
> directory, but a diff was captured/provided separately). See `part1.md` and
> `part2.md` for earlier history.

## 1. Summary
Part 2 added templating + static assets for a server-rendered homepage.
Part 3 adds a **post detail page**, a matching **JSON detail endpoint**, and
centralized **error handling** (both HTML and JSON) via FastAPI/Starlette
exception handlers.

## 2. `src/fastapi_blog/main.py` changes

### New imports
```python
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
```
- `HTTPException`, `status` — for raising typed HTTP errors (e.g. 404).
- `RequestValidationError` — FastAPI's validation error, raised automatically
  when request data fails pydantic/type validation.
- `JSONResponse` — for returning JSON error bodies on `/api/*` routes.
- `StarletteHTTPException` — aliased so the custom exception handler can catch
  **all** HTTP exceptions (including ones raised internally by Starlette, e.g.
  404 for unmatched routes), not just FastAPI's `HTTPException` subclass.

### New route: `GET /posts/{post_id}` → `post_page`
```python
@app.get("/posts/{post_id}", include_in_schema=False, name="post_page")
def post_page(request: Request, post_id: int):
    for post in posts:
        title = post["title"][:50]
        if post["id"] == post_id:
            return templates.TemplateResponse(request, "post.html", {"post": post, "title": title})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
```
- Renders a single post's detail page (`templates/post.html`, new in this
  part) by looking it up from the in-memory `posts` list.
- `post_id: int` path param — FastAPI validates/coerces it to `int`
  automatically; non-integer values trigger `RequestValidationError`.
- Raises a 404 `HTTPException` if no post matches — now handled centrally
  (see exception handlers below) instead of an unhandled crash.
- `title = post["title"][:50]` truncates the title (e.g. for use in
  `<title>` tag / page metadata).

### New route: `GET /api/posts/{post_id}` → `get_post`
```python
@app.get("/api/posts/{post_id}")
def get_post(post_id: int):
    for post in posts:
        if post["id"] == post_id:
            return {"data": post}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
```
- JSON counterpart to `post_page` — returns a single post as JSON, or a 404
  handled as JSON (via the exception handler, since the path starts with
  `/api`).

### New exception handler: `general_http_exception_handler`
```python
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    ...
```
- Catches **any** `HTTPException` raised anywhere in the app (404s from the
  routes above, or Starlette's own routing 404s).
- **Content negotiation by path prefix**: if `request.url.path` starts with
  `/api`, returns a `JSONResponse` with `{"detail": message}`; otherwise
  renders `templates/error.html` (new in this part) with the status code,
  title, and message — giving API clients JSON errors and browser users a
  styled error page from the same handler.
- Falls back to a generic message if `exception.detail` is empty.

### New exception handler: `validation_exception_handler`
```python
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    ...
```
- Catches FastAPI's automatic request validation failures (e.g. hitting
  `/posts/abc` where `post_id` expects an `int`).
- Same `/api` vs. HTML branching as above: JSON with
  `exception.errors()` (pydantic's detailed error list) for API routes, or
  `error.html` with a generic "Invalid request" message for HTML routes, both
  using `422 Unprocessable Content`.

## 3. `templates/home.html` changes
- Each post title is now a link to its detail page instead of a dead `href="#"`:
  ```html
  <a class="article-title" href="{{ url_for('post_page', post_id=post.id) }}">
      {{ post.title }}
  </a>
  ```
  This wires the homepage post list to the new `post_page` route by name,
  using the route's declared `name="post_page"` and passing `post_id`.
- Minor formatting/indentation cleanup around the article markup (no
  functional change beyond the link).

## 4. New template: `templates/post.html`
- Renders a single post's detail view (title, content, author, etc.), used by
  the new `post_page` route. Receives `post` and `title` from the view
  function.

## 5. New template: `templates/error.html`
- Generic error page used by both exception handlers for non-API requests.
  Receives `status_code`, `title`, and `message` and displays them, extending
  the shared `layout.html` (consistent styling/nav with the rest of the site).

## 6. Behavior summary (routes)
| Route | Method | Purpose | On not found |
|---|---|---|---|
| `/` , `/posts` | GET | Blog homepage (post list) | — |
| `/posts/{post_id}` | GET | Post detail page (HTML) | 404 → `error.html` |
| `/api/posts` | GET | All posts (JSON) | — |
| `/api/posts/{post_id}` | GET | Single post (JSON) | 404 → JSON `{"detail": ...}` |

## 7. Carried over from Part 2 (unchanged)
- `Jinja2Templates` + `StaticFiles` mount setup, `static/` assets,
  `layout.html` base template — all unchanged from Part 2.
- `pyproject.toml`, `uv.lock`, `.gitignore`, `README.md`,
  `src/fastapi_blog/__init__.py` — no changes.
- Jinja2 install note from Part 2 (`uv add jinja2`) still applies.
