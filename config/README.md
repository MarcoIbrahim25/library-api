# 📚 Library Management System API

A Django REST Framework API for managing a library — users can view, borrow, and return books.
Admins and librarians can manage books and users. Authentication is handled with JWT tokens.

---

## 🚀 Features

* JWT authentication (`/api/login/`)
* CRUD for Books
* Checkout & Return Loans
* Track available copies
* Overdue detection
* Role-based permissions

---

## ⚙️ Setup

```bash
git clone <repo-url>
cd library-api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 🧩 Main Models

**User** – username, email, password, role (`admin` | `librarian` | `user`)
**Book** – title, author, isbn, total/available_copies, publish_date
**Loan** – user, book, checkout_date, due_date, return_date

---

## 🔐 Authentication

**POST `/api/login/`**

```json
{ "username": "admin", "password": "123" }
```

**Response**

```json
{ "token": "<JWT_ACCESS_TOKEN>" }
```

Use in headers:

```
Authorization: Bearer <token>
```

---

## 📚 API Endpoints

| Method | Endpoint                   | Access          | Description            |
| ------ | -------------------------- | --------------- | ---------------------- |
| GET    | `/api/books/`              | Public          | List all books         |
| POST   | `/api/books/`              | Admin/Librarian | Add a new book         |
| GET    | `/api/books/{id}/`         | Public          | Retrieve book details  |
| POST   | `/api/loans/checkout/`     | Authenticated   | Borrow a book          |
| POST   | `/api/loans/{id}/return/`  | Authenticated   | Return a borrowed book |
| GET    | `/api/loans/?overdue=true` | Authenticated   | List overdue loans     |

---

## 💻 Example Commands (Windows CMD)

```cmd
:: Login
curl -X POST http://127.0.0.1:8000/api/login/ -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"123\"}"

:: Add a Book
curl -X POST http://127.0.0.1:8000/api/books/ -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d "{\"title\":\"Django 5\",\"author\":\"Marco\",\"isbn\":\"1111\",\"total_copies\":3}"

:: Checkout
curl -X POST http://127.0.0.1:8000/api/loans/checkout/ -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d "{\"book_id\":1,\"days\":14}"

:: Return
curl -X POST http://127.0.0.1:8000/api/loans/1/return/ -H "Authorization: Bearer <TOKEN>"
```

---

## 🧪 Testing Checklist

* ✅ Create → Checkout → Return → Copies update
* ✅ Double checkout → 400 error
* ✅ Member tries to add a book → 403 forbidden
* ✅ Overdue filter shows correct loans

---

## ☁️ Deployment (PythonAnywhere)

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
```

Then configure the WSGI file in PythonAnywhere and restart the web app.

