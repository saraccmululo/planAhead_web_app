from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from db import init_db
from routes import register_routes
from flask_mail import Mail

# Load environment variables
load_dotenv()

# --- Initialize Flask app ---
app = Flask(__name__, static_folder="dist")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# Detect dev environment
is_dev = os.environ.get("FLASK_ENV") == "development"
app.config["DEV_MODE"] = is_dev

# Enable CORS
if is_dev:
    CORS(app, supports_credentials=True, origins=["http://localhost:5173"])
else:
    CORS(
        app, supports_credentials=True, origins=["https://planahead-daa2.onrender.com"]
    )

# --- Brevo Mail config ---
app.config["MAIL_SERVER"] = "smtp-relay.brevo.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("BREVO_EMAIL")
app.config["MAIL_PASSWORD"] = os.getenv("BREVO_SMTP_KEY")
app.config["MAIL_DEFAULT_SENDER"] = ("PlanAhead", "saramululo@gmail.com")

if not app.config["MAIL_USERNAME"] or not app.config["MAIL_PASSWORD"]:
    raise Exception("Brevo mail credentials are not set!")

# --- Initialize Mail extension ---
mail = Mail(app)

# --- Initialize DB tables ---
init_db()

# Register routes (routes can now import/use `mail`)
register_routes(app, mail)


# Serve React frontend
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path != "" and os.path.exists("dist/" + path):
        return send_from_directory("dist", path)
    else:
        return send_from_directory("dist", "index.html")


# Run app locally
if __name__ == "__main__":
    app.run(debug=(os.environ.get("FLASK_ENV") == "development"))
