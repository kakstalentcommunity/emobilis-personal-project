# TableTap

TableTap is a small QR ordering app for a restaurant. Guests scan a table card, browse the menu and send an order. Kitchen staff update each order; waiters serve dishes and record cash or manually confirmed M-Pesa payments. Owners manage the menu and tables and view sales insights.

## Run locally

Requirements: Python 3.10+ and Node.js 20+.

1. In a terminal, create and activate a virtual environment, then install the backend packages:

   ```powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r backend\requirements.txt
   ```

2. Install the frontend packages once:

   ```powershell
   cd frontend
   npm install
   cd ..
   ```

3. Terminal 1 builds the one React file and rebuilds it as you make changes:

   ```powershell
   cd frontend
   npm run watch
   ```

4. Terminal 2 prepares a demo restaurant and runs Django:

   ```powershell
   cd backend
   python manage.py migrate
   python manage.py seed_demo
   python manage.py runserver 0.0.0.0:8000
   ```

   Staff sign in at `/staff/login/`. Demo usernames are `owner`, `kitchen`, and `waiter`; each password is `demo1234`. Open `/owner/tables/` to find table QR links. The Django admin is at `/admin/`.

For a phone on the same Wi-Fi, add the laptop's local IP address to `ALLOWED_HOSTS` and start the server on `0.0.0.0`. Set `SITE_BASE_URL=http://LAPTOP-IP:8000` before running Django so printed QR codes point to the laptop.

## How it works

- `backend/config/` contains settings, the main URL list and the WSGI entry point.
- Each feature folder (`accounts`, `menu`, `tables`, `orders`, `analytics`) has its own models, views, URL patterns and admin setup. Django models store the relational data in SQLite locally, or PostgreSQL when `DATABASE_URL` is set.
- `backend/templates/` contains Django HTML pages. Django renders ordinary forms and manager pages; it places JSON menu data into the diner page with `json_script`.
- `backend/static/` holds the shared black-and-white CSS, small browser scripts and SVG images.
- `frontend/src/` contains four small React islands. Vite bundles them together into `backend/static/js/react/app.js`; Django includes that bundle only on the diner, kitchen, waiter and dashboard pages. The React screens call plain Django JSON views under `/api/`.
- Orders are checked and priced again on the server. Kitchen and waiter screens poll the server at intervals, so no separate realtime service is needed.

## Deploy with Vercel and Render

The Django app and its frontend are hosted on Vercel. Render provides the PostgreSQL database.

### 1. Create the Render database

1. In Render, create a PostgreSQL database. Choose a region close to your Vercel deployment if available.
2. Copy its **External Database URL**. Vercel is outside Render's private network, so it cannot use Render's internal URL.

### 2. Import the repository into Vercel

1. In Vercel, import this GitHub repository and set the project Root Directory to the repository root (the folder containing `vercel.json`).
2. Keep the build command from `vercel.json`: `npm --prefix frontend ci && npm --prefix frontend run build`.
3. Set these environment variables for **Production**:

   | Variable | Value |
   | --- | --- |
   | `DATABASE_URL` | Render's External Database URL |
   | `SECRET_KEY` | A new, long random secret |
   | `DEBUG` | `0` |
   | `ALLOWED_HOSTS` | `.vercel.app` (and your custom domain, if you add one) |
   | `CSRF_TRUSTED_ORIGINS` | `https://*.vercel.app` (and `https://your-domain.example` if used) |
   | `SITE_BASE_URL` | The production URL, such as `https://your-project.vercel.app` |

   Use the Vercel production URL as `SITE_BASE_URL` so table QR codes lead to the live site. Keep the database URL and secret in Vercel's environment settings; do not commit them into the repository.

4. Deploy. Vercel detects the Django app under `backend/`; the root `requirements.txt` installs its Python dependencies. The frontend build writes the React bundle into Django's static directory, and Vercel serves Django's collected static files.

### 3. Initialize the production database

Run these commands from the repository root in PowerShell after setting up your local virtual environment. Use the Render **External Database URL** for this one-time setup:

```powershell
$env:DATABASE_URL = "paste-the-render-external-database-url-here"
python -m pip install -r requirements.txt
python backend\manage.py migrate
python backend\manage.py seed_demo
Remove-Item Env:DATABASE_URL
```

The demo staff accounts are `owner`, `kitchen`, and `waiter`, each with password `demo1234`. Change those passwords before using the site with real staff. To apply future model migrations, run `python backend\manage.py migrate` against the same production `DATABASE_URL` before relying on the new schema.

For a custom domain, add it in Vercel and include it in `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and `SITE_BASE_URL` as appropriate. Uploaded files are not used; menu photos are stored as image URLs.
