# Deployment Documentation

## Overview
Dreams Fitness Center was deployed using a production-ready Django setup with PostgreSQL and Stripe integration.

---

## Local Deployment

1. Clone the repository
2. Create virtual environment
3. Install dependencies
4. Set environment variables
5. Run migrations
6. Create superuser
7. Run development server

---

## Production Deployment

### Environment Variables


## Deployment

- Platform: **Heroku**
- Web Server: **Gunicorn**
- Static Files: **Whitenoise**
- Database: **PostgreSQL**
- Environment variables used for sensitive data

Deployment Steps:
1. Create Heroku app
2. Configure environment variables
3. Install production dependencies
4. Run migrations
5. Collect static files
6. Deploy via GitHub integration


## Static & Media Files
- Static files collected using `collectstatic`
- Media files served via cloud storage or platform configuration


## Deployment Verification

| Check | Status |
|---|---|
Site loads | Pass |
Admin access | Pass |
Checkout | Pass |
Media files | Pass |
