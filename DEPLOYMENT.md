# 🚀 Cloud Deployment Guide for Disaster Relief DBMS

This guide provides step-by-step instructions to deploy the **Flask + MySQL Disaster Relief Management System** to the cloud for free.

---

## 📋 Prerequisites
1. A free GitHub account ([github.com](https://github.com))
2. Push this project to a GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for deployment"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```

---

## 🌟 Option 1: Render (Web Service) + TiDB Cloud / Aiven (Free Cloud MySQL) — *Recommended*

### Step 1: Create a Free Cloud MySQL Database
Choose one of these free MySQL cloud providers:

#### Choice A: TiDB Cloud (Serverless MySQL - 100% Free Forever)
1. Go to [tidbcloud.com](https://tidbcloud.com) and sign up (Free).
2. Click **Create Cluster** -> Select **Serverless (Free)**.
3. Once created, click **Connect** -> Choose **PyMySQL / Python**.
4. Copy the connection string or details (`Host`, `Port`, `User`, `Password`, `Database`).
5. Open the TiDB SQL Editor and paste/run the contents of `database/schema.sql` and `database/seed.sql`.

#### Choice B: Aiven for MySQL (Free Tier)
1. Go to [aiven.io](https://aiven.io) and create a free account.
2. Create a new **MySQL** service on the free tier.
3. Copy the `Service URI` (e.g., `mysql://avnadmin:password@host:port/defaultdb?ssl-mode=REQUIRED`).

---

### Step 2: Deploy the Flask App to Render
1. Go to [render.com](https://render.com) and sign in with GitHub.
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Fill in the settings:
   - **Name**: `disaster-relief-dbms`
   - **Region**: Closest to your database region
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`
5. Under **Environment Variables**, add:
   - `SECRET_KEY` = `your-secret-key-12345`
   - `FLASK_ENV` = `production`
   - `FLASK_DEBUG` = `False`
   - `DATABASE_URL` = `<Your Cloud MySQL Connection URL>` *(or individual DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)*
   - `DB_SSL` = `true` *(if using TiDB or Aiven)*
6. Click **Deploy Web Service**.
7. Render will build and provide a live public URL (e.g. `https://disaster-relief-dbms.onrender.com`).

---

## 🚂 Option 2: Railway (All-In-One: App + MySQL)

Railway allows deploying both your Python Flask app and a MySQL database in a single project.

1. Go to [railway.app](https://railway.app) and sign in with GitHub.
2. Click **New Project** -> **Provision MySQL**.
3. In the MySQL service, go to **Connect** and copy the `MYSQL_URL` / `DATABASE_URL`.
4. Use Railway's Query editor or connect locally to run `database/schema.sql` and `database/seed.sql`.
5. Click **+ New Service** -> **GitHub Repo** -> Select your repo.
6. Under Service **Variables**, add:
   - `DATABASE_URL` = `${{MySQL.MYSQL_URL}}`
   - `SECRET_KEY` = `disaster-relief-secret-key-2026`
   - `PORT` = `5000`
7. Under **Settings** -> **Networking**, click **Generate Domain**.
8. Your app is live!

---

## 🐍 Option 3: PythonAnywhere (Built-in Free MySQL)

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com).
2. Go to the **Databases** tab and initialize your free MySQL instance with a password.
3. Create a database named `disaster_relief_db`.
4. Open a **Bash Console** in PythonAnywhere:
   ```bash
   git clone https://github.com/<your-username>/<your-repo-name>.git
   cd <your-repo-name>
   pip3 install -r requirements.txt --user
   mysql -u <username> -h <username>.mysql.pythonanywhere-services.com -p <username>$disaster_relief_db < database/schema.sql
   mysql -u <username> -h <username>.mysql.pythonanywhere-services.com -p <username>$disaster_relief_db < database/seed.sql
   ```
5. Go to the **Web** tab -> **Add a new web app** -> Choose **Manual Configuration** -> **Python 3.10**.
6. Set the **Source code** path to `/home/<username>/<repo-name>`.
7. Edit the WSGI configuration file:
   ```python
   import sys
   import os

   path = '/home/<username>/<your-repo-name>'
   if path not in sys.path:
       sys.path.append(path)

   from app import app as application
   ```
8. Set environment variables or configure `.env` with your PythonAnywhere MySQL credentials.
9. Click **Reload** to go live!

---

## 🐳 Option 4: Self-Hosted Docker Deployment

If you have a VPS or server with Docker and Docker Compose installed:

```bash
docker compose up -d --build
```
The app will be live at `http://<your-server-ip>:5000` with the MySQL database pre-seeded and running in a dedicated container.
