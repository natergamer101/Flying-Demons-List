# Game Leaderboard

A Flask-based web application for submitting and tracking game level completions with YouTube proof videos.

## Features

- **User Registration & Authentication**: Secure account creation and login
- **Claim Submission**: Submit level completion claims with YouTube proof links
- **Community Voting**: Vote on approved claims to determine rankings
- **Dynamic Leaderboard**: Top 50 ranked claims with embedded YouTube videos
- **Points System**: Earn points based on ranking (51 - rank formula)
- **Admin Dashboard**: Review and approve/reject user submissions
- **User Profiles**: View all claims and total points for any user

## Technology Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Security**: CSRF protection, password hashing, session management

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- PostgreSQL database

### 2. Clone and Setup

```bash
cd c:\git\Leaderboard
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Configure Database

Create a PostgreSQL database:
```sql
CREATE DATABASE leaderboard_dev;
```

Create a `.env` file (copy from `.env.example`):
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-random-secret-key-here
DEV_DATABASE_URL=postgresql://username:password@localhost/leaderboard_dev
```

### 4. Initialize Database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. Create Admin User

```bash
flask create-admin
```

### 6. Seed Levels (Optional)

```bash
flask seed-levels
```

### 7. Run the Application

```bash
flask run
```

Visit http://localhost:5000

## Deployment Options

The repository has always been a normal Flask application; the GitHub Pages
support described later is optional.  If you want the site to be **dynamic and
interactive**, you must host it somewhere that can run Python (Heroku, Render,
Railway, your own VPS, etc.).  The tools below make that easy:

- A `Procfile` is included for Heroku-style deployments.
- A `Dockerfile` is provided if you prefer containerizing the app.
- The `requirements.txt` now lists `gunicorn` to serve the app in production.

### Heroku (example)

1. Install the Heroku CLI and log in:
   ```bash
   heroku login
   ```
2. Create an app:
   ```bash
   heroku create your-app-name
   ```
3. (Optional) provision a database:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```
4. Push the code:
   ```bash
   git push heroku main
   ```

Heroku will automatically detect the `Procfile` and install dependencies.  Set
any required environment variables with `heroku config:set SECRET_KEY=...` and
`heroku config:set DATABASE_URL=...`.

### Render

Render is another popular (and free‑tier) platform that can build directly from
GitHub.  To deploy this application on Render:

1. Sign in at https://render.com and create a new **Web Service**.
2. Connect your GitHub account and select the `Flying-Demons-List` repository.
3. Use the `Python` environment.
4. Set the **Build Command** to something that upgrades pip and installs
dependencies into the service's environment.  The default `pip` on Render is a
little old and sometimes skips packages, which is why you saw `gunicorn: command
not found` in the log.  A safe command is:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
5. Set the **Start Command** to:
   ```bash
   gunicorn run:app --bind 0.0.0.0:$PORT
   ```
6. (Optional) specify environment variables such as `SECRET_KEY` and
   `DATABASE_URL` in the service settings.  Render provides a managed PostgreSQL
   plan you can add under the **Addons** section, or you can use a separate
   database host.

Render will automatically build and deploy on every push to the selected
branch (typically `main`).  You can also create a `render.yaml` file with the
configuration below and push it to version control; Render will pick it up
automatically.

```yaml
services:
  - type: web
    name: leaderboard
    env: python
    branch: main
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn run:app --bind 0.0.0.0:$PORT
    plan: free
    disk: 512
```

Once deployed, the service URL will host the full dynamic application with
login, submission forms, and database interactions.  You no longer need to run
`flask freeze` or use GitHub Pages unless you want a static demo copy.

### Running locally with Gunicorn

```bash
pip install gunicorn
export FLASK_APP=run.py
export FLASK_ENV=production
gunicorn run:app --bind 0.0.0.0:5000
```

### Using the included Dockerfile

```bash
docker build -t leaderboard .
docker run -p 5000:5000 \
    -e SECRET_KEY=yourkey \
    -e DATABASE_URL=sqlite:///dev.db \
    leaderboard
```

Once the app is running on a host, you will have a fully interactive site with
login, submissions, and database-backed features.  You no longer need to run
`flask freeze` or deal with the `gh-pages` branch unless you still want a
static demonstration copy.

```
## Project Structure

```
c:\git\Leaderboard\
├── app/                    # Application package
│   ├── auth/              # Authentication routes
│   ├── main/              # Main pages
│   ├── claims/            # Claim submission & voting
│   ├── users/             # User profiles
│   ├── admin/             # Admin dashboard
│   ├── templates/         # HTML templates
│   ├── static/            # CSS, JS files
│   └── models.py          # Database models
├── migrations/            # Database migrations
├── config.py              # Configuration
├── run.py                 # Application entry point
└── requirements.txt       # Python dependencies
```

## Usage

### For Users
1. Register an account
2. Submit claims for levels you've beaten with YouTube proof links
3. Vote on other users' approved claims
4. View your profile to see your total points

### For Admins
1. Login with admin credentials
2. Review pending claims
3. Approve or reject submissions
4. Manage game levels

### Generating a Static GitHub Pages Site
This application is dynamic by default and requires a Python backend plus
a database. However, you can freeze a *snapshot* of the publicly-visible
pages (home, leaderboard, user profiles, etc.) and deploy that output to
GitHub Pages or any other static host.

```bash
# install the extra dependency
pip install Frozen-Flask

# make sure your database has whatever data you want included (seed it)
flask seed-levels
# optionally create some users/claims

# run the freeze command
flask freeze
```

The command will create a `build/` directory containing `.html`, CSS,
JS and image assets. Commit that directory to a branch such as
`gh-pages` or push it to another repo configured for Pages. Note that
forms, login/logout, and any action requiring a server are non-functional
in the static snapshot – the site is read‑only.

If deploying to a *project page* (e.g. `https://username.github.io/repo/`),
set the base URL before freezing so asset paths resolve correctly.  The
`flask freeze` command now writes its output to a top‑level `build/`
directory rather than inside `app/`.

```bash
export FREEZER_BASE_URL="https://username.github.io/repo/"
flask freeze
```

Freezer will crawl routes starting at `/`; since GitHub Pages serves
relative to the repo path the base URL helps generate correct links.

Also, if the local database cannot be reached the freeze command will
still run but user profile pages will be omitted (it simply prints a
warning). You don’t need a full PostgreSQL install just to build the
static snapshot – seed whatever rows you want beforehand.

```shell
# example branch workflow
git checkout --orphan gh-pages
rm -rf *
cp -R build/* .
git add .
git commit -m "Deploy static site"
git push origin gh-pages
```

For ongoing changes, regenerate the snapshot and update the branch.

> **Automatic builds via GitHub Actions**
>
> A workflow (`.github/workflows/pages.yml`) is included which runs on every
> push to `main`. It installs dependencies, initializes an SQLite database
> with a demo user/claim, runs `flask freeze`, and then deploys the resulting
> `build/` folder to GitHub Pages using the official Pages actions.  You only
> need to enable Pages in the repository settings (choose the `gh-pages`
> branch or the `pages` artifact – the action configures this for you).


## Security Features

- Password hashing (bcrypt via werkzeug)
- CSRF protection on all forms
- Session security (HttpOnly, SameSite cookies)
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (WTForms)
- XSS prevention (Jinja2 auto-escaping)

## License

This project is open source and available for educational purposes.
# trigger action
