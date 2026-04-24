from flask import Flask, render_template, request, redirect, session, flash
import random, string
import smtplib
from email.mime.text import MIMEText
import datetime
import io, base64
import matplotlib.pyplot as plt
import os
import psycopg2

# Try ML model
try:
    from algorithms import lstm_prediction
except:
    lstm_prediction = None

app = Flask(__name__)
app.secret_key = "123456"

otp_store = {}

# ======================
# DATABASE CONNECTION (NEW)
# ======================
def get_db_connection():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        return conn
    except Exception as e:
        print("DB ERROR:", e)
        return None

# ======================
# BILL CALCULATION
# ======================
def calculate_bill(units):
    cost = 0

    if units > 500:
        cost += (units - 500) * 11
        units = 500
    if units > 300:
        cost += (units - 300) * 9
        units = 300
    if units > 200:
        cost += (units - 200) * 7.40
        units = 200
    if units > 100:
        cost += (units - 100) * 6.80
        units = 100
    if units > 50:
        cost += (units - 50) * 4.80
        units = 50
    if units > 0:
        cost += units * 3.35

    return round(cost, 2)

# ======================
# OTP EMAIL
# ======================
def send_otp_email(to_email, otp, name):

    sender_email = os.getenv("EMAIL_USER")
    app_password = os.getenv("EMAIL_PASS")

    if not sender_email or not app_password:
        print(f"OTP for {to_email}: {otp}")
        return

    body = f"""
Hi {name},

Your EnergyPrediction verification code is: {otp}

This OTP is valid for 2 minutes.

⚡ AI Energy Consumption System
"""

    msg = MIMEText(body)
    msg["Subject"] = "EnergyPrediction OTP Verification"
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print("✅ OTP SENT")
    except Exception as e:
        print("EMAIL ERROR:", e)

# ======================
# ROUTES
# ======================
@app.route("/")
def index():
    return render_template("index.html")

# ======================
# LOGIN
# ======================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        gender = request.form.get("gender")
        email = request.form.get("email")

        if not name or not gender or not email:
            flash("All fields required")
            return redirect("/login")

        session["name"] = name
        session["gender"] = gender
        session["email"] = email

        otp = "".join(random.choices(string.digits, k=6))
        otp_store[email] = otp

        send_otp_email(email, otp, name)

        return redirect("/verify_otp")

    return render_template("login.html")

# ======================
# VERIFY OTP
# ======================
@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        entered = request.form.get("otp")
        email = session.get("email")

        if otp_store.get(email) == entered:
            session["logged_in"] = True
            otp_store.pop(email)
            return redirect("/home")

        flash("Invalid OTP")

    return render_template("verify_otp.html")

# ======================
# HOME
# ======================
@app.route("/home")
def home():
    if not session.get("logged_in"):
        return redirect("/login")
    return render_template("home.html")

# ======================
# PREDICTION (UPDATED WITH DB)
# ======================
@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if not session.get('logged_in'):
        return redirect('/login')

    if request.method == 'POST':
        try:
            now = datetime.datetime.now()

            features = [
                float(request.form['temperature']),
                float(request.form['humidity']),
                float(request.form['wind_speed']),
                float(request.form['solar_radiation']),
                now.hour,
                now.weekday(),
                float(request.form['peak_hour_indicator'])
            ]

            try:
                if lstm_prediction:
                    predicted_value = lstm_prediction(features)
                else:
                    raise Exception()
            except:
                predicted_value = sum(features) / len(features)

            cost = calculate_bill(predicted_value)

            # ✅ STORE IN DATABASE
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS energy_predictions (
                        id SERIAL PRIMARY KEY,
                        predicted_value FLOAT
                    )
                """)
                cursor.execute(
                    "INSERT INTO energy_predictions (predicted_value) VALUES (%s)",
                    (predicted_value,)
                )
                conn.commit()
                cursor.close()
                conn.close()

            return render_template(
                'prediction.html',
                prediction_text=f"{predicted_value:.2f}",
                cost=cost
            )

        except Exception as e:
            print("ERROR:", e)
            return render_template('prediction.html', prediction_text="Error")

    return render_template('prediction.html')

# ======================
# GRAPH (UPDATED)
# ======================
@app.route("/graph")
def graph():

    conn = get_db_connection()
    if not conn:
        return render_template("graph.html", graph_url=None)

    cursor = conn.cursor()
    cursor.execute("SELECT predicted_value FROM energy_predictions")
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    if not data:
        return render_template("graph.html", graph_url=None)

    y = [row[0] for row in data]
    x = list(range(1, len(y) + 1))

    plt.figure()
    plt.plot(x, y)

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)

    graph_url = base64.b64encode(img.getvalue()).decode()
    return render_template("graph.html", graph_url=graph_url)

# ======================
# RUN
# ======================
if __name__ == "__main__":
    app.run(debug=True)