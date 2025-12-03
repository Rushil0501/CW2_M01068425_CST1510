# Multi-Domain Intelligence Platform (CST1510)

A modular, secure web application designed for managing cyber incidents, IT tickets, and dataset metadata. Built for CST1510 coursework using **Python, Streamlit, SQLite, and a clean service-layer architecture**.

## 🛠️ Tech Stack

- **Frontend:** Streamlit, Plotly (Interactive Dashboards)
- **Backend:** Python 3.x
- **Database:** SQLite3
- **Security:** Bcrypt (Password Hashing & Salting)
- **Data Processing:** Pandas

---

## 📅 Weekly Progress & Features

### **Week 7: Secure Authentication System**

Implemented the core security layer using file-based storage before the database migration:

- **Password Security:** Uses `bcrypt` for hashing and salting passwords to ensure no plaintext storage.
- **User Management:** Registration and Login logic with duplicate username prevention.
- **Advanced Security Features (Challenges Completed):**
  - **Account Lockout:** Temporarily locks account after 3 failed attempts.
  - **Password Strength Checker:** Enforces complexity (Length, Case, Digits).
  - **Role-Based Access:** Support for 'admin', 'analyst', and 'user' roles.
  - **Session Tokens:** Generates secure hex tokens upon login.

### **Week 8: Database Architecture & Data Pipeline**

Transitioned from text files to a professional SQL database:

- **SQLite Integration:** Replaced `users.txt` with a relational database (`intelligence_platform.db`).
- **Data Migration:** Automated script (`migrate_users_from_file`) to move legacy users to the database without losing data.
- **CSV Ingestion:** Automated loading of `cyber_incidents.csv`, `it_tickets.csv`, and `datasets_metadata.csv` using Pandas.
- **CRUD Operations:** Full Create, Read, Update, Delete functionality for all domains (Incidents, Tickets, Datasets).

### **Week 9: Interactive Web Interface (Streamlit)**

The project now features a fully functional web frontend:

- **Multi-Page App Structure:**
  - **`Home.py`**: Secure Login and Registration tabs.
  - **`pages`**: Main intelligence dashboards protected by session state.
- **Visualisations:** Interactive bar charts and pie charts using **Plotly** to analyse incident types and severity.
- **Session Management:** Secure state handling to keep users logged in across pages.
- **Live Reporting:** Users can submit new incidents via a form, which updates the database in real-time.

---

## 📂 Project Structure (Week 9)

This project is organised to keep everything clean, logical, and easy to maintain.

At the top level, you’ve got the main Streamlit files: Home.py, which handles the login page, and main.py, which you run once to set up the database.

The pages folder holds extra Streamlit screens like the Dashboard, while the DATA folder stores all the actual information the system uses – including the SQLite database, old user records, and any CSV files.

The real engine of the application lives inside the app directory: the data subfolder manages database connections and SQL queries, while the services subfolder contains the business logic, such as user authentication and password handling.

Altogether, the structure makes the system easy to understand, extend, and debug, with every part of the project having a clear purpose.
