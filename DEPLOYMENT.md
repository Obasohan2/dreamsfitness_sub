# Deployment Documentation

## Overview

Dreams Fitness Center is a full-stack Django web application deployed using a production-ready configuration with **PostgreSQL** and **Stripe** integration.  
The project was developed using **VS Code** with **Git** for version control and deployed to **Heroku**.

---

## Local Deployment

To run the project locally, follow these steps:

1. Create or clone the project repository.
2. Create and activate a virtual environment.
3. Install project dependencies:
   ```bash
   pip install -r requirements.txt

4. Set the required environment variables.
- Then create Procfile

5. Apply database migrations:
- python manage.py migrate

6. Create a superuser:
- python manage.py createsuperuser

7. Run the development server:
- python manage.py runserver

---

## Production Deployment

### Platform & Technologies

- Platform: **Heroku**
- Web Server: **Gunicorn**
- Static Files: **Whitenoise**
- Database: **PostgreSQL**
- Payments: **Stripe**
Sensitive data is managed securely using environment variables.

---

### Environment Variables

The following environment variables were configured in Heroku:

- DATABASE_URL
- SECRET_KEY
- STRIPE_PUBLIC_KEY
- STRIPE_SECRET_KEY
- DISABLE_COLLECTSTATIC

---

### Heroku Setup

1. Log in to [Heroku](https://id.heroku.com/login) or create an account.
2. Click **New** and select **Create New App**.
3. Enter a unique app name.
4. Select **Europe** as the region.
5. Click **Create App**.

---

## Connecting the Database

1. Open the **Heroku App Dashboard**.
2. Navigate to **Settings**.
3. Click **Reveal Config Vars**.
4. Add the following configuration variables:

| Key | Value |
|----|------|
| `DATABASE_URL` | PostgreSQL database URL |
| `DISABLE_COLLECTSTATIC` | `1` |

---

## Django Database Configuration Notes

To connect Django to the Heroku PostgreSQL database, ensure the following packages are installed:

```bash
pip install dj-database-url psycopg2-binary
```

Add the required packages to your `requirements.txt` file:

```txt
dj-database-url
psycopg2-binary
```

---

## Deployment via GitHub

1. Commit and push all changes to your GitHub repository:
   ```bash
   git add .
   git commit -m "Prepare app for deployment"
   git push origin main
   ```
2. Open the **Heroku App Dashboard**.
3. Navigate to the **Deploy** tab.
4. Under **Deployment method**, connect the application to your GitHub repository.
5. Choose one of the following:
   - **Manual Deploy** – deploy manually when needed
   - **Automatic Deploy** – deploy automatically on every push to the selected branch
6. Deploy the **main** branch.
7. Click **View** to access the live application.

---

## Static & Media Files

- Static files are managed using **WhiteNoise**
- Static files are collected automatically during deployment using `collectstatic`
- Media files are served via **AWS cloud storage** or platform configuration

---

## Deployment Verification

| Feature        | Status |
|---------------|--------|
| Site loads     | Pass   |
| Admin access   | Pass   |
| Checkout       | Pass   |
| Media files    | Pass   |
