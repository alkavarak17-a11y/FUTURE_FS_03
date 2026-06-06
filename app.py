from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "secret"

# -------------------------------
# MySQL Configuration
# -------------------------------
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'crm'

mysql = MySQL(app)

# -------------------------------
# Login Page
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM admin WHERE username=%s AND password=%s",
            (username, password)
        )

        user = cur.fetchone()
        cur.close()

        if user:
            session['user'] = username
            return redirect("/dashboard")

        return "Invalid Username or Password"

    return render_template("login.html")


# -------------------------------
# Dashboard
# -------------------------------
@app.route("/dashboard")
def dashboard():

    if 'user' not in session:
        return redirect("/")

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM leads")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM leads WHERE status='New'")
    new = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM leads WHERE status='Contacted'")
    contacted = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM leads WHERE status='Converted'")
    converted = cur.fetchone()[0]

    cur.close()

    return render_template(
        "dashboard.html",
        total=total,
        new=new,
        contacted=contacted,
        converted=converted
    )


# -------------------------------
# View Leads
# -------------------------------
@app.route("/leads")
def leads():

    if 'user' not in session:
        return redirect("/")

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM leads ORDER BY created_at DESC")

    leads = cur.fetchall()

    cur.close()

    return render_template(
        "leads.html",
        leads=leads
    )


# -------------------------------
# Add Lead
# -------------------------------
@app.route("/add-lead", methods=["GET", "POST"])
def add_lead():

    if 'user' not in session:
        return redirect("/")

    if request.method == "POST":

        name = request.form['name']
        email = request.form['email']
        source = request.form['source']
        status = request.form['status']

        cur = mysql.connection.cursor()

        cur.execute(
            """
            INSERT INTO leads
            (name,email,source,status)
            VALUES(%s,%s,%s,%s)
            """,
            (name, email, source, status)
        )

        mysql.connection.commit()
        cur.close()

        return redirect("/leads")

    return render_template("add_lead.html")

# -------------------------------
# Update Lead Status
# -------------------------------
@app.route("/update-status/<int:id>", methods=["POST"])
def update_status(id):

    if 'user' not in session:
        return redirect("/")

    status = request.form['status']

    cur = mysql.connection.cursor()

    cur.execute(
        "UPDATE leads SET status=%s WHERE lead_id=%s",
        (status, id)
    )

    mysql.connection.commit()
    cur.close()

    return redirect("/leads")


# -------------------------------
# Delete Lead
# -------------------------------
@app.route("/delete-lead/<int:id>")
def delete_lead(id):

    if 'user' not in session:
        return redirect("/")

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM leads WHERE lead_id=%s",
        (id,)
    )

    mysql.connection.commit()
    cur.close()

    return redirect("/leads")


# -------------------------------
# Logout
# -------------------------------
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# -------------------------------
# Run Application
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)