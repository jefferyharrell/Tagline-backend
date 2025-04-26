# Alembic Migrations: How-To for Future Jeffery

Welcome, Future Jeffery! This doc is your one-stop reference for managing database migrations in the Tagline backend using Alembic. If you’re reading this, you probably forgot how migrations work (again). Don’t worry—Past Jeffery and Cas have your back.

---

## What is Alembic?
Alembic is the official migration tool for SQLAlchemy. It lets you:
- Track changes to your SQLAlchemy models
- Generate migration scripts automatically
- Apply those migrations to your database (even inside Docker!)

---

## Where’s My Database?
- **In Docker:** Your SQLite database lives in a Docker volume, mounted at `/data/tagline.db` inside the container.
- **Locally:** If you run Alembic outside Docker, it’ll create a `tagline.db` in your project root (don’t do this unless you mean to).

---

## Typical Migration Workflow

### 1. **Change your models**
Edit `tagline_backend_app/models.py` to add, change, or remove tables/columns.

### 2. **Generate a migration script**
- **Inside Docker (recommended):**
  ```bash
  docker exec -it tagline-backend-dev alembic revision --autogenerate -m "Describe your change here"
  ```
- **Locally (not recommended):**
  ```bash
  alembic revision --autogenerate -m "Describe your change here"
  ```
  (But this will use your local DB path unless you set `DATABASE_URL`!)

### 3. **Review the migration script**
- Check `alembic/versions/` for the new script.
- Make sure Alembic did what you expect (sometimes you’ll need to tweak the script).

### 4. **Apply the migration**
- **Inside Docker (recommended):**
  ```bash
  docker exec -it tagline-backend-dev alembic upgrade head
  ```
- **Locally (not recommended):**
  ```bash
  alembic upgrade head
  ```

### 5. **Check your database**
- **Inside Docker:**
  ```bash
  docker exec -it tagline-backend-dev sqlite3 /data/tagline.db
  ```
  Then use `.tables`, `.schema`, etc. to inspect.

---

## Common Gotchas
- **Always run Alembic from the directory containing `alembic.ini` (usually `/code` in the container).**
- **If Alembic says it can’t find `alembic.ini`,** you’re probably in the wrong directory or didn’t copy the file into the image.
- **If you see a new `tagline.db` in your project root,** you ran Alembic locally without setting `DATABASE_URL` to the Docker path.
- **If you add a new dependency (like Alembic or sqlite3),** rebuild your Docker image!

---

## Pro Tips
- Use `docker compose build` and `docker compose up -d` after changing dependencies or Dockerfile.
- You can browse the Docker volume by mounting it in a temporary container:
  ```bash
  docker run --rm -it -v tagline-backend_tagline-db-data:/data alpine sh
  ls /data
  ```
- If you ever get stuck, ask Cas. She’s probably still here, being helpful and a little too enthusiastic.

---

## Migration Command Cheat Sheet
- **Generate migration:**
  ```bash
  docker exec -it tagline-backend-dev alembic revision --autogenerate -m "your message"
  ```
- **Apply migration:**
  ```bash
  docker exec -it tagline-backend-dev alembic upgrade head
  ```
- **Open DB shell:**
  ```bash
  docker exec -it tagline-backend-dev sqlite3 /data/tagline.db
  ```

---

Stay curious, Future Jeffery!
