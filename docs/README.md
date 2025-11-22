# Multi-Domain Intelligence Platform (CST1510)

A modular, secure web application designed for managing cyber incidents, IT tickets, and dataset metadata. [cite_start]Built for CST1510 coursework using **Python, Streamlit, SQLite, and a clean service-layer architecture**[cite: 7, 8, 136, 387].

## 🛠️ Tech Stack

- **Frontend:** Streamlit, Plotly (Interactive Dashboards) [cite: 387, 391]
- **Backend:** Python 3.x [cite: 7]
- **Database:** SQLite3 [cite: 100]
- **Security:** Bcrypt (Password Hashing & Salting) [cite: 131, 473]
- **Data Processing:** Pandas [cite: 130]

---

## 📅 Weekly Progress & Features

### **Week 7: Secure Authentication System**

Implemented the core security layer using file-based storage before the database migration[cite: 453, 661]:

- **Password Security:** Uses `bcrypt` for hashing and salting passwords to ensure no plaintext storage[cite: 473, 663].
- **User Management:** Registration and Login logic with duplicate username prevention[cite: 663, 664].
- **Advanced Security Features (Challenges Completed):**
  - **Account Lockout:** Temporarily locks account after 3 failed attempts[cite: 713].
  - **Password Strength Checker:** Enforces complexity (Length, Case, Digits)[cite: 691, 701].
  - **Role-Based Access:** Support for 'admin', 'analyst', and 'user' roles[cite: 705, 707].
  - **Session Tokens:** Generates secure hex tokens upon login[cite: 715, 720].

### **Week 8: Database Architecture & Data Pipeline**

Transitioned from text files to a professional SQL database[cite: 100, 376]:

- **SQLite Integration:** Replaced `users.txt` with a relational database (`intelligence_platform.db`)[cite: 102, 384].
- **Data Migration:** Automated script (`migrate_users_from_file`) to move legacy users to the database without losing data[cite: 273].
- **CSV Ingestion:** Automated loading of `cyber_incidents.csv`, `it_tickets.csv`, and `datasets_metadata.csv` using Pandas[cite: 306, 314].
- **CRUD Operations:** Full Create, Read, Update, Delete functionality for all domains (Incidents, Tickets, Datasets)[cite: 105, 317].

### **Week 9: Interactive Web Interface (Streamlit)**

The project now features a fully functional web frontend[cite: 387]:

- **Multi-Page App Structure:**
  - **`Home.py`**: Secure Login and Registration tabs.
  - **`pages/Dashboard.py`**: Main intelligence dashboard protected by session state[cite: 51].
- **Visualisations:** Interactive bar charts and pie charts using **Plotly** to analyse incident types and severity[cite: 391].
- **Session Management:** Secure state handling to keep users logged in across pages[cite: 392].
- **Live Reporting:** Users can submit new incidents via a form, which updates the database in real-time[cite: 390].

---

## 📂 Project Structure (Week 9)

```text
CW2_M01068425_CST1510/
│
├── Home.py                 # Main Entry Point (Web Login Page)
├── main.py                 # Database Setup Script (Run once to initialise DB)
├── requirements.txt        # Project Dependencies
├── README.md               # Documentation
│
├── pages/                  # Streamlit Pages
│   └── Dashboard.py        # Main Dashboard Interface
│
├── DATA/                   # Data Storage
│   ├── intelligence_platform.db  # SQLite Database
│   ├── users.txt           # Legacy Data / Migration Source
│   └── *.csv               # Raw Data Files
│
└── app/                    # Application Logic
    ├── data/               # Database Layer (SQL Queries)
    │   ├── db.py           # Connection Logic
    │   ├── schema.py       # Table Definitions
    │   └── [users.py, incidents.py, tickets.py, datasets.py]
    │
    └── services/           # Business Logic Layer
        └── user_service.py # Auth, Hashing, Validation Rules
```
