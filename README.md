# Royasazanjavan

A full-featured Django web platform for [royasazanjavan.org](https://royasazanjavan.org) — offering online courses, a product shop, articles, and a comprehensive admin dashboard.

## 🌐 Live Site

[https://royasazanjavan.org](https://royasazanjavan.org)

---

## ✨ Features

- **Accounts** — Custom user model, email-based authentication, email verification, password reset, and Google OAuth2 login
- **Courses** — Online course catalog with video lessons, ratings, and progress tracking
- **Shop** — Product listings with cart, checkout, and order management
- **Articles** — Blog/article system with categories, tags, and comments
- **Orders** — Order processing with coupon/discount support
- **Files** — Excel file upload and management
- **Dashboard** — Staff/admin panel for managing all content, users, orders, and site settings
- **Website** — Public pages: home, about, contact, FAQ, job applications, newsletter, testimonials, and more
- **SEO** — Sitemaps, robots.txt, and meta support built in
- **Security** — Rate limiting, CSRF protection, HSTS, secure cookies in production
- **Caching** — Redis-backed caching and session storage

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2 |
| Database | PostgreSQL |
| Cache / Sessions | Redis (`django-redis`) |
| Auth | Custom backend + Google OAuth2 (`social-auth-app-django`) |
| Rate Limiting | `django-ratelimit` |
| Email | Console (dev) / Gmail SMTP (prod) |
| Containerization | Docker + Docker Compose |
| Web Server | Nginx |
| Process Manager | Supervisor |
| Frontend | Bootstrap 5, AOS, Swiper, GLightbox |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL
- Redis
- Docker & Docker Compose (optional but recommended)

### 1. Clone the repository

```bash
git clone https://github.com/amirhamidi2001/royasazanjavan.git
cd royasazanjavan
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000

DATABASE_NAME=your_db_name
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

REDIS_URL=redis://localhost:6379/1

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your-google-client-id
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your-google-client-secret

# Required only in production (DEBUG=False)
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 4. Apply migrations and run

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 5. (Optional) Seed sample data

```bash
python manage.py seed_data       # Articles
python manage.py seed_courses    # Courses
python manage.py seed_products   # Shop products
```

---

## 🐳 Running with Docker

```bash
docker-compose up --build
```

---

## 📁 Project Structure

```
royasazanjavan/
├── accounts/       # User auth, registration, OAuth2 pipeline
├── articles/       # Blog articles, categories, tags, comments
├── cart/           # Shopping cart logic and context processor
├── core/           # Django project settings and root URLs
├── courses/        # Online courses, videos, ratings, progress
├── dashboard/      # Staff dashboard (CRUD for all modules)
├── files/          # Excel file uploads
├── orders/         # Orders, checkout, coupons
├── shop/           # Products and categories
├── website/        # Public pages, contact, newsletter, partners
├── static/         # CSS, JS, vendor libraries
├── templates/      # HTML templates
├── media/          # User-uploaded files
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 🔐 Authentication

- Email/password with mandatory email verification
- Google OAuth2 (sign in with Google)
- Custom pipeline to link social accounts to existing users

---

## 📄 License

This project is licensed under the terms of the [LICENSE](LICENSE) file.

---

## 👤 Author

**Amir Hamidi**  
GitHub: [@amirhamidi2001](https://github.com/amirhamidi2001)