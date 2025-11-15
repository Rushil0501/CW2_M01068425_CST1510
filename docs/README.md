# A modular Python-based system designed for managing cyber incidents, IT tickets, dataset metadata, and user authentication.

Built for CST1510 coursework using **Python, SQLite, and a clean service-layer architecture**.

## Features

### **User Authentication**

- Register / login with secure password hashing
- Automated migration from `users.txt`
- Centralised authentication logic in `user_service.py`

### **Cyber Incident Management**

- Create, read, update, delete incidents
- CSV ingestion of `cyber_incidents.csv`
- Incident fields processed automatically (timestamp, type, severity, status, description)

### **IT Ticket Tracking**

- Loads `it_tickets.csv`
- Stores ticket priority, assigned staff, status, resolution hours, timestamps

### **Dataset Metadata Handling**

- Loads `datasets_metadata.csv`
- Saves dataset info (rows, columns, uploader, upload date)

### **Database Structure**

- SQLite database auto-created on first run
- Tables:
  - `users`
  - `cyber_incidents`
  - `it_tickets`
  - `datasets_metadata`

### **Fully Modular Architecture**
