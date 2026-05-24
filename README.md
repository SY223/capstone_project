
# 📘 Course Enrollment API — README

A lightweight FastAPI backend for managing students, courses, and enrollments.  
Built with clean service layers, role‑based access control, and in‑memory storage for simplicity.

---

## 🚀 How to Run the API

### **1. Clone the repository**
```bash
git clone <your-repo-url>
cd <your-project-folder>
```

### **2. Create and activate a virtual environment**
```bash
python3 -m venv env
source env/bin/activate     # macOS / Linux
env\Scripts\activate        # Windows
```

### **3. Install dependencies**
```bash
pip install -r requirements.txt
```

### **4. Start the FastAPI server**
```bash
uvicorn app.main:app --reload
```

### **5. Open the interactive API docs**
FastAPI automatically generates Swagger documentation.

- Swagger UI:  
  👉 `http://127.0.0.1:8000/docs` [(127.0.0.1)](https://www.bing.com/search?q="http%3A%2F%2F127.0.0.1%3A8000%2Fdocs")

- ReDoc:  
  👉 `http://127.0.0.1:8000/redoc` [(127.0.0.1)](https://www.bing.com/search?q="http%3A%2F%2F127.0.0.1%3A8000%2Fredoc")

---

## 🧪 How to Run the Tests

### **1. Ensure your virtual environment is active**
```bash
source env/bin/activate     # macOS / Linux
env\Scripts\activate        # Windows
```

### **2. Run all tests using pytest**
```bash
pytest
```

### **3. Run tests with detailed output**
```bash
pytest -vv
```

### **4. Run a specific test file**
```bash
pytest tests/test_enrollment.py
```

### **5. Run tests with coverage**
If you have `pytest-cov` installed:

```bash
pytest --cov=app
```

---

## 🗂 Project Structure

```
app/
 ├── api/
 │    └── v1/
 │    │   ├── enrollments.py
 │    │   ├── courses.py
 │    │   └── users.py
 │    └── deps.py
 ├── core/
 │    └── db.py
 ├── schemas/
 │    ├── user_schema.py
 │    ├── course_schema.py
 │    └── enrollment_schema.py
 ├── services/
 │    ├── user_services.py
 │    ├── course_services.py
 │    └── enrollment_services.py
 │   
 └── main.py
tests/
 ├── api
 └── unit
```

---

## 🧩 Environment Requirements

- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic v2
- Pytest (for tests)

---

## 💡 Tips for Development

- Use `x-user-id` header to simulate authentication.
- Admin and student roles are enforced via FastAPI dependencies.
- In‑memory DB (`users_db`, `courses_db`, `enrollments_db`) resets on restart.
- All input is sanitised (lowercase, stripped) before saving.
