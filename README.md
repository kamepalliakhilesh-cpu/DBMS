# DISASTER RELIEF RESOURCE MANAGEMENT SYSTEM (DRRMS)

An academic DBMS full-stack web application designed for managing disaster relief operations, victims, relief resources, relief centres, volunteers, and resource distributions with real-time MySQL database integration.

---

## 👥 Project Team (Batch 05)

- **Eeranki Sri Surya Krishna Karthik** — `25B11CS253`
- **Kamepalli Venkata Akhilesh** — `25B11CS381`
- **Chokka Sri Sowmya** — `25B11CS194`
- **Boddu Lakshmi Surya Sahithi** — `25B11CS115`

**Supervisor:** Dr. M.V.B. Murali Krishna

---

## 🗄️ Database Architecture & Relational Schema (3NF)

The database strictly consists of **6 fixed entities** with exact attributes, primary keys, and foreign keys as specified in the project documentation:

```
1. Disaster (Disaster_ID [PK], Type, Location, Date, Severity_Level)
2. Victim (Victim_ID [PK], Name, Age, Contact, Address, Disaster_ID [FK -> Disaster])
3. ReliefCenter (Center_ID [PK], Name, Location, Capacity, Contact)
4. Resource (Resource_ID [PK], Resource_Name, Type, Quantity, Center_ID [FK -> ReliefCenter])
5. Volunteer (Volunteer_ID [PK], Name, Phone, Skill, Center_ID [FK -> ReliefCenter])
6. Distribution (Distribution_ID [PK], Victim_ID [FK -> Victim], Resource_ID [FK -> Resource], Quantity_Distributed, Date)
```

### Referential Integrity Constraints:
- `Victim.Disaster_ID` ➜ `Disaster.Disaster_ID`
- `Resource.Center_ID` ➜ `ReliefCenter.Center_ID`
- `Volunteer.Center_ID` ➜ `ReliefCenter.Center_ID`
- `Distribution.Victim_ID` ➜ `Victim.Victim_ID`
- `Distribution.Resource_ID` ➜ `Resource.Resource_ID`

---

## 🚀 Tech Stack

- **Backend:** Python Flask
- **Database:** MySQL 8.0 (connected via PyMySQL)
- **Frontend:** Modern Semantic HTML5, Vanilla CSS3 (Ultra-crisp dark glassmorphism design system), JavaScript (ES6+), Chart.js
- **Environment:** Windows / VS Code

---

## ⚙️ Quick Setup & Running Locally

### 1. Configure MySQL Database Credentials
Open or edit the `.env` file in the project root:
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=disaster_relief_db
SECRET_KEY=disaster-relief-secret-key-2026
PORT=5000
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize & Seed Database (Automated or Manual)

#### Option A: Automatic Setup from Web Interface
Simply run the application, open the web dashboard at `http://localhost:5000`, and click the **"Re-Seed Data"** button in the top navigation bar.

#### Option B: Manual Setup using MySQL Client
```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

### 4. Run the Flask Web Server
```bash
python app.py
```
or via the Python launcher on Windows:
```powershell
py app.py
```

Open your browser and navigate to:
👉 **`http://localhost:5000`**

---

## 📊 Application Features

1. **Relief Command Dashboard:** Real-time KPI summaries, inventory charts, disaster type distributions, and rapid distribution recording modal.
2. **Disasters Management:** Full CRUD operations, filtering by disaster type and severity levels (`Critical`, `High`, `Moderate`, `Low`).
3. **Victims Directory:** Complete victim records linked to active disasters with contact and shelter location tracking.
4. **Relief Centres Hub:** Capacity indicators, active stockpiles, and volunteer workforce allocations.
5. **Resources Inventory:** Live stock status (`In Stock`, `Low Stock`, `Out of Stock`), center associations, and instant restock actions.
6. **Volunteers Task Force:** Contact directories and skill filters (`Medical Support`, `Rescue & Evacuation`, `Food Distribution`, `Logistics`).
7. **Distribution Ledger:** Real-time inventory tracking, automatic stock deduction, multi-table join visibility.
8. **Interactive SQL Console & Reports:** One-click execution for all 20 standard academic viva queries (`Q1` to `Q20`) + interactive custom SQL query workbench with live tabular output.
9. **Relational ER Diagram Viewer:** Visual entity cards, attribute datatypes, primary keys, and foreign key relationships.

---

## 📝 Academic SQL Query Catalog (Q1 - Q20)

| Query | Title | SQL Implementation |
|---|---|---|
| **Q1** | Display all disasters | `SELECT * FROM Disaster;` |
| **Q2** | Display all victims | `SELECT * FROM Victim;` |
| **Q3** | Display all resources | `SELECT * FROM Resource;` |
| **Q4** | Display all volunteers | `SELECT * FROM Volunteer;` |
| **Q5** | Display all relief centres | `SELECT * FROM ReliefCenter;` |
| **Q6** | Resources with quantity > 0 | `SELECT Resource_Name, Type, Quantity FROM Resource WHERE Quantity > 0;` |
| **Q7** | Victims sorted by name | `SELECT * FROM Victim ORDER BY Name;` |
| **Q8** | Victims linked to disaster 1 | `SELECT V.Victim_ID, V.Name, V.Age, V.Contact, D.Type, D.Location FROM Victim V JOIN Disaster D ON V.Disaster_ID = D.Disaster_ID WHERE D.Disaster_ID = 1;` |
| **Q9** | Resources with relief centre | `SELECT R.Resource_Name, R.Type, R.Quantity, C.Name AS Centre_Name FROM Resource R JOIN ReliefCenter C ON R.Center_ID = C.Center_ID;` |
| **Q10** | Volunteers assigned to centre | `SELECT V.Name, V.Phone, V.Skill, C.Name AS Centre_Name FROM Volunteer V JOIN ReliefCenter C ON V.Center_ID = C.Center_ID;` |
| **Q11** | Multi-table Distribution details | `SELECT Dist.Distribution_ID, V.Name AS Victim_Name, R.Resource_Name, Dist.Quantity_Distributed, Dist.Date FROM Distribution Dist JOIN Victim V ON Dist.Victim_ID = V.Victim_ID JOIN Resource R ON Dist.Resource_ID = R.Resource_ID;` |
| **Q12** | Victim count per disaster | `SELECT D.Type, COUNT(V.Victim_ID) AS Victim_Count FROM Disaster D LEFT JOIN Victim V ON D.Disaster_ID = V.Disaster_ID GROUP BY D.Type;` |
| **Q13** | Total distributed per resource | `SELECT R.Resource_Name, SUM(Dist.Quantity_Distributed) AS Total_Distributed FROM Distribution Dist JOIN Resource R ON Dist.Resource_ID = R.Resource_ID GROUP BY R.Resource_Name;` |
| **Q14** | Disasters of type 'Cyclone' | `SELECT * FROM Disaster WHERE Type = 'Cyclone';` |
| **Q15** | Resources of type 'Food' | `SELECT * FROM Resource WHERE Type = 'Food';` |
| **Q16** | Volunteers with Medical skill | `SELECT * FROM Volunteer WHERE Skill LIKE '%Medical%';` |
| **Q17** | Victims starting with 'R' | `SELECT * FROM Victim WHERE Name LIKE 'R%';` |
| **Q18** | Relief centres capacity > 100 | `SELECT * FROM ReliefCenter WHERE Capacity > 100;` |
| **Q19** | Update resource stock | `UPDATE Resource SET Quantity = Quantity + 200 WHERE Resource_ID = 201;` |
| **Q20** | Delete distribution record | `DELETE FROM Distribution WHERE Distribution_ID = 702;` |

---

## 📁 File Structure

```
dbms/
├── app.py                     # Flask application routes and API logic
├── requirements.txt           # Python package requirements
├── README.md                  # Comprehensive project documentation
├── .env                       # Active MySQL environment configuration
├── .env.example               # Template environment configuration
│
├── database/
│   ├── db.py                  # PyMySQL connection pool and query helpers
│   ├── schema.sql             # Pure MySQL DDL (6 entities + constraints)
│   ├── seed.sql               # Seed records aligned with PPT and report
│   └── queries.sql            # Standard queries Q1 to Q20
│
├── templates/
│   ├── base.html              # Layout master template with sidebar & navbar
│   ├── dashboard.html         # Operations command center with charts
│   ├── disasters.html         # Disaster module CRUD & filtering
│   ├── victims.html           # Victim module CRUD & linking
│   ├── relief_centers.html    # ReliefCenter module CRUD
│   ├── resources.html         # Resource inventory module CRUD
│   ├── volunteers.html        # Volunteer workforce module CRUD
│   ├── distributions.html     # Distribution ledger module CRUD
│   ├── reports.html           # Academic SQL Runner & Q1-Q20 Catalog
│   └── er_diagram.html        # Relational ER architecture visualizer
│
└── static/
    ├── css/
    │   └── style.css          # Ultra-modern dark glassmorphism design system
    └── js/
        └── app.js             # Interactive modal, search, and SQL handlers
```
