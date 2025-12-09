# Multi-Domain Intelligence Platform (CST1510)

Name: Kavirajduthsingh Ramdawor
Student ID: M01068425

A modular, secure web application designed for managing cyber incidents, IT tickets, and dataset metadata. Built for CST1510 coursework using **Python, Streamlit, SQLite, and a clean service-layer architecture**.

## Tech Stack

- **Frontend:** Streamlit, Plotly (Interactive Dashboards)
- **Backend:** Python 3.13.x
- **Database:** SQLite3
- **Security:** Bcrypt (Password Hashing & Salting)
- **Data Processing:** Pandas
- **Images:** Pillow (profile avatars)
- **API Integration:** Gemini API (requires `GOOGLE_API_KEY` in `.streamlit/secrets.toml`)
- **Programming Paradigm:** Object-Oriented Programming (OOP)

---

## Weekly Progress & Features

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
  - **`pages`**: Main intelligence dashboards folder (Cybersecuity.py, Data_Science.py, IT_Operations.py) protected by session state.
  - It also contains Login.py, AI_Assitant.py, and profile.py.
- **Visualisations:** Interactive bar charts and pie charts using **Plotly** to analyse incident types and severity.
- **Session Management:** Secure state handling to keep users logged in across pages.
- **Live Reporting:** Users can submit new incidents via a form, which updates the database in real-time.

### **Week 10: Gemini API Integration**

Enhanced the platform with external intelligence capabilities:

- **Gemini API:** Integrated Gemini API to fetch real-time cyber threat intelligence.
- **Automated Alerts:** Users can receive updates on emerging threats directly in the dashboard.
- **API Service Layer:** Encapsulated API calls in a dedicated service module for cleaner code and easier testing.
- **Data Processing:** Parsed and stored Gemini API responses into the database for historical tracking and analysis.

### **Week 11: Object-Oriented Programming Implementation**

Refactored the codebase to leverage OOP principles:

- **Class-Based Services:** Converted user authentication, ticket management, and incident handling into classes.
- **Encapsulation:** Improved code maintainability by restricting direct access to sensitive attributes.
- **Inheritance & Reusability:** Created base classes for shared functionalities across different domain modules.
- **Modular Design:** Enhanced readability and made the platform easier to extend for future features.

---

## Project Structure

This project is organised to keep everything clean, logical, and easy to maintain.

- **Top-Level Files:** `Home.py` (login & registration), `main.py` (database setup)
- **`pages/` Folder:** Additional Streamlit pages like the Dashboards
- **`DATA/` Folder:** Stores SQLite database, legacy user files, CSV datasets, and AI chat history per dashboard.
- **`app/` Folder:**
  - **`data/`**: Database connections & queries
  - **`services/`**: Business logic (authentication, ticket/incident handling, Gemini API service)
  - **OOP Refactor:** Services and modules are now class-based for better structure

Altogether, the structure makes the system easy to understand, extend, and debug, with every part of the project having a clear purpose.

## Setup Notes

- Populate `.streamlit/secrets.toml` with `GOOGLE_API_KEY` to enable Gemini responses; without it, AI calls will warn or return a fallback.
- Initial data load and table creation: run `python main.py` to create the SQLite database, migrate legacy users, and seed CSVs if present. Then start the app with `streamlit run Home.py`.
