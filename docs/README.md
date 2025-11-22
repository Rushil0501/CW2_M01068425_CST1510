# Multi-Domain Intelligence Platform (CST1510)

A modular, secure web application designed for managing cyber incidents, IT tickets, and dataset metadata. [cite_start]Built for CST1510 coursework using **Python, Streamlit, SQLite, and a clean service-layer architecture**[cite: 7, 57].

## 🛠️ Tech Stack

- [cite_start]**Frontend:** Streamlit, Plotly (Interactive Dashboards) [cite: 49]
- **Backend:** Python 3.x
- [cite_start]**Database:** SQLite3 [cite: 45]
- [cite_start]**Security:** Bcrypt (Password Hashing & Salting) [cite: 41]
- [cite_start]**Data Processing:** Pandas [cite: 47]

---

## 📅 Weekly Progress & Features

### **Week 9: Interactive Web Interface (Streamlit)**

[cite_start]The project now features a fully functional web frontend:

- **Multi-Page App Structure:**
  - [cite_start]**`Home.py`**: Secure Login and Registration tabs.
  - [cite_start]**`pages/Dashboard.py`**: Main intelligence dashboard protected by session state[cite: 49, 51].
- [cite_start]**Visualisations:** Interactive bar charts and pie charts using **Plotly** to analyse incident types and severity[cite: 49, 51].
- [cite_start]**Session Management:** Secure state handling to keep users logged in across pages.
- [cite_start]**Live Reporting:** Users can submit new incidents via a form, which updates the database in real-time.

### **Week 8: Database Architecture & Data Pipeline**

[cite_start]Transitioned from text files to a professional SQL database[cite: 369]:

- [cite_start]**SQLite Integration:** Replaced `users.txt` with a relational database (`intelligence_platform.db`)[cite: 371].
- [cite_start]**Data Migration:** Automated script (`migrate_users_from_file`) to move legacy users to the database without losing data[cite: 371, 533].
- [cite_start]**CSV Ingestion:** Automated loading of `cyber_incidents.csv`, `it_tickets.csv`, and `datasets_metadata.csv` using Pandas[cite: 47, 573].
- [cite_start]**CRUD Operations:** Full Create, Read, Update, Delete functionality for all domains (Incidents, Tickets, Datasets)[cite: 47, 588].

### **Week 7: Secure Authentication System**

[cite_start]Implemented the core security layer[cite: 40]:

- [cite_start]**Password Security:** Uses `bcrypt` for hashing and salting passwords (never stored in plain text)[cite: 41, 306].
- [cite_start]**User Management:** Registration and Login logic with duplicate username prevention[cite: 43, 306].
- **Advanced Security Features (Challenges Completed):**
  - [cite_start]**Account Lockout:** Temporarily locks account after 3 failed attempts[cite: 355].
  - [cite_start]**Password Strength Checker:** Enforces complexity (Length, Case, Digits)[cite: 334].
  - [cite_start]**Role-Based Access:** Support for 'admin', 'analyst', and 'user' roles[cite: 348].
  - [cite_start]**Session Tokens:** Generates secure hex tokens upon login[cite: 358].

---

## 📂 Project Structure (Week 9)

```text
CW2_YourID_CST1510/
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
