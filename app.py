from flask import Flask, request, render_template, redirect, url_for
import database

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    recent = database.get_recent_appointments()
    return render_template("index.html", recent_appointments=recent, search_results=None)

@app.route("/book", methods=["POST"])
def book():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    service = request.form.get("service")
    visit_time = request.form.get("visit_time")
    phone = request.form.get("phone")

    database.add_appointment(first_name, last_name, service, visit_time, phone)
    return redirect(url_for("index"))

@app.route("/search", methods=["GET"])
def search():
    phone = request.args.get("phone", "")
    results = database.search_by_phone(phone)
    recent = database.get_recent_appointments()
    return render_template("index.html", recent_appointments=recent, search_results=results)

@app.route("/admin", methods=["GET"])
def admin():
    all_appointments = database.get_all_appointments()
    return render_template("admin.html", appointments=all_appointments)

if __name__ == "__main__":
    database.init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)