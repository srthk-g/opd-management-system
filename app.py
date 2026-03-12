from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "hospital_secret"


# DATABASE CONNECTION
def get_db():
    conn = sqlite3.connect("hospital.db", timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        user_id = request.form.get("user_id")
        password = request.form.get("password")

        db = get_db()

        user = db.execute(
            "SELECT * FROM users WHERE user_id=? AND password=?",
            (user_id, password)
        ).fetchone()

        if user:

            role = user["role"].lower()

            if role == "patient":
                return redirect("/patient_dashboard")

            elif role == "doctor":
                return redirect("/doctor_dashboard")

            elif role == "inventory":
                return redirect("/inventory_dashboard")

        return "Invalid login"

    return render_template("login.html")


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# PATIENT DASHBOARD
@app.route("/patient_dashboard")
def patient_dashboard():
    return render_template("patient_dashboard.html")


# DOCTOR DASHBOARD
@app.route("/doctor_dashboard")
def doctor_dashboard():

    db = get_db()

    appointments = db.execute(
        "SELECT * FROM appointments"
    ).fetchall()

    return render_template(
        "doctor_dashboard.html",
        appointments=appointments
    )


# INVENTORY DASHBOARD
@app.route("/inventory_dashboard")
def inventory_dashboard():

    db = get_db()

    medicines = db.execute(
        "SELECT * FROM medicines"
    ).fetchall()

    store_items = db.execute(
        "SELECT * FROM store_items"
    ).fetchall()

    return render_template(
        "inventory_dashboard.html",
        medicines=medicines,
        store_items=store_items
    )


# REGISTER PATIENT
@app.route("/register_patient", methods=["GET", "POST"])
def register_patient():

    if request.method == "POST":

        patient_id = request.form["patient_id"]
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        address = request.form["address"]

        db = get_db()

        db.execute(
            "INSERT INTO patients VALUES (?,?,?,?,?,?)",
            (patient_id, name, age, gender, phone, address)
        )

        db.commit()

        return redirect("/patient_dashboard")

    return render_template("register_patient.html")


# BOOK APPOINTMENT (FIXED)
@app.route("/book_appointment", methods=["GET","POST"])
def book_appointment():

    db = get_db()

    doctors = db.execute("SELECT * FROM doctors").fetchall()

    if request.method == "POST":

        patient_id = request.form["patient_id"]
        doctor_id = request.form["doctor_id"]
        appointment_date = request.form["appointment_date"]
        appointment_time = request.form["appointment_time"]


        db.execute(
        "INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status) VALUES (?,?,?,?,?)",
        (patient_id, doctor_id, appointment_date, appointment_time, "Scheduled")
        )

        db.commit()

        return redirect("/patient_dashboard")

    return render_template("appointments.html", doctors=doctors)


# VIEW APPOINTMENTS
@app.route("/appointments")
def appointments():

    db = get_db()

    appointments = db.execute(
        "SELECT * FROM appointments"
    ).fetchall()

    return render_template("view_appointments.html", appointments=appointments)


# ADD VISIT
@app.route("/add_visit", methods=["GET", "POST"])
def add_visit():

    if request.method == "POST":

        patient_id = request.form["patient_id"]
        doctor_id = request.form["doctor_id"]
        date = request.form["date"]
        diagnosis = request.form["diagnosis"]
        treatment = request.form["treatment"]

        db = get_db()

        db.execute(
        "INSERT INTO visits (patient_id, doctor_id, visit_date, diagnosis, treatment) VALUES (?,?,?,?,?)",
        (patient_id, doctor_id, date, diagnosis, treatment)
        )

        db.commit()

        return redirect("/doctor_dashboard")

    return render_template("add_visit.html")


# ADMIT PATIENT
@app.route("/admit_patient", methods=["GET", "POST"])
def admit_patient():

    db = get_db()

    beds = db.execute(
        "SELECT * FROM beds WHERE status='available'"
    ).fetchall()

    if request.method == "POST":

        patient_id = request.form["patient_id"]
        bed_id = request.form["bed_id"]
        date = request.form["date"]

        db.execute(
        "INSERT INTO admissions (patient_id, bed_id, admission_date) VALUES (?,?,?)",
        (patient_id, bed_id, date)
        )
        

        db.execute(
            "UPDATE beds SET status='occupied' WHERE bed_id=?",
            (bed_id,)
        )

        db.commit()

        return redirect("/patient_dashboard")

    return render_template("admit_patient.html", beds=beds)

@app.route("/view_medicines")
def view_medicines():

    db = get_db()

    medicines = db.execute(
        "SELECT * FROM medicines"
    ).fetchall()

    return render_template("view_medicines.html", medicines=medicines)


@app.route("/view_consumables")
def view_consumables():

    db = get_db()

    consumables = db.execute(
        "SELECT * FROM store_items"
    ).fetchall()

    return render_template("view_consumables.html", consumables=consumables)


@app.route("/update_stock", methods=["GET","POST"])
def update_stock():

    if request.method == "POST":

        item_id = request.form["item_id"]
        stock = request.form["stock"]

        db = get_db()

        db.execute(
        "UPDATE store_items SET stock=? WHERE item_id=?",
        (stock, item_id)
        )

        db.commit()

    return render_template("update_stock.html")


# RUN SERVER
if __name__ == "__main__":
    app.run(debug=True)