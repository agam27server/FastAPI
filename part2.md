# Part 2 — Changes Since Part 1

> Note: this project is not yet a git repository (`git diff` reports
> "not a git repository"), so the changes below were captured by comparing the
> current file contents against what was documented in `part1.md`.
> See `part1.md` for the baseline codebase understanding and setup steps.

## 1. Summary
Since Part 1 (bare scaffold + a simple JSON/HTML `main.py`), the app moved from
returning inline HTML to a proper **Jinja2 templating + static assets** setup,
i.e. a real server-rendered blog homepage.

## 2. `src/fastapi_blog/main.py`

Previously (Part 1): a single inline `HTMLResponse` route and one JSON route,
no templates, no static files.

Now:
```python
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {"posts": posts})

@app.get("/api/posts")
def get_posts():
    return {"data": posts}
```

Key changes:
- **Added `Jinja2Templates(directory="templates")`** — renders HTML from files
  in `templates/` instead of building HTML strings in Python.
- **Added `StaticFiles` mount at `/static`, named `"static"`** — required so
  templates can call `url_for("static", path=...)` to reference CSS/JS/images.
  Without this mount, `url_for("static", ...)` raises
  `starlette.routing.NoMatchFound` (this was hit and fixed in this session).
- **`home()` now takes a `Request` and returns `templates.TemplateResponse(...)`**
  instead of returning a raw `HTMLResponse` string.
- **Two routes map to the same `home()` view**: `"/"` and `"/posts"`, both
  `include_in_schema=False` (hidden from `/docs`) and each given an explicit
  `name` (`"home"`, `"posts"`) so `url_for("home")` in templates resolves
  correctly — FastAPI/Starlette otherwise derives the route name from the
  function name, and stacking two `@app.get` decorators on one function would
  make the *last-applied* route win the name unless named explicitly.
- `GET /api/posts` JSON route is unchanged from Part 1.

## 3. New template: `templates/home.html`
Renders the `posts` list passed from `main.py`, extending a shared
`layout.html` base template. For each post it renders: author's profile
picture (`static/profile_pics/default.jpg` via `url_for('static', ...)`),
author name, date, title, and content — a typical blog post card using
Bootstrap-based classes (`content-section`, `article-title`, etc.).

## 4. New template: `templates/layout.html`
Shared base layout (Jinja2 `{% block content %}`) providing:
- `<head>` metadata, Open Graph tags, Google Fonts, Bootstrap 5 CSS/JS via CDN.
- App stylesheet: `url_for('static', path='css/main.css')`.
- Favicon/PWA icons and manifest: all referenced under `static/icons/` and
  `static/site.webmanifest` via `url_for('static', ...)`.
- Navbar with a light/dark theme toggle (vanilla JS, persisted to
  `localStorage`) and a `home` link via `url_for("home")`.
- Sidebar and footer boilerplate.

## 5. New `static/` directory
Static assets required by the templates, now mounted at `/static`:
```
static/
├── css/main.css          # app stylesheet (colors, spacing, dark mode, etc.)
├── icons/
│   ├── favicon.ico
│   ├── icon.svg
│   ├── icon.png
│   ├── icon-192.png
│   ├── icon-512.png
│   └── original.png
├── js/utils.js
├── profile_pics/default.jpg
└── site.webmanifest
```
- `css/main.css` defines CSS custom properties (fonts, colors, spacing) and
  styles for the navbar, content cards, buttons, and a dark-mode theme
  (`[data-bs-theme="dark"]` overrides), matching the classes used in
  `layout.html`/`home.html`.

## 6. Installing Jinja2 (required for `Jinja2Templates`)
`Jinja2Templates` needs the `jinja2` package installed — it's not pulled in
automatically unless already present via `fastapi[standard]`'s extras. Install
it with one of:

- Using **uv** (recommended, matches this project's `pyproject.toml`/`uv.lock`):
  ```
  uv add jinja2
  ```
- Using **pip** (if not using uv's dependency management):
  ```
  pip install jinja2
  ```

`uv add` updates `pyproject.toml`'s `dependencies` and `uv.lock` automatically,
keeping the lockfile in sync. Prefer `uv add` over `pip install` in this
project since `uv` is the package manager already in use.

## 7. Carried over from Part 1 (unchanged)
- `pyproject.toml`, `uv.lock`, `.gitignore`, `README.md` — no changes.
- `src/fastapi_blog/__init__.py` — still just the placeholder `main()`
  function, unrelated to the FastAPI `app` in `main.py`.
- Setup/run commands from Part 1 still apply:
  ```
  uv sync
  uv run fastapi dev src/fastapi_blog/main.py
  ```
