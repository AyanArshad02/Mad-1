from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask import send_from_directory
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
            # Hardcoded Admin credentials
            if username == "admin" and password == "admin123":
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
    
    customers = Customer.query.all()
    professionals = ServiceProfessional.query.all()
    services = Service.query.all()

    return render_template("admin_dashboard.html", customers=customers, professionals=professionals, services=services)


@app.route('/uploads/<filename>')
def serve_document(filename):
    # documents are stored in an 'uploads' folder within the project
    return send_from_directory('uploads', filename)




@app.route("/admin/approve_professional/<int:professional_id>", methods=["GET", "POST"])
def approve_professional(professional_id):
    if session.get("user_type") != "Admin":
        flash("Please log in as Admin.")
        return redirect(url_for("login"))

    professional = ServiceProfessional.query.get_or_404(professional_id)

    if request.method == "POST":

        professional.is_approved = True
        db.session.commit()

        flash("Service professional approved successfully!")
        return redirect(url_for("admin_dashboard"))

    return render_template("verify_document.html", professional=professional)



@app.route("/admin/block/<int:user_id>")
def block_user(user_id):
    user_type = session.get("user_type")
    
    if user_type == "Admin":
        customer = Customer.query.get(user_id)
        if customer:
            customer.blocked = True
            db.session.commit()
            flash(f"Customer {customer.name} blocked successfully!")
            return redirect(url_for("admin_dashboard"))
        
        professional = ServiceProfessional.query.get(user_id)
        if professional:
            professional.blocked = True
            db.session.commit()
            flash(f"Professional {professional.name} blocked successfully!")
            return redirect(url_for("admin_dashboard"))

    flash("User not found.")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/unblock/<int:user_id>")
def unblock_user(user_id):
    user_type = session.get("user_type")
    
    if user_type == "Admin":
        customer = Customer.query.get(user_id)
        if customer:
            customer.blocked = False
            db.session.commit()
            flash(f"Customer {customer.name} unblocked successfully!")
            return redirect(url_for("admin_dashboard"))
        
        professional = ServiceProfessional.query.get(user_id)
        if professional:
            professional.blocked = False
            db.session.commit()
            flash(f"Professional {professional.name} unblocked successfully!")
            return redirect(url_for("admin_dashboard"))
    
    flash("User not found.")
    return redirect(url_for("admin_dashboard"))






@app.route("/admin/service/create", methods=["GET", "POST"])
def create_service():
    if session.get("user_type") != "Admin":
        flash("Please log in as Admin.")
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name")
        base_price = request.form.get("base_price")
        description = request.form.get("description")
        time_required = request.form.get("time_required")

        if not name or not base_price or not time_required:
            flash("All fields except description are required.")
            return redirect(url_for("create_service"))

        try:
            # Create the new service record
            new_service = Service(
                name=name,
                base_price=float(base_price),
                description=description,
                time_required=time_required
            )

            # Add and commit to the database
            db.session.add(new_service)
            db.session.commit()
            flash("Service created successfully!")
            return redirect(url_for("admin_dashboard"))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}")
            return redirect(url_for("create_service"))

    return render_template("create_service.html")



@app.route("/admin/service/edit/<int:service_id>", methods=["GET", "POST"])
def edit_service(service_id):
    service = Service.query.get(service_id)
    if not service:
        flash("Service not found.")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        service.name = request.form.get("name")
        service.base_price = request.form.get("base_price")
        service.time_required = request.form.get("time_required")

        try:
            db.session.commit()
            flash("Service updated successfully!")
            return redirect(url_for("admin_dashboard"))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}")
            return redirect(url_for("admin_dashboard"))

    return render_template("edit_service.html", service=service)


@app.route("/admin/service/delete/<int:service_id>")
def delete_service(service_id):
    service = Service.query.get(service_id)
    if service:
        db.session.delete(service)
        db.session.commit()
        flash("Service deleted successfully!")
    else:
        flash("Service not found.")
    return redirect(url_for("admin_dashboard"))


@app.route("/customer/dashboard", methods=["GET", "POST"])
def customer_dashboard():
    if session.get("user_type") != "Customer":
        flash("Please log in as Customer.")
        return redirect(url_for("login"))

    customer_id = session["user_id"]
    customer = Customer.query.get(customer_id)

    # Fetching all service requests for the logged-in customer
    service_requests = ServiceRequest.query.filter_by(customer_id=customer.id).all()

    # Fetching all available services
    services = Service.query.all()

    return render_template("customer_dashboard.html", service_requests=service_requests, services=services)


@app.route("/customer/service/create", methods=["GET", "POST"])
def create_service_request():
    if session.get("user_type") != "Customer":
        flash("Please log in as Customer.")
        return redirect(url_for("login"))

    if request.method == "POST":
        service_id = request.form.get("service_id")
        remarks = request.form.get("remarks")
        date_of_request = datetime.now()

        try:
            # Create the new service request
            new_service_request = ServiceRequest(
                service_id=service_id,
                customer_id=session["user_id"],
                date_of_request=date_of_request,
                remarks=remarks
            )

            # Add and commit to the database
            db.session.add(new_service_request)
            db.session.commit()
            flash("Service request created successfully!")
            return redirect(url_for("customer_dashboard"))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}")
            return redirect(url_for("customer_dashboard"))

    return redirect(url_for("customer_dashboard"))

@app.route("/customer/service/edit/<int:request_id>", methods=["GET", "POST"])
def edit_service_request(request_id):
    service_request = ServiceRequest.query.get(request_id)

    if not service_request:
        flash("Service request not found.")
        return redirect(url_for("customer_dashboard"))

    if request.method == "POST":
        service_request.remarks = request.form.get("remarks")
        service_request.date_of_request = request.form.get("date_of_request")  # Update the date if necessary
        service_request.service_status = request.form.get("service_status")  # Edit the service status

        try:
            db.session.commit()
            flash("Service request updated successfully!")
            return redirect(url_for("customer_dashboard"))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}")
            return redirect(url_for("customer_dashboard"))

    return render_template("edit_service_request.html", service_request=service_request)

@app.route("/customer/service/close/<int:request_id>")
def close_service_request(request_id):
    service_request = ServiceRequest.query.get(request_id)

    if not service_request:
        flash("Service request not found.")
        return redirect(url_for("customer_dashboard"))

    # Set the service request status to closed and add the completion date
    service_request.service_status = "closed"
    service_request.date_of_completion = datetime.now()

    try:
        db.session.commit()
        flash("Service request closed successfully!")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}")

    return redirect(url_for("customer_dashboard"))



@app.route("/professional/dashboard")
def professional_dashboard():
    if session.get("user_type") != "Professional":
        flash("Please log in as Professional.")
        return redirect(url_for("login"))
    
    service_requests = ServiceRequest.query.all()
    return render_template('professional_dashboard.html', service_requests=service_requests)


@app.route('/update_request/<int:request_id>/<string:action>', methods=['POST'])
def update_request(request_id, action):
    request = ServiceRequest.query.get_or_404(request_id)
    
    if action == 'accept':
        request.service_status = 'accepted'
    elif action == 'reject':
        request.service_status = 'rejected'
    elif action == 'close':
        request.service_status = 'completed'
        request.date_of_completion = datetime.utcnow()  # Set completion date
    
    db.session.commit()
    flash(f'Service request {action} successfully!', 'success')
    return redirect(url_for('professional_dashboard'))


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.debug = True
    app.run(debug=True)



