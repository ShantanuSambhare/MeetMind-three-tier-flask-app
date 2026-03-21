from flask import Flask, render_template, request, jsonify
import mysql.connector
import os
 
app = Flask(__name__)
 
# ── DB CONFIG FROM ENVIRONMENT VARIABLES ──────────────
def get_db():
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "mysql"),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", "root"),
        database=os.environ.get("MYSQL_DB", "devops")
    )
 
# ── CREATE TABLE IF NOT EXISTS ─────────────────────────
def init_db():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                role VARCHAR(100) NOT NULL,
                department VARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meetings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                notes TEXT,
                action_items TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ DB init error: {e}")
 
# ── ROUTES ────────────────────────────────────────────
 
@app.route("/")
def index():
    return render_template("index.html")
 
# ── EMPLOYEE: ADD ─────────────────────────────────────
@app.route("/add_employee", methods=["POST"])
def add_employee():
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employees (name, role, department, email, message) VALUES (%s, %s, %s, %s, %s)",
            (data["name"], data["role"], data["department"], data["email"], data.get("message", ""))
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Employee added successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
 
# ── EMPLOYEE: GET ALL ─────────────────────────────────
@app.route("/get_employees", methods=["GET"])
def get_employees():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employees ORDER BY created_at DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        # Convert datetime to string
        for row in rows:
            if row.get("created_at"):
                row["created_at"] = str(row["created_at"])
        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
 
# ── EMPLOYEE: DELETE ──────────────────────────────────
@app.route("/delete_employee/<int:emp_id>", methods=["DELETE"])
def delete_employee(emp_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id = %s", (emp_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Employee deleted"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
 
# ── MEETING: ADD ──────────────────────────────────────
@app.route("/add_meeting", methods=["POST"])
def add_meeting():
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO meetings (title, notes, action_items) VALUES (%s, %s, %s)",
            (data["title"], data.get("notes", ""), data.get("action_items", ""))
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Meeting saved!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
 
# ── MEETING: GET ALL ──────────────────────────────────
@app.route("/get_meetings", methods=["GET"])
def get_meetings():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM meetings ORDER BY created_at DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        for row in rows:
            if row.get("created_at"):
                row["created_at"] = str(row["created_at"])
        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
 
# ── MAIN ──────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
