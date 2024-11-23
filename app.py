from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from model.model import db, Admin, Customer, ServiceProfessional, Service, ServiceRequest

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'timeout': 20}  # Increase timeout to 20 seconds
}

# Upload folder setup
UPLOAD_FOLDER = "uploads/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize db
db.init_app(app)

with app.app_context():
    db.create_all()

# Initialize LoginManager
login_manager = LoginManager(app)
login_manager.login_view = "login"


@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user_type = request.form.get("user_type")  # Admin, Customer, Professional

        if user_type == "Admin":
            # Hardcoded Admin credentials (Change this as needed)
            if username == "admin" and password == "admin123":  # Example credentials
                session.clear()
                session["user_id"] = "admin"  # Set a special ID for admin
                session["user_type"] = "Admin"
                return redirect(url_for("admin_dashboard"))
            else:
                flash("Invalid Admin credentials.")
                return redirect(url_for("login"))

        elif user_type == "Customer":
            user = Customer.query.filter_by(email=username).first()
        elif user_type == "Professional":
            user = ServiceProfessional.query.filter_by(email=username).first()
        else:
            flash("Invalid user type selected.")
            return redirect(url_for("login"))

        if user and user.password == password:
            session.clear()
            session["user_id"] = user.id
            session["user_type"] = user_type
            return redirect(url_for(f"{user_type.lower()}_dashboard"))
        else:
            flash("Invalid credentials")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/signup/customer", methods=["GET", "POST"])
def customer_signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")
        address = request.form.get("address")
        pincode = request.form.get("pincode")

        # Check if the email is already registered
        if Customer.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for("customer_signup"))

        try:
            # Create and add the new customer to the database
            new_customer = Customer(
                email=email, 
                password=password, 
                name=name, 
                address=address, 
                pincode=pincode
            )
            db.session.add(new_customer)
            db.session.commit()
            flash("Account created successfully! Please log in.")
            return redirect(url_for("login"))
        except Exception as e:
            db.session.rollback()  # Rollback any changes if there's an error
            flash(f"An error occurred: {str(e)}")
        finally:
            db.session.close()  # Ensure the session is closed

    return render_template("customer_signup.html")


@app.route("/signup/professional", methods=["GET", "POST"])
def professional_signup():
    if request.method == "POST":
        try:
            email = request.form.get("email")
            password = request.form.get("password")
            name = request.form.get("name")
            service_name = request.form.get("service_name")
            experience = request.form.get("experience")
            address = request.form.get("address")
            pincode = request.form.get("pincode")
            document = request.files["document"]

            # Check if the email is already registered
            if ServiceProfessional.query.filter_by(email=email).first():
                flash("Email already registered.")
                return redirect(url_for("professional_signup"))

            # Save the uploaded document
            document_filename = secure_filename(document.filename)
            document_path = os.path.join(app.config["UPLOAD_FOLDER"], document_filename)
            document.save(document_path)

            # Create a new ServiceProfessional instance
            new_professional = ServiceProfessional(
                email=email,
                password=password,
                name=name,
                service_name=service_name,
                experience=experience,
                address=address,
                pincode=pincode,
                document_path=document_path  # Save the path instead of the file
            )

            # Add and commit to the database
            db.session.add(new_professional)
            db.session.commit()
            flash("Account created successfully! Please log in after verification.")
            return redirect(url_for("login"))

        except Exception as e:
            # Handle any unexpected errors
            flash(f"An error occurred: {str(e)}")
            return redirect(url_for("professional_signup"))

        finally:
            # Close the database session to release resources
            db.session.close()

    return render_template("professional_signup.html")

# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    if session.get('user_type') == 'Admin':
        return Admin.query.get(int(user_id))
    elif session.get('user_type') == 'Customer':
        return Customer.query.get(int(user_id))
    elif session.get('user_type') == 'Professional':
        return ServiceProfessional.query.get(int(user_id))
    return None



@app.route("/admin/dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if session.get("user_type") != "Admin":
        flash("Please log in as Admin.")
        return redirect(url_for("login"))
    return render_template("admin_dashboard.html")


@app.route("/customer/dashboard")
def customer_dashboard():
    if session.get("user_type") != "Customer":
        flash("Please log in as Customer.")
        return redirect(url_for("login"))
    return render_template("customer_dashboard.html")

@app.route("/professional/dashboard")
def professional_dashboard():
    if session.get("user_type") != "Professional":
        flash("Please log in as Professional.")
        return redirect(url_for("login"))
    return render_template("professional_dashboard.html")

@app.route("/logout")
def logout():
    session.clear()  # Clear all session data
    flash("Logged out successfully.")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.debug = True
    app.run(debug=True)



