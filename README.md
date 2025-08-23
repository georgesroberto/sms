# 👗 ThreadLedger — Simple Stock & Sales Management System

ThreadLedger is a lightweight **Stock Management System (SMS)** built with **Django**.  
It’s designed for small vendors and admins to easily manage stock, record sales, and generate quick reports — all in a clean and simple interface.  

---

## 🚀 Features

### 👩‍💼 Admin
- Add and manage stock (`product name`, `buying price`, `quantity`, `reorder level`)
- Monitor stock levels and reorder alerts
- View sales summaries by date and payment method

### 🧑‍💻 Vendor
- View available stock
- Log sales (`product`, `qty`, `selling price`, `payment status`)
- Track personal daily sales history

### 📊 System
- Auto-reduces stock on each sale
- Payment statuses: `Paid & Taken`, `Partial`, `Unpaid & Taken`, `Paid & Untaken`
- Simple daily sales reports
- Separate user roles: **Admin** vs **Vendor**

---

## 🏗️ Tech Stack

- **Backend**: Django (Python 3.10+)
- **Database**: SQLite (local dev), PythonAnywhere DB (production)
- **Frontend**: Django templates + Bootstrap
- **Deployment**: PythonAnywhere

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/georgesroberto/sms.git
cd sms
````

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup environment variables

Create a `.env` file in the project root:

```env
DJANGO_SETTINGS_MODULE=src.settings.dev
SECRET_KEY=your-secret-key
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create superuser

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🗄️ Database Models

**Product**

* name
* buying\_price
* quantity
* reorder\_level

**Sale**

* product (FK)
* vendor (FK to User)
* quantity
* selling\_price
* payment\_status
* date

**User**

* username, password
* role: `ADMIN` / `VENDOR`

---

## 🚦 Deployment (PythonAnywhere)

1. Push your code to GitHub.
2. Log into [PythonAnywhere](https://www.pythonanywhere.com).
3. Create a new web app → Manual configuration → Python 3.10+.
4. Clone repo in PythonAnywhere console.
5. Setup `virtualenv` and install dependencies.
6. Configure **WSGI file** to point to `threadledger.wsgi`.
7. Run `python manage.py migrate` in console.
8. Collect static files:

   ```bash
   python manage.py collectstatic
   ```
9. Reload the web app from PythonAnywhere dashboard.

---

## 👥 Team

* **Georges** — Backend setup, Auth & Deployment
* **Grace** — Admin UI
* **Solomon** — Vendor UI
* **James** — Reports & Polishing

---

## 📝 License

This project is licensed under the MIT License — feel free to use, modify, and share.

---

## ✨ Cute Note

> “ThreadLedger keeps your threads in check 👗📊.
> Less paperwork, more fashion.”

