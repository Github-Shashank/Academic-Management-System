# 📚 Academic Management System (Backend)

A secure and scalable backend system for managing academic resources like lectures, discussions, assignments, and submissions.
Built using **Flask**, with **JWT authentication**, **rate limiting**, and **file upload support**.

---

## 🚀 Features

### 🔐 Authentication & Security

* User Registration & Login
* Password hashing (Werkzeug)
* JWT-based authentication
* Role-based access (student / teacher)
* Secure routes using decorators

---

### 📖 Academic Management

* Subjects management
* Lecture organization (ordered by lecture number)
* Discussion threads & replies
* Assignment creation & submission

---

### 📂 File Handling

* Upload files (PDF, images, etc.)
* Unique filenames using UUID
* Secure file storage
* File serving via API

---

### ⚡ Rate Limiting

* Prevents API abuse
* Per-user/IP request tracking
* Custom decorator-based implementation

---

## 🧠 Tech Stack

* **Backend:** Flask (Python)
* **Database:** SQLite (via SQLAlchemy)
* **Authentication:** JWT (PyJWT)
* **Security:** Werkzeug hashing
* **Other:** UUID, OS, Time-based tracking

---

## 📁 Project Structure

```
backend/
│
├── app.py              # Main Flask application
├── models.py           # Database models
├── uploads/            # Uploaded files
├── instance/           # Database (ignored)
├── .gitignore
└── requirements.txt
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository

```
git clone https://github.com/Github-Shashank/Academic-Management-System.git
cd Academic-Management-System/backend
```

---

### 2️⃣ Create Virtual Environment

```
python -m venv venv
venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

### 4️⃣ Run Server

```
python app.py
```

Server will start at:

```
http://127.0.0.1:5000/
```

---

## 🔑 API Usage

### Register

```
POST /register
```

### Login

```
POST /login
```

Returns JWT token.

---

### Protected Routes

Use header:

```
Authorization: Bearer <token>
```

---

### Example: Submit Assignment

```
POST /submit_assignment
```

---

## ⚡ Rate Limiting

Example:

* Login → max 5 requests/minute
* Submission → max 3 requests/minute

Returns:

```
429 Too Many Requests
```

---

## 🔐 Security Practices

* Passwords are hashed (never stored in plain text)
* JWT ensures authenticated access
* User identity is NOT taken from request body
* File uploads are sanitized
* Rate limiting prevents abuse

---

## 🧪 Testing (cURL Example)

```
curl -X POST http://127.0.0.1:5000/login \
-H "Content-Type: application/json" \
-d "{\"name\":\"Shashank\",\"password\":\"1234\"}"
```

---

## 🚀 Future Improvements

* Refresh tokens (JWT)
* Redis-based rate limiting
* Role-based middleware decorators
* Frontend (React / Web UI)
* Docker deployment

---

## 👨‍💻 Author

**Shashank Singh Patel**
GitHub: https://github.com/Github-Shashank

---

## ⭐ Final Note

This project demonstrates:

* Secure backend design
* Real-world authentication flow
* Middleware & decorators usage
* API protection & scalability concepts

---
