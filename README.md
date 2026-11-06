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

## Deploy to Render

1. Create a PostgreSQL database on Render and copy its **internal** connection URL.
2. Create one Web Service connected to this repository.
3. Set the Root Directory to the repository root and Build Command to `bash build.sh`.
4. Set Start Command to `cd backend && gunicorn config.wsgi:application`.
5. Set environment variables: `DATABASE_URL` (the database URL), `SECRET_KEY` (a long random value), `DEBUG=0`, `ALLOWED_HOSTS` (your Render hostname), and `CSRF_TRUSTED_ORIGINS=https://your-service.onrender.com`. Set `SITE_BASE_URL` to the public HTTPS service URL.
6. After deployment, use the Render Shell to run `cd backend && python manage.py seed_demo`.

The service uses WhiteNoise for collected static files. Uploaded files are not used; menu photos are external image URLs entered by the owner.
