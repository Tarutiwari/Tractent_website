from dotenv import load_dotenv
import os
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from jinja2 import BaseLoader, TemplateNotFound
from werkzeug.utils import secure_filename
from database import (
    init_db, get_db,
    create_user, get_user_by_email,
    create_tractor, get_tractor_by_id, set_tractor_availability, tractor_to_dict,
    create_booking, get_bookings_by_user, get_booking_by_id,
    update_booking_status, get_pending_bookings_for_owner, booking_to_dict,
    create_or_update_profile, profile_to_dict,
    pwd_context
)
from datetime import datetime
import time

from flask_cors import CORS

load_dotenv()

# Resolve BASE_DIR first — must be before any path construction
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, '..', 'frontend', 'static')

app = Flask(__name__,
            static_folder='../frontend/static',
            template_folder='../frontend/templates')
CORS(app)

# ---- Custom Jinja2 loader: lets templates use {% extends "../index.html" %}
# which resolves to frontend/index.html (parent of templates/)
class ParentAwareLoader(BaseLoader):
    def __init__(self, templates_path, parent_path):
        self.templates_path = os.path.abspath(templates_path)
        self.parent_path = os.path.abspath(parent_path)

    def get_source(self, environment, template):
        if template.startswith('../'):
            path = os.path.join(self.parent_path, template[3:])
        else:
            path = os.path.join(self.templates_path, template)
        path = os.path.normpath(path)
        if not os.path.exists(path):
            raise TemplateNotFound(template)
        mtime = os.path.getmtime(path)
        with open(path, encoding='utf-8') as f:
            source = f.read()
        return source, path, lambda: mtime == os.path.getmtime(path)

    def list_templates(self):
        return [f for f in os.listdir(self.templates_path) if not f.startswith('.')]

_templates_dir = os.path.join(BASE_DIR, '..', 'frontend', 'templates')
_frontend_dir  = os.path.join(BASE_DIR, '..', 'frontend')
app.jinja_loader = ParentAwareLoader(_templates_dir, _frontend_dir)
app.secret_key = os.environ.get("SECRET_KEY")

# Configure upload folder (BASE_DIR and STATIC_DIR already defined above)
app.config['UPLOAD_FOLDER'] = os.path.join(STATIC_DIR, 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

init_db()

# -------- Page Routes --------

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/agrisuggestion")
def agrisuggestion():
    return render_template("agrisuggestion.html")

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")

@app.route("/tractorview", methods=["GET"])
def tractor_view():
    return render_template("tractorview.html")

@app.route('/add-tractor', methods=['GET'])
def add_tractor():
    if 'user_email' not in session:
        flash("Please login first to add a tractor.")
        return redirect(url_for('login'))
    return render_template('add.html')

@app.route('/book/<tractor_id>', methods=['GET'])
def book_tractor(tractor_id):
    if 'user_email' not in session:
        flash("Please login first.")
        return redirect(url_for('login'))
    tractor = get_tractor_by_id(tractor_id)
    if not tractor:
        flash("Tractor not found.")
        return redirect(url_for('tractor_view'))
    tractor_dict = tractor_to_dict(tractor)
    return render_template("book_tractor.html", tractor=tractor_dict, tractor_id=tractor_id)

@app.route('/history')
def history_bhai():
    if 'user_email' not in session:
        flash("Please login first.")
        return redirect(url_for('login'))
    return render_template('history.html')

@app.route("/edit_profile", methods=["GET"])
def edit_profile_page():
    if "user_email" not in session:
        return redirect(url_for("login"))
    return render_template("profile.html")

@app.route('/profile', methods=['GET'])
def profile_page():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html')

# -------- API Routes --------

@app.route("/api/auth/status", methods=["GET"])
def api_auth_status():
    if "user_email" in session:
        return jsonify({
            "logged_in": True,
            "user": {
                "email": session["user_email"],
                "username": session.get("username", "User")
            }
        })
    return jsonify({"logged_in": False})

# --- Contact ---
@app.route("/api/contact", methods=["POST"])
def api_contact():
    data = request.get_json() or request.form
    name = data.get("name")
    email = data.get("email")
    subject = data.get("subject")
    message = data.get("message")

    if not all([name, email, subject, message]):
        return jsonify({"success": False, "message": "All fields are required."}), 400

    print(f"Contact form: {name} ({email}) - {subject}: {message}")
    return jsonify({"success": True, "message": "Message received. We'll get back to you soon!"})

# --- Auth ---
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or request.form
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    user = get_user_by_email(email)
    if user and pwd_context.verify(password, user["password"]):
        session["user_email"] = user["email"]
        session["username"] = user["username"]
        return jsonify({
            "success": True,
            "message": "Login successful.",
            "user": {"email": user["email"], "username": user["username"]}
        })

    return jsonify({"success": False, "message": "Invalid email or password."}), 401

@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})

@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json() or request.form
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"success": False, "message": "All fields are required."}), 400

    if get_user_by_email(email):
        return jsonify({"success": False, "message": "Email is already registered."}), 409

    user = create_user(username, email, password)
    if user:
        return jsonify({"success": True, "message": "Account created successfully."})
    return jsonify({"success": False, "message": "An error occurred. Please try again."}), 500

# --- Tractors ---
@app.route("/api/tractors", methods=["GET"])
def api_get_tractors():
    db = get_db()
    query = {"available": {"$ne": False}}

    location = request.args.get('location')
    model = request.args.get('model')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    if model:
        query["tractor_model"] = {"$regex": model, "$options": "i"}
    if min_price or max_price:
        query["price"] = {}
        if min_price:
            query["price"]["$gte"] = float(min_price)
        if max_price:
            query["price"]["$lte"] = float(max_price)

    tractors = list(db.tractors.find(query))
    return jsonify({"success": True, "tractors": [tractor_to_dict(t) for t in tractors]})

@app.route('/api/tractors', methods=['POST'])
def api_add_tractor():
    if 'user_email' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    tractor_name = request.form.get('name')
    tractor_model = request.form.get('model')
    location = request.form.get('location')
    price = request.form.get('price')

    photo_file = request.files.get('image')
    photo_filename = None

    if photo_file and photo_file.filename != '':
        filename = secure_filename(photo_file.filename)
        photo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        photo_filename = filename

    if not tractor_name or not tractor_model or not location or not price:
        return jsonify({"success": False, "message": "Required fields are missing."}), 400

    combined_model = f"{tractor_name} ({tractor_model})"
    tractor = create_tractor(
        email=session['user_email'],
        tractor_model=combined_model,
        location=location,
        price=float(price),
        photo=photo_filename
    )
    return jsonify({"success": True, "message": "Tractor added successfully.", "tractor": tractor})

# --- Bookings ---
@app.route('/api/bookings', methods=['POST'])
def api_book_tractor():
    if 'user_email' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json() or request.form
    tractor_id = data.get('tractor_id')
    delivery_location = data.get('delivery_location')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')

    if not tractor_id or not delivery_location or not start_date_str or not end_date_str:
        return jsonify({"success": False, "message": "All fields are required."}), 400

    tractor = get_tractor_by_id(tractor_id)
    if not tractor:
        return jsonify({"success": False, "message": "Tractor not found."}), 404

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except Exception:
        return jsonify({"success": False, "message": "Invalid date format."}), 400

    if start_date > end_date:
        return jsonify({"success": False, "message": "End date must be after start date."}), 400

    if not tractor.get("available"):
        return jsonify({"success": False, "message": "Tractor already booked or unavailable."}), 400

    create_booking(
        tractor_id=tractor_id,
        email=session['user_email'],
        delivery_location=delivery_location,
        start_date=start_date,
        end_date=end_date
    )
    # Mark tractor unavailable while pending
    set_tractor_availability(tractor_id, False)

    return jsonify({"success": True, "message": "Booking request sent successfully."})

@app.route('/api/owner/requests', methods=['GET'])
def api_owner_requests():
    if 'user_email' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    db = get_db()
    owner_email = session['user_email']
    pending = get_pending_bookings_for_owner(owner_email)

    requests_data = []
    for booking in pending:
        tractor = get_tractor_by_id(booking["tractor_id"])
        booker = get_user_by_email(booking["email"])
        profile = db.user_profiles.find_one({"email": booking["email"]})

        requests_data.append({
            "booking_id": str(booking["_id"]),
            "tractor_id": booking["tractor_id"],
            "tractor_model": tractor["tractor_model"] if tractor else "Unknown",
            "start_date": booking["start_date"],
            "end_date": booking["end_date"],
            "delivery_location": booking["delivery_location"],
            "booker_username": booker["username"] if booker else "Unknown",
            "booker_address": profile["address"] if profile else "Not provided"
        })

    return jsonify({"success": True, "requests": requests_data})

@app.route('/api/owner/respond/<booking_id>', methods=['POST'])
def api_owner_respond(booking_id):
    if 'user_email' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json() or request.form
    action = data.get('action')  # 'approve' or 'reject'

    if action not in ['approve', 'reject']:
        return jsonify({"success": False, "message": "Invalid action."}), 400

    booking = get_booking_by_id(booking_id)
    if not booking:
        return jsonify({"success": False, "message": "Booking not found."}), 404

    tractor = get_tractor_by_id(booking["tractor_id"])
    if not tractor or tractor["email"] != session['user_email']:
        return jsonify({"success": False, "message": "Unauthorized to respond to this booking."}), 403

    if action == 'approve':
        if booking.get("status") != 'Pending':
            return jsonify({"success": False, "message": "Can only approve pending requests."}), 400
        update_booking_status(booking_id, 'Booked')
        set_tractor_availability(booking["tractor_id"], False)
        message = "Booking approved successfully."
    else:
        update_booking_status(booking_id, 'Rejected')
        set_tractor_availability(booking["tractor_id"], True)
        message = "Booking rejected."

    return jsonify({"success": True, "message": message})

@app.route('/api/history', methods=['GET'])
def api_get_history():
    if 'user_email' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    bookings = get_bookings_by_user(session['user_email'])
    history = []
    for b in bookings:
        tractor = get_tractor_by_id(b["tractor_id"])
        history.append(booking_to_dict(b, tractor=tractor_to_dict(tractor)))
    return jsonify({"success": True, "history": history})

# --- Profile ---
@app.route("/api/profile", methods=["GET", "POST"])
def api_profile():
    if "user_email" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    email = session["user_email"]

    if request.method == "GET":
        user = get_user_by_email(email)
        if not user:
            return jsonify({"success": False, "message": "Profile not found"}), 404

        db = get_db()
        prof = db.user_profiles.find_one({"email": email})
        user_data = {"email": user["email"], "username": user["username"]}
        user_data["profile"] = profile_to_dict(prof)
        return jsonify({"success": True, "user": user_data})

    # POST
    data = request.get_json() or request.form
    address = data.get("address")
    contact = data.get("contact")

    profile = create_or_update_profile(email=email, address=address, contact=contact)
    return jsonify({"success": True, "message": "Profile updated", "profile": profile_to_dict(profile)})

@app.route("/api/upload_profile_photo", methods=["POST"])
def api_upload_profile_photo():
    if "user_email" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    file = request.files.get("photo")
    if file and file.filename != "":
        filename = secure_filename(file.filename)
        filename = f"{session['user_email']}_{int(time.time())}_{filename}"

        upload_folder = os.path.join(STATIC_DIR, 'profile_photos')
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))

        profile = create_or_update_profile(email=session["user_email"], photo=filename)
        return jsonify({"success": True, "message": "Photo uploaded", "photo": filename})

    return jsonify({"success": False, "message": "No photo provided"}), 400

if __name__ == "__main__":
    # use_reloader=False prevents OSError 10038 (Windows socket bug with watchdog)
    # app.run(debug=True, use_reloader=False)
    app.run(host="0.0.0.0" , port = int(os.environ.get("PORT" , 10000)), debug = False)
