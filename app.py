import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dotenv import load_dotenv
from database.db import (
    check_connection, init_db, seed_db,
    execute_query, execute_one, execute_update, run_raw_sql
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "disaster-relief-secret-key-2026")

# Custom template filters
@app.template_filter('format_date')
def format_date_filter(value):
    if not value:
        return "N/A"
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.strftime("%d %b %Y")
    try:
        dt = datetime.datetime.strptime(str(value), "%Y-%m-%d")
        return dt.strftime("%d %b %Y")
    except Exception:
        return str(value)

# Context processor for global stats and DB health
@app.context_processor
def inject_global_data():
    db_ok, db_msg = check_connection()
    return {
        'db_ok': db_ok,
        'db_status_msg': db_msg,
        'current_year': datetime.datetime.now().year,
        'now_date': datetime.date.today().strftime("%Y-%m-%d")
    }

# ----------------------------------------------------
# SYSTEM / DATABASE MANAGEMENT ROUTES
# ----------------------------------------------------

@app.route('/api/db-status')
def api_db_status():
    ok, msg = check_connection()
    return jsonify({'connected': ok, 'message': msg})

@app.route('/system/init-db', methods=['POST', 'GET'])
def system_init_db():
    ok, msg = init_db()
    if ok:
        flash("Database schema initialized successfully!", "success")
    else:
        flash(f"Error initializing schema: {msg}", "danger")
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/system/seed-db', methods=['POST', 'GET'])
def system_seed_db():
    ok, msg = seed_db()
    if ok:
        flash("Database successfully reset and seeded with default project records!", "success")
    else:
        flash(f"Error seeding database: {msg}", "danger")
    return redirect(request.referrer or url_for('dashboard'))


# ----------------------------------------------------
# DASHBOARD ROUTE
# ----------------------------------------------------

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    # Gather counts and statistics
    try:
        disasters_count = execute_one("SELECT COUNT(*) AS count FROM Disaster")['count']
        victims_count = execute_one("SELECT COUNT(*) AS count FROM Victim")['count']
        centers_count = execute_one("SELECT COUNT(*) AS count FROM ReliefCenter")['count']
        resources_count = execute_one("SELECT COUNT(*) AS count FROM Resource")['count']
        volunteers_count = execute_one("SELECT COUNT(*) AS count FROM Volunteer")['count']
        distributions_count = execute_one("SELECT COUNT(*) AS count FROM Distribution")['count']

        total_distributed_items = execute_one(
            "SELECT COALESCE(SUM(Quantity_Distributed), 0) AS total FROM Distribution"
        )['total']

        total_stock = execute_one(
            "SELECT COALESCE(SUM(Quantity), 0) AS total FROM Resource"
        )['total']

        # Disasters breakdown
        disasters_by_type = execute_query(
            "SELECT Type, COUNT(*) AS count FROM Disaster GROUP BY Type"
        )

        # Disasters by severity
        disasters_by_severity = execute_query(
            "SELECT Severity_Level, COUNT(*) AS count FROM Disaster GROUP BY Severity_Level"
        )

        # Resources inventory summary
        resource_inventory = execute_query(
            """SELECT R.Resource_ID, R.Resource_Name, R.Type, R.Quantity, 
                      C.Name AS Center_Name
               FROM Resource R
               LEFT JOIN ReliefCenter C ON R.Center_ID = C.Center_ID
               ORDER BY R.Quantity ASC LIMIT 6"""
        )

        # Volunteers by skill
        volunteers_by_skill = execute_query(
            "SELECT Skill, COUNT(*) AS count FROM Volunteer GROUP BY Skill"
        )

        # Recent distributions
        recent_distributions = execute_query(
            """SELECT Dist.Distribution_ID, V.Name AS Victim_Name, R.Resource_Name, 
                      Dist.Quantity_Distributed, Dist.Date
               FROM Distribution Dist
               JOIN Victim V ON Dist.Victim_ID = V.Victim_ID
               JOIN Resource R ON Dist.Resource_ID = R.Resource_ID
               ORDER BY Dist.Date DESC, Dist.Distribution_ID DESC LIMIT 5"""
        )

        # Recent disasters
        recent_disasters = execute_query(
            "SELECT * FROM Disaster ORDER BY Date DESC, Disaster_ID DESC LIMIT 4"
        )

        stats = {
            'disasters': disasters_count,
            'victims': victims_count,
            'centers': centers_count,
            'resources': resources_count,
            'volunteers': volunteers_count,
            'distributions': distributions_count,
            'total_distributed': total_distributed_items,
            'total_stock': total_stock
        }

        # Also pass victims and resources for quick distribution modal
        all_victims = execute_query("SELECT Victim_ID, Name FROM Victim ORDER BY Name")
        all_resources = execute_query("SELECT Resource_ID, Resource_Name, Quantity FROM Resource WHERE Quantity > 0 ORDER BY Resource_Name")

        return render_template(
            'dashboard.html',
            stats=stats,
            disasters_by_type=disasters_by_type,
            disasters_by_severity=disasters_by_severity,
            resource_inventory=resource_inventory,
            volunteers_by_skill=volunteers_by_skill,
            recent_distributions=recent_distributions,
            recent_disasters=recent_disasters,
            all_victims=all_victims,
            all_resources=all_resources
        )
    except Exception as e:
        flash(f"Database error while loading dashboard: {e}. Please ensure MySQL is running and initialized.", "warning")
        return render_template('dashboard.html', stats={}, error=str(e),
                               disasters_by_type=[], disasters_by_severity=[],
                               resource_inventory=[], volunteers_by_skill=[],
                               recent_distributions=[], recent_disasters=[],
                               all_victims=[], all_resources=[])


# ----------------------------------------------------
# 1. DISASTER MODULE (CRUD)
# ----------------------------------------------------

@app.route('/disasters')
def disasters_list():
    type_filter = request.args.get('type', '')
    severity_filter = request.args.get('severity', '')
    search = request.args.get('search', '')

    query = "SELECT * FROM Disaster WHERE 1=1"
    params = []

    if type_filter:
        query += " AND Type = %s"
        params.append(type_filter)
    if severity_filter:
        query += " AND Severity_Level = %s"
        params.append(severity_filter)
    if search:
        query += " AND (Location LIKE %s OR Type LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY Disaster_ID ASC"

    try:
        disasters = execute_query(query, params)
        disaster_types = execute_query("SELECT DISTINCT Type FROM Disaster ORDER BY Type")
        severities = ['Critical', 'High', 'Moderate', 'Low']
        return render_template('disasters.html', disasters=disasters, types=disaster_types,
                               severities=severities, selected_type=type_filter,
                               selected_severity=severity_filter, search=search)
    except Exception as e:
        flash(f"Error loading disasters: {e}", "danger")
        return render_template('disasters.html', disasters=[], types=[], severities=[])

@app.route('/disasters/add', methods=['POST'])
def disaster_add():
    try:
        raw_id = request.form.get('Disaster_ID')
        disaster_id = int(raw_id) if raw_id and raw_id.strip() else None
        dtype = request.form.get('Type', '').strip()
        location = request.form.get('Location', '').strip()
        date = request.form.get('Date') or None
        severity = request.form.get('Severity_Level', '').strip()

        if not dtype:
            flash("Disaster Type is required.", "warning")
            return redirect(url_for('disasters_list'))

        if disaster_id:
            existing = execute_one("SELECT Disaster_ID FROM Disaster WHERE Disaster_ID = %s", (disaster_id,))
            if existing:
                flash(f"Disaster ID {disaster_id} already exists. Please choose a unique ID.", "warning")
                return redirect(url_for('disasters_list'))
            execute_update(
                "INSERT INTO Disaster (Disaster_ID, Type, Location, Date, Severity_Level) VALUES (%s, %s, %s, %s, %s)",
                (disaster_id, dtype, location, date, severity)
            )
            flash(f"Disaster '{dtype}' (ID: {disaster_id}) added successfully!", "success")
        else:
            execute_update(
                "INSERT INTO Disaster (Type, Location, Date, Severity_Level) VALUES (%s, %s, %s, %s)",
                (dtype, location, date, severity)
            )
            flash(f"Disaster '{dtype}' recorded successfully!", "success")
    except Exception as e:
        flash(f"Error adding disaster: {e}", "danger")
    return redirect(url_for('disasters_list'))

@app.route('/disasters/edit/<int:disaster_id>', methods=['POST'])
def disaster_edit(disaster_id):
    try:
        dtype = request.form.get('Type', '').strip()
        location = request.form.get('Location', '').strip()
        date = request.form.get('Date') or None
        severity = request.form.get('Severity_Level', '').strip()

        execute_update(
            "UPDATE Disaster SET Type = %s, Location = %s, Date = %s, Severity_Level = %s WHERE Disaster_ID = %s",
            (dtype, location, date, severity, disaster_id)
        )
        flash(f"Disaster ID {disaster_id} updated successfully.", "success")
    except Exception as e:
        flash(f"Error updating disaster: {e}", "danger")
    return redirect(url_for('disasters_list'))

@app.route('/disasters/delete/<int:disaster_id>', methods=['POST', 'GET'])
def disaster_delete(disaster_id):
    try:
        execute_update("DELETE FROM Disaster WHERE Disaster_ID = %s", (disaster_id,))
        flash(f"Disaster ID {disaster_id} deleted successfully.", "info")
    except Exception as e:
        flash(f"Error deleting disaster: {e}", "danger")
    return redirect(url_for('disasters_list'))


# ----------------------------------------------------
# 2. VICTIM MODULE (CRUD)
# ----------------------------------------------------

@app.route('/victims')
def victims_list():
    disaster_filter = request.args.get('disaster_id', '')
    search = request.args.get('search', '')

    query = """
        SELECT V.Victim_ID, V.Name, V.Age, V.Contact, V.Address, V.Disaster_ID,
               D.Type AS Disaster_Type, D.Location AS Disaster_Location
        FROM Victim V
        LEFT JOIN Disaster D ON V.Disaster_ID = D.Disaster_ID
        WHERE 1=1
    """
    params = []

    if disaster_filter:
        query += " AND V.Disaster_ID = %s"
        params.append(disaster_filter)
    if search:
        query += " AND (V.Name LIKE %s OR V.Contact LIKE %s OR V.Address LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY V.Victim_ID ASC"

    try:
        victims = execute_query(query, params)
        disasters = execute_query("SELECT Disaster_ID, Type, Location FROM Disaster ORDER BY Disaster_ID")
        return render_template('victims.html', victims=victims, disasters=disasters,
                               selected_disaster=disaster_filter, search=search)
    except Exception as e:
        flash(f"Error loading victims: {e}", "danger")
        return render_template('victims.html', victims=[], disasters=[])

@app.route('/victims/add', methods=['POST'])
def victim_add():
    try:
        raw_id = request.form.get('Victim_ID')
        victim_id = int(raw_id) if raw_id and raw_id.strip() else None
        name = request.form.get('Name', '').strip()
        age = int(request.form.get('Age')) if request.form.get('Age') else None
        contact = request.form.get('Contact', '').strip()
        address = request.form.get('Address', '').strip()
        disaster_id = int(request.form.get('Disaster_ID')) if request.form.get('Disaster_ID') else None

        if not name:
            flash("Victim Name is required.", "warning")
            return redirect(url_for('victims_list'))

        if victim_id:
            existing = execute_one("SELECT Victim_ID FROM Victim WHERE Victim_ID = %s", (victim_id,))
            if existing:
                flash(f"Victim ID {victim_id} already exists. Please choose a unique ID.", "warning")
                return redirect(url_for('victims_list'))
            execute_update(
                "INSERT INTO Victim (Victim_ID, Name, Age, Contact, Address, Disaster_ID) VALUES (%s, %s, %s, %s, %s, %s)",
                (victim_id, name, age, contact, address, disaster_id)
            )
            flash(f"Victim '{name}' (ID: {victim_id}) registered successfully.", "success")
        else:
            execute_update(
                "INSERT INTO Victim (Name, Age, Contact, Address, Disaster_ID) VALUES (%s, %s, %s, %s, %s)",
                (name, age, contact, address, disaster_id)
            )
            flash(f"Victim '{name}' registered successfully.", "success")
    except Exception as e:
        flash(f"Error adding victim: {e}", "danger")
    return redirect(url_for('victims_list'))

@app.route('/victims/edit/<int:victim_id>', methods=['POST'])
def victim_edit(victim_id):
    try:
        name = request.form.get('Name', '').strip()
        age = int(request.form.get('Age')) if request.form.get('Age') else None
        contact = request.form.get('Contact', '').strip()
        address = request.form.get('Address', '').strip()
        disaster_id = int(request.form.get('Disaster_ID')) if request.form.get('Disaster_ID') else None

        execute_update(
            "UPDATE Victim SET Name = %s, Age = %s, Contact = %s, Address = %s, Disaster_ID = %s WHERE Victim_ID = %s",
            (name, age, contact, address, disaster_id, victim_id)
        )
        flash(f"Victim ID {victim_id} details updated.", "success")
    except Exception as e:
        flash(f"Error updating victim: {e}", "danger")
    return redirect(url_for('victims_list'))

@app.route('/victims/delete/<int:victim_id>', methods=['POST', 'GET'])
def victim_delete(victim_id):
    try:
        execute_update("DELETE FROM Victim WHERE Victim_ID = %s", (victim_id,))
        flash(f"Victim ID {victim_id} deleted successfully.", "info")
    except Exception as e:
        flash(f"Error deleting victim: {e}", "danger")
    return redirect(url_for('victims_list'))


# ----------------------------------------------------
# 3. RELIEF CENTER MODULE (CRUD)
# ----------------------------------------------------

@app.route('/relief-centers')
def relief_centers_list():
    search = request.args.get('search', '')
    query = """
        SELECT C.Center_ID, C.Name, C.Location, C.Capacity, C.Contact,
               COUNT(DISTINCT R.Resource_ID) AS Resource_Count,
               COALESCE(SUM(R.Quantity), 0) AS Total_Stock,
               COUNT(DISTINCT V.Volunteer_ID) AS Volunteer_Count
        FROM ReliefCenter C
        LEFT JOIN Resource R ON C.Center_ID = R.Center_ID
        LEFT JOIN Volunteer V ON C.Center_ID = V.Center_ID
        WHERE 1=1
    """
    params = []
    if search:
        query += " AND (C.Name LIKE %s OR C.Location LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " GROUP BY C.Center_ID, C.Name, C.Location, C.Capacity, C.Contact ORDER BY C.Center_ID ASC"

    try:
        centers = execute_query(query, params)
        return render_template('relief_centers.html', centers=centers, search=search)
    except Exception as e:
        flash(f"Error loading relief centers: {e}", "danger")
        return render_template('relief_centers.html', centers=[])

@app.route('/relief-centers/add', methods=['POST'])
def relief_center_add():
    try:
        raw_id = request.form.get('Center_ID')
        center_id = int(raw_id) if raw_id and raw_id.strip() else None
        name = request.form.get('Name', '').strip()
        location = request.form.get('Location', '').strip()
        capacity = int(request.form.get('Capacity')) if request.form.get('Capacity') else None
        contact = request.form.get('Contact', '').strip()

        if not name:
            flash("Center Name is required.", "warning")
            return redirect(url_for('relief_centers_list'))

        if center_id:
            existing = execute_one("SELECT Center_ID FROM ReliefCenter WHERE Center_ID = %s", (center_id,))
            if existing:
                flash(f"Center ID {center_id} already exists. Please choose a unique ID.", "warning")
                return redirect(url_for('relief_centers_list'))
            execute_update(
                "INSERT INTO ReliefCenter (Center_ID, Name, Location, Capacity, Contact) VALUES (%s, %s, %s, %s, %s)",
                (center_id, name, location, capacity, contact)
            )
            flash(f"Relief Center '{name}' (ID: {center_id}) added successfully.", "success")
        else:
            execute_update(
                "INSERT INTO ReliefCenter (Name, Location, Capacity, Contact) VALUES (%s, %s, %s, %s)",
                (name, location, capacity, contact)
            )
            flash(f"Relief Center '{name}' established successfully.", "success")
    except Exception as e:
        flash(f"Error adding relief center: {e}", "danger")
    return redirect(url_for('relief_centers_list'))

@app.route('/relief-centers/edit/<int:center_id>', methods=['POST'])
def relief_center_edit(center_id):
    try:
        name = request.form.get('Name', '').strip()
        location = request.form.get('Location', '').strip()
        capacity = int(request.form.get('Capacity')) if request.form.get('Capacity') else None
        contact = request.form.get('Contact', '').strip()

        execute_update(
            "UPDATE ReliefCenter SET Name = %s, Location = %s, Capacity = %s, Contact = %s WHERE Center_ID = %s",
            (name, location, capacity, contact, center_id)
        )
        flash(f"Relief Center ID {center_id} updated.", "success")
    except Exception as e:
        flash(f"Error updating relief center: {e}", "danger")
    return redirect(url_for('relief_centers_list'))

@app.route('/relief-centers/delete/<int:center_id>', methods=['POST', 'GET'])
def relief_center_delete(center_id):
    try:
        execute_update("DELETE FROM ReliefCenter WHERE Center_ID = %s", (center_id,))
        flash(f"Relief Center ID {center_id} deleted successfully.", "info")
    except Exception as e:
        flash(f"Error deleting relief center: {e}", "danger")
    return redirect(url_for('relief_centers_list'))


# ----------------------------------------------------
# 4. RESOURCE MODULE (CRUD)
# ----------------------------------------------------

@app.route('/resources')
def resources_list():
    type_filter = request.args.get('type', '')
    center_filter = request.args.get('center_id', '')
    search = request.args.get('search', '')

    query = """
        SELECT R.Resource_ID, R.Resource_Name, R.Type, R.Quantity, R.Center_ID,
               C.Name AS Center_Name, C.Location AS Center_Location
        FROM Resource R
        LEFT JOIN ReliefCenter C ON R.Center_ID = C.Center_ID
        WHERE 1=1
    """
    params = []

    if type_filter:
        query += " AND R.Type = %s"
        params.append(type_filter)
    if center_filter:
        query += " AND R.Center_ID = %s"
        params.append(center_filter)
    if search:
        query += " AND (R.Resource_Name LIKE %s OR R.Type LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY R.Resource_ID ASC"

    try:
        resources = execute_query(query, params)
        resource_types = execute_query("SELECT DISTINCT Type FROM Resource WHERE Type IS NOT NULL ORDER BY Type")
        centers = execute_query("SELECT Center_ID, Name FROM ReliefCenter ORDER BY Center_ID")
        return render_template('resources.html', resources=resources, types=resource_types,
                               centers=centers, selected_type=type_filter,
                               selected_center=center_filter, search=search)
    except Exception as e:
        flash(f"Error loading resources: {e}", "danger")
        return render_template('resources.html', resources=[], types=[], centers=[])

@app.route('/resources/add', methods=['POST'])
def resource_add():
    try:
        raw_id = request.form.get('Resource_ID')
        resource_id = int(raw_id) if raw_id and raw_id.strip() else None
        resource_name = request.form.get('Resource_Name', '').strip()
        rtype = request.form.get('Type', '').strip()
        quantity = int(request.form.get('Quantity')) if request.form.get('Quantity') else 0
        center_id = int(request.form.get('Center_ID')) if request.form.get('Center_ID') else None

        if not resource_name:
            flash("Resource Name is required.", "warning")
            return redirect(url_for('resources_list'))

        if resource_id:
            existing = execute_one("SELECT Resource_ID FROM Resource WHERE Resource_ID = %s", (resource_id,))
            if existing:
                flash(f"Resource ID {resource_id} already exists. Please choose a unique ID.", "warning")
                return redirect(url_for('resources_list'))
            execute_update(
                "INSERT INTO Resource (Resource_ID, Resource_Name, Type, Quantity, Center_ID) VALUES (%s, %s, %s, %s, %s)",
                (resource_id, resource_name, rtype, quantity, center_id)
            )
            flash(f"Resource '{resource_name}' (ID: {resource_id}) registered with quantity {quantity}.", "success")
        else:
            execute_update(
                "INSERT INTO Resource (Resource_Name, Type, Quantity, Center_ID) VALUES (%s, %s, %s, %s)",
                (resource_name, rtype, quantity, center_id)
            )
            flash(f"Resource '{resource_name}' registered with quantity {quantity}.", "success")
    except Exception as e:
        flash(f"Error adding resource: {e}", "danger")
    return redirect(url_for('resources_list'))

@app.route('/resources/edit/<int:resource_id>', methods=['POST'])
def resource_edit(resource_id):
    try:
        resource_name = request.form.get('Resource_Name', '').strip()
        rtype = request.form.get('Type', '').strip()
        quantity = int(request.form.get('Quantity'))
        center_id = int(request.form.get('Center_ID')) if request.form.get('Center_ID') else None

        execute_update(
            "UPDATE Resource SET Resource_Name = %s, Type = %s, Quantity = %s, Center_ID = %s WHERE Resource_ID = %s",
            (resource_name, rtype, quantity, center_id, resource_id)
        )
        flash(f"Resource ID {resource_id} updated.", "success")
    except Exception as e:
        flash(f"Error updating resource: {e}", "danger")
    return redirect(url_for('resources_list'))

@app.route('/resources/restock/<int:resource_id>', methods=['POST'])
def resource_restock(resource_id):
    try:
        add_qty = int(request.form.get('Add_Quantity', 0))
        if add_qty <= 0:
            flash("Please enter a positive restock quantity.", "warning")
            return redirect(url_for('resources_list'))

        execute_update(
            "UPDATE Resource SET Quantity = Quantity + %s WHERE Resource_ID = %s",
            (add_qty, resource_id)
        )
        flash(f"Resource ID {resource_id} restocked by +{add_qty} units.", "success")
    except Exception as e:
        flash(f"Error restocking resource: {e}", "danger")
    return redirect(url_for('resources_list'))

@app.route('/resources/delete/<int:resource_id>', methods=['POST', 'GET'])
def resource_delete(resource_id):
    try:
        execute_update("DELETE FROM Resource WHERE Resource_ID = %s", (resource_id,))
        flash(f"Resource ID {resource_id} deleted.", "info")
    except Exception as e:
        flash(f"Error deleting resource: {e}", "danger")
    return redirect(url_for('resources_list'))


# ----------------------------------------------------
# 5. VOLUNTEER MODULE (CRUD)
# ----------------------------------------------------

@app.route('/volunteers')
def volunteers_list():
    skill_filter = request.args.get('skill', '')
    center_filter = request.args.get('center_id', '')
    search = request.args.get('search', '')

    query = """
        SELECT V.Volunteer_ID, V.Name, V.Phone, V.Skill, V.Center_ID,
               C.Name AS Center_Name, C.Location AS Center_Location
        FROM Volunteer V
        LEFT JOIN ReliefCenter C ON V.Center_ID = C.Center_ID
        WHERE 1=1
    """
    params = []

    if skill_filter:
        query += " AND V.Skill LIKE %s"
        params.append(f"%{skill_filter}%")
    if center_filter:
        query += " AND V.Center_ID = %s"
        params.append(center_filter)
    if search:
        query += " AND (V.Name LIKE %s OR V.Phone LIKE %s OR V.Skill LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY V.Volunteer_ID ASC"

    try:
        volunteers = execute_query(query, params)
        centers = execute_query("SELECT Center_ID, Name FROM ReliefCenter ORDER BY Center_ID")
        skills = execute_query("SELECT DISTINCT Skill FROM Volunteer WHERE Skill IS NOT NULL ORDER BY Skill")
        return render_template('volunteers.html', volunteers=volunteers, centers=centers,
                               skills=skills, selected_skill=skill_filter,
                               selected_center=center_filter, search=search)
    except Exception as e:
        flash(f"Error loading volunteers: {e}", "danger")
        return render_template('volunteers.html', volunteers=[], centers=[], skills=[])

@app.route('/volunteers/add', methods=['POST'])
def volunteer_add():
    try:
        raw_id = request.form.get('Volunteer_ID')
        volunteer_id = int(raw_id) if raw_id and raw_id.strip() else None
        name = request.form.get('Name', '').strip()
        phone = request.form.get('Phone', '').strip()
        skill = request.form.get('Skill', '').strip()
        center_id = int(request.form.get('Center_ID')) if request.form.get('Center_ID') else None

        if not name:
            flash("Volunteer Name is required.", "warning")
            return redirect(url_for('volunteers_list'))

        if volunteer_id:
            existing = execute_one("SELECT Volunteer_ID FROM Volunteer WHERE Volunteer_ID = %s", (volunteer_id,))
            if existing:
                flash(f"Volunteer ID {volunteer_id} already exists. Please choose a unique ID.", "warning")
                return redirect(url_for('volunteers_list'))
            execute_update(
                "INSERT INTO Volunteer (Volunteer_ID, Name, Phone, Skill, Center_ID) VALUES (%s, %s, %s, %s, %s)",
                (volunteer_id, name, phone, skill, center_id)
            )
            flash(f"Volunteer '{name}' (ID: {volunteer_id}) enrolled successfully.", "success")
        else:
            execute_update(
                "INSERT INTO Volunteer (Name, Phone, Skill, Center_ID) VALUES (%s, %s, %s, %s)",
                (name, phone, skill, center_id)
            )
            flash(f"Volunteer '{name}' enrolled successfully.", "success")
    except Exception as e:
        flash(f"Error adding volunteer: {e}", "danger")
    return redirect(url_for('volunteers_list'))

@app.route('/volunteers/edit/<int:volunteer_id>', methods=['POST'])
def volunteer_edit(volunteer_id):
    try:
        name = request.form.get('Name', '').strip()
        phone = request.form.get('Phone', '').strip()
        skill = request.form.get('Skill', '').strip()
        center_id = int(request.form.get('Center_ID')) if request.form.get('Center_ID') else None

        execute_update(
            "UPDATE Volunteer SET Name = %s, Phone = %s, Skill = %s, Center_ID = %s WHERE Volunteer_ID = %s",
            (name, phone, skill, center_id, volunteer_id)
        )
        flash(f"Volunteer ID {volunteer_id} updated.", "success")
    except Exception as e:
        flash(f"Error updating volunteer: {e}", "danger")
    return redirect(url_for('volunteers_list'))

@app.route('/volunteers/delete/<int:volunteer_id>', methods=['POST', 'GET'])
def volunteer_delete(volunteer_id):
    try:
        execute_update("DELETE FROM Volunteer WHERE Volunteer_ID = %s", (volunteer_id,))
        flash(f"Volunteer ID {volunteer_id} removed.", "info")
    except Exception as e:
        flash(f"Error deleting volunteer: {e}", "danger")
    return redirect(url_for('volunteers_list'))


# ----------------------------------------------------
# 6. DISTRIBUTION MODULE (CRUD)
# ----------------------------------------------------

@app.route('/distributions')
def distributions_list():
    victim_filter = request.args.get('victim_id', '')
    resource_filter = request.args.get('resource_id', '')
    date_filter = request.args.get('date', '')

    query = """
        SELECT Dist.Distribution_ID, Dist.Victim_ID, Dist.Resource_ID, 
               Dist.Quantity_Distributed, Dist.Date,
               V.Name AS Victim_Name, V.Contact AS Victim_Contact,
               R.Resource_Name, R.Type AS Resource_Type, R.Quantity AS Stock_Remaining
        FROM Distribution Dist
        JOIN Victim V ON Dist.Victim_ID = V.Victim_ID
        JOIN Resource R ON Dist.Resource_ID = R.Resource_ID
        WHERE 1=1
    """
    params = []

    if victim_filter:
        query += " AND Dist.Victim_ID = %s"
        params.append(victim_filter)
    if resource_filter:
        query += " AND Dist.Resource_ID = %s"
        params.append(resource_filter)
    if date_filter:
        query += " AND Dist.Date = %s"
        params.append(date_filter)

    query += " ORDER BY Dist.Date DESC, Dist.Distribution_ID DESC"

    try:
        distributions = execute_query(query, params)
        victims = execute_query("SELECT Victim_ID, Name FROM Victim ORDER BY Name")
        resources = execute_query("SELECT Resource_ID, Resource_Name, Quantity FROM Resource ORDER BY Resource_Name")
        return render_template('distributions.html', distributions=distributions,
                               victims=victims, resources=resources,
                               selected_victim=victim_filter,
                               selected_resource=resource_filter,
                               selected_date=date_filter)
    except Exception as e:
        flash(f"Error loading distributions: {e}", "danger")
        return render_template('distributions.html', distributions=[], victims=[], resources=[])

@app.route('/distributions/add', methods=['POST'])
def distribution_add():
    try:
        raw_id = request.form.get('Distribution_ID')
        dist_id = int(raw_id) if raw_id and raw_id.strip() else None
        victim_id = int(request.form.get('Victim_ID'))
        resource_id = int(request.form.get('Resource_ID'))
        quantity_distributed = int(request.form.get('Quantity_Distributed'))
        date = request.form.get('Date') or datetime.date.today().strftime('%Y-%m-%d')
        auto_deduct = request.form.get('auto_deduct') == '1'

        if not victim_id or not resource_id or quantity_distributed <= 0:
            flash("Victim, Resource and a valid quantity (>0) are required.", "warning")
            return redirect(request.referrer or url_for('distributions_list'))

        if dist_id:
            existing = execute_one("SELECT Distribution_ID FROM Distribution WHERE Distribution_ID = %s", (dist_id,))
            if existing:
                flash(f"Distribution ID {dist_id} already exists. Please choose a unique ID.", "warning")
                return redirect(request.referrer or url_for('distributions_list'))

        # Check stock availability
        res = execute_one("SELECT Resource_Name, Quantity FROM Resource WHERE Resource_ID = %s", (resource_id,))
        if not res:
            flash(f"Resource ID {resource_id} not found.", "danger")
            return redirect(request.referrer or url_for('distributions_list'))

        if auto_deduct and res['Quantity'] < quantity_distributed:
            flash(f"Insufficient stock! '{res['Resource_Name']}' has only {res['Quantity']} units available (requested {quantity_distributed}).", "danger")
            return redirect(request.referrer or url_for('distributions_list'))

        # Record distribution
        if dist_id:
            execute_update(
                "INSERT INTO Distribution (Distribution_ID, Victim_ID, Resource_ID, Quantity_Distributed, Date) VALUES (%s, %s, %s, %s, %s)",
                (dist_id, victim_id, resource_id, quantity_distributed, date)
            )
        else:
            execute_update(
                "INSERT INTO Distribution (Victim_ID, Resource_ID, Quantity_Distributed, Date) VALUES (%s, %s, %s, %s)",
                (victim_id, resource_id, quantity_distributed, date)
            )

        # Optionally deduct from resource inventory
        if auto_deduct:
            execute_update(
                "UPDATE Resource SET Quantity = Quantity - %s WHERE Resource_ID = %s",
                (quantity_distributed, resource_id)
            )

        flash(f"Distribution recorded: {quantity_distributed} units of '{res['Resource_Name']}' distributed.", "success")
    except Exception as e:
        flash(f"Error creating distribution: {e}", "danger")
    return redirect(request.referrer or url_for('distributions_list'))

@app.route('/distributions/edit/<int:dist_id>', methods=['POST'])
def distribution_edit(dist_id):
    try:
        victim_id = int(request.form.get('Victim_ID'))
        resource_id = int(request.form.get('Resource_ID'))
        quantity_distributed = int(request.form.get('Quantity_Distributed'))
        date = request.form.get('Date') or datetime.date.today().strftime('%Y-%m-%d')

        execute_update(
            "UPDATE Distribution SET Victim_ID = %s, Resource_ID = %s, Quantity_Distributed = %s, Date = %s WHERE Distribution_ID = %s",
            (victim_id, resource_id, quantity_distributed, date, dist_id)
        )
        flash(f"Distribution ID {dist_id} updated.", "success")
    except Exception as e:
        flash(f"Error updating distribution: {e}", "danger")
    return redirect(url_for('distributions_list'))

@app.route('/distributions/delete/<int:dist_id>', methods=['POST', 'GET'])
def distribution_delete(dist_id):
    try:
        execute_update("DELETE FROM Distribution WHERE Distribution_ID = %s", (dist_id,))
        flash(f"Distribution ID {dist_id} deleted.", "info")
    except Exception as e:
        flash(f"Error deleting distribution: {e}", "danger")
    return redirect(url_for('distributions_list'))


# ----------------------------------------------------
# 7. REPORTS & SQL RUNNER (Academic Q1 - Q20)
# ----------------------------------------------------

SAMPLE_QUERIES = [
    {
        "id": "Q1",
        "title": "Display All Disasters",
        "desc": "Retrieves all registered disaster events with their date and severity.",
        "sql": "SELECT * FROM Disaster;"
    },
    {
        "id": "Q2",
        "title": "Display All Victims",
        "desc": "Retrieves all affected persons/victims registered in the system.",
        "sql": "SELECT * FROM Victim;"
    },
    {
        "id": "Q3",
        "title": "Display All Resources",
        "desc": "Lists all relief supplies and inventory amounts across relief centers.",
        "sql": "SELECT * FROM Resource;"
    },
    {
        "id": "Q4",
        "title": "Display All Volunteers",
        "desc": "Lists all volunteers, their contact details, and specialized skills.",
        "sql": "SELECT * FROM Volunteer;"
    },
    {
        "id": "Q5",
        "title": "Display All Relief Centres",
        "desc": "Retrieves all established relief centers, capacity, and location details.",
        "sql": "SELECT * FROM ReliefCenter;"
    },
    {
        "id": "Q6",
        "title": "Resources with Quantity > 0",
        "desc": "Filters resources that currently have positive available inventory.",
        "sql": "SELECT Resource_Name, Type, Quantity FROM Resource WHERE Quantity > 0;"
    },
    {
        "id": "Q7",
        "title": "Victims Sorted Alphabetically",
        "desc": "Sorts victim list by Name in ascending order for quick lookup.",
        "sql": "SELECT * FROM Victim ORDER BY Name;"
    },
    {
        "id": "Q8",
        "title": "Victims Linked to Disaster (ID = 1)",
        "desc": "Demonstrates INNER JOIN between Victim and Disaster tables.",
        "sql": "SELECT V.Victim_ID, V.Name, V.Age, V.Contact, D.Type, D.Location FROM Victim V JOIN Disaster D ON V.Disaster_ID = D.Disaster_ID WHERE D.Disaster_ID = 1;"
    },
    {
        "id": "Q9",
        "title": "Resources with Relief Centre Info",
        "desc": "Demonstrates INNER JOIN between Resource and ReliefCenter tables.",
        "sql": "SELECT R.Resource_Name, R.Type, R.Quantity, C.Name AS Centre_Name FROM Resource R JOIN ReliefCenter C ON R.Center_ID = C.Center_ID;"
    },
    {
        "id": "Q10",
        "title": "Volunteers Assigned to Relief Centres",
        "desc": "Demonstrates INNER JOIN between Volunteer and ReliefCenter tables.",
        "sql": "SELECT V.Name, V.Phone, V.Skill, C.Name AS Centre_Name FROM Volunteer V JOIN ReliefCenter C ON V.Center_ID = C.Center_ID;"
    },
    {
        "id": "Q11",
        "title": "Distribution Details with Victim & Resource",
        "desc": "Multi-table INNER JOIN across Distribution, Victim, and Resource.",
        "sql": "SELECT Dist.Distribution_ID, V.Name AS Victim_Name, R.Resource_Name, Dist.Quantity_Distributed, Dist.Date FROM Distribution Dist JOIN Victim V ON Dist.Victim_ID = V.Victim_ID JOIN Resource R ON Dist.Resource_ID = R.Resource_ID;"
    },
    {
        "id": "Q12",
        "title": "Victim Count per Disaster Type (Aggregation)",
        "desc": "Demonstrates LEFT JOIN and GROUP BY with aggregate COUNT.",
        "sql": "SELECT D.Type, COUNT(V.Victim_ID) AS Victim_Count FROM Disaster D LEFT JOIN Victim V ON D.Disaster_ID = V.Disaster_ID GROUP BY D.Type;"
    },
    {
        "id": "Q13",
        "title": "Total Quantity Distributed per Resource (SUM)",
        "desc": "Demonstrates SUM() aggregation grouped by resource name.",
        "sql": "SELECT R.Resource_Name, SUM(Dist.Quantity_Distributed) AS Total_Distributed FROM Distribution Dist JOIN Resource R ON Dist.Resource_ID = R.Resource_ID GROUP BY R.Resource_Name;"
    },
    {
        "id": "Q14",
        "title": "Disasters of Type 'Cyclone'",
        "desc": "Exact string pattern match for cyclone emergencies.",
        "sql": "SELECT * FROM Disaster WHERE Type = 'Cyclone';"
    },
    {
        "id": "Q15",
        "title": "Resources of Type 'Food'",
        "desc": "Filters all food provisions across all hubs.",
        "sql": "SELECT * FROM Resource WHERE Type = 'Food';"
    },
    {
        "id": "Q16",
        "title": "Volunteers with Medical Skill (LIKE)",
        "desc": "Pattern matching with SQL LIKE '%Medical%' on Volunteer skills.",
        "sql": "SELECT * FROM Volunteer WHERE Skill LIKE '%Medical%';"
    },
    {
        "id": "Q17",
        "title": "Victims Whose Names Start with 'R' (LIKE)",
        "desc": "Pattern matching with SQL LIKE 'R%' on victim names.",
        "sql": "SELECT * FROM Victim WHERE Name LIKE 'R%';"
    },
    {
        "id": "Q18",
        "title": "Relief Centres with Capacity > 100",
        "desc": "Filters major relief centers capable of housing large populations.",
        "sql": "SELECT * FROM ReliefCenter WHERE Capacity > 100;"
    },
    {
        "id": "Q19",
        "title": "Update Resource Stock (DML)",
        "desc": "Increases stock quantity of Resource 201 by 200 units.",
        "sql": "UPDATE Resource SET Quantity = Quantity + 200 WHERE Resource_ID = 201;"
    },
    {
        "id": "Q20",
        "title": "Delete Distribution Record (DML)",
        "desc": "Removes a specific distribution transaction record.",
        "sql": "DELETE FROM Distribution WHERE Distribution_ID = 702;"
    }
]

@app.route('/reports', methods=['GET', 'POST'])
def reports():
    query_result = None
    executed_sql = ""
    error = None

    if request.method == 'POST':
        executed_sql = request.form.get('sql_query', '').strip()
        if executed_sql:
            ok, res = run_raw_sql(executed_sql)
            if ok:
                query_result = res
            else:
                error = res
        else:
            flash("Please enter an SQL query to execute.", "warning")

    return render_template(
        'reports.html',
        sample_queries=SAMPLE_QUERIES,
        query_result=query_result,
        executed_sql=executed_sql,
        error=error
    )

@app.route('/api/run-sql', methods=['POST'])
def api_run_sql():
    data = request.get_json() or {}
    sql_code = data.get('sql', '').strip()
    if not sql_code:
        return jsonify({'success': False, 'error': 'No SQL statement provided.'}), 400

    ok, result = run_raw_sql(sql_code)
    if ok:
        # Convert any non-serializable objects (like datetime) to string
        for res_block in result:
            if 'rows' in res_block:
                for row in res_block['rows']:
                    for k, v in row.items():
                        if isinstance(v, (datetime.date, datetime.datetime)):
                            row[k] = v.strftime("%Y-%m-%d")
        return jsonify({'success': True, 'results': result})
    else:
        return jsonify({'success': False, 'error': result}), 400


# ----------------------------------------------------
# 8. RELATIONAL ER DIAGRAM & SCHEMA VIEW
# ----------------------------------------------------

@app.route('/er-diagram')
def er_diagram():
    return render_template('er_diagram.html')


# ----------------------------------------------------
# APP STARTUP
# ----------------------------------------------------

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    print(f"[*] Disaster Relief Resource Management System is starting on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=debug)
