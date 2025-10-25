# 📘 Project Documentation – Library Management System API

## 1. Overview

The **Library Management System API** is built using **Django REST Framework** and provides a backend service for managing books, users, and loans.
It supports authentication using **JWT (Bearer tokens)** and implements role-based access control for Admins, Librarians, and regular Users.

---

## 2. Project Goals

* Manage library books efficiently (add, update, delete, search).
* Allow authenticated users to borrow and return books.
* Ensure only authorized roles (Admin/Librarian) can modify inventory or manage users.
* Track book availability and overdue loans.

---

## 3. Technologies Used

| Component                 | Description          |
| ------------------------- | -------------------- |
| **Django 4.x**            | Web framework        |
| **Django REST Framework** | API layer            |
| **SimpleJWT**             | JWT authentication   |
| **SQLite**                | Development database |
| **Python 3.11+**          | Programming language |

---

## 4. System Architecture

**Type:** RESTful API (Backend only)
**Layers:**

1. **Models** → define data structure
2. **Serializers** → convert models <-> JSON
3. **Views/ViewSets** → handle requests (CRUD + custom actions)
4. **Permissions** → manage role-based access
5. **URLs/Routers** → define endpoints
6. **Authentication** → JWT Bearer tokens

---

## 5. Data Models

### 5.1 Book

| Field              | Type                             | Notes              |
| ------------------ | -------------------------------- | ------------------ |
| `title`            | CharField(200)                   | Indexed for search |
| `author`           | CharField(100)                   | Indexed            |
| `isbn`             | CharField(13)                    | Unique             |
| `category`         | CharField(100, null=True)        | Optional           |
| `total_copies`     | PositiveIntegerField             | Default = 1        |
| `available_copies` | PositiveIntegerField             | Default = 1        |
| `publish_date`     | DateField                        | Optional           |
| `created_at`       | DateTimeField(auto_now_add=True) | —                  |
| `updated_at`       | DateTimeField(auto_now=True)     | —                  |

### 5.2 Loan

| Field           | Type                | Notes                 |
| --------------- | ------------------- | --------------------- |
| `user`          | FK → User           | Linked to borrower    |
| `book`          | FK → Book           | Linked book           |
| `checkout_date` | DateTime            | Default = now         |
| `due_date`      | DateTime            | Calculated            |
| `return_date`   | DateTime, null=True | Null = still borrowed |

**Rules:**

* A user cannot have more than one active loan for the same book.
* When loan created → `available_copies -= 1`.
* When returned → `available_copies += 1`.

### 5.3 User / UserProfile

| Field                           | Type                     | Notes                |
| ------------------------------- | ------------------------ | -------------------- |
| `username`, `email`, `password` | From Django user         |                      |
| `role`                          | admin / librarian / user | Controls permissions |
| `created_at`, `updated_at`      | DateTime                 | —                    |

---

## 6. Authentication & Authorization

**JWT Bearer Tokens** using `djangorestframework-simplejwt`.

* **Login Endpoint:** `/api/login/`
  Body:

  ```json
  { "username": "user", "password": "pass" }
  ```

  Response:

  ```json
  { "access": "<token>", "refresh": "<token>" }
  ```
* All API calls must include:

  ```
  Authorization: Bearer <access_token>
  ```

**Permissions:**

| Role      | Description          |
| --------- | -------------------- |
| Admin     | Full access          |
| Librarian | Manage books/loans   |
| User      | Borrow & return only |

---

## 7. API Endpoints

### 7.1 Books

| Method    | Endpoint           | Description             | Auth            |
| --------- | ------------------ | ----------------------- | --------------- |
| GET       | `/api/books/`      | List books with filters | Authenticated   |
| GET       | `/api/books/{id}/` | Retrieve book details   | Authenticated   |
| POST      | `/api/books/`      | Add new book            | Admin/Librarian |
| PUT/PATCH | `/api/books/{id}/` | Update book             | Admin/Librarian |
| DELETE    | `/api/books/{id}/` | Delete book             | Admin/Librarian |

**Filters:**

* `q` → search title/author
* `available=true` → available books only
* `ordering=title` or `-created_at` → sort results

---

### 7.2 Loans

| Method | Endpoint                   | Description        | Auth            |
| ------ | -------------------------- | ------------------ | --------------- |
| POST   | `/api/loans/checkout/`     | Borrow a book      | Authenticated   |
| POST   | `/api/loans/{id}/return/`  | Return a book      | Owner/Admin     |
| GET    | `/api/loans/?overdue=true` | List overdue loans | Admin/Librarian |

---

### 7.3 Users (optional)

| Method    | Endpoint           | Description    | Auth  |
| --------- | ------------------ | -------------- | ----- |
| GET       | `/api/users/`      | List all users | Admin |
| POST      | `/api/users/`      | Create user    | Admin |
| GET       | `/api/users/{id}/` | Get details    | Admin |
| PUT/PATCH | `/api/users/{id}/` | Update user    | Admin |
| DELETE    | `/api/users/{id}/` | Delete user    | Admin |

---

## 8. Workflow Example

**1. Login**

```bash
POST /api/login/
→ returns JWT tokens
```

**2. List books**

```bash
GET /api/books/
Header: Authorization: Bearer <token>
```

**3. Checkout**

```bash
POST /api/loans/checkout/
Body: {"book_id":1, "days":14}
```

**4. Return**

```bash
POST /api/loans/1/return/
```

---

## 9. Error Responses (Examples)

| Code | Meaning                        |
| ---- | ------------------------------ |
| 400  | Invalid data or rule violation |
| 401  | Missing/Invalid token          |
| 403  | Insufficient permission        |
| 404  | Resource not found             |
| 201  | Created                        |
| 200  | Success                        |
| 204  | Deleted/No content             |

---

## 10. Future Improvements

* Add **email notifications** for overdue books.
* Add **fine system** for late returns.
* Integrate with **external APIs** (e.g. Open Library).
* Add **frontend dashboard** using React.

---


