# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()

# # Admin model
# class Admin(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     username = db.Column(db.String(50), unique=True, nullable=False)
#     password = db.Column(db.String(50), nullable=False)


# # Customer model
# class Customer(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     password = db.Column(db.String(50), nullable=False)
#     address = db.Column(db.Text, nullable=False)
#     pincode = db.Column(db.String(6), nullable=False)  # Pin code
#     blocked = db.Column(db.Boolean, default=False)
    
#     # Relationship with ServiceRequest
#     service_requests = db.relationship("ServiceRequest", backref="customer", lazy=True)


# # ServiceProfessional model
# class ServiceProfessional(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(120), nullable=False)
#     name = db.Column(db.String(120), nullable=False)
#     service_name = db.Column(db.String(120), nullable=False)
#     experience = db.Column(db.Integer, nullable=False)
#     document_path = db.Column(db.String(200), nullable=False)  # Path to uploaded document
#     address = db.Column(db.Text, nullable=False)
#     pincode = db.Column(db.String(6), nullable=False)
#     blocked = db.Column(db.Boolean, default=False)  # Blocked flag
#     is_approved = db.Column(db.Boolean, default=False, nullable=False)  # Approval status
    
#     # Relationship with ServiceRequest
#     service_requests = db.relationship("ServiceRequest", backref="professional", lazy=True)


# # Service model
# class Service(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(100), unique=True, nullable=False)
#     base_price = db.Column(db.Float, nullable=False)
#     description = db.Column(db.Text, nullable=True)
#     time_required = db.Column(db.String(50), nullable=True)
    
#     # Relationship with ServiceRequest
#     service_requests = db.relationship('ServiceRequest', backref='service', lazy=True)


# class ServiceRequest(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
#     customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
#     professional_id = db.Column(db.Integer, db.ForeignKey("service_professional.id"), nullable=True)
#     date_of_request = db.Column(db.DateTime, nullable=False)
#     date_of_completion = db.Column(db.DateTime, nullable=True)
#     service_status = db.Column(db.String(50), default="requested", nullable=False)  # requested/assigned/closed
#     remarks = db.Column(db.Text, nullable=True)

#     # Define relationships with backrefs that don't conflict with existing columns
#     customer = db.relationship('Customer', backref=db.backref('service_requests', lazy=True))
#     service = db.relationship('Service', backref=db.backref('service_requests', lazy=True))
#     professional = db.relationship('ServiceProfessional', backref=db.backref('service_requests', lazy=True))






from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(6), nullable=False)
    blocked = db.Column(db.Boolean, default=False)
    service_requests = db.relationship("ServiceRequest", backref="customer", lazy=True)


class ServiceProfessional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    service_name = db.Column(db.String(120), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    document_path = db.Column(db.String(200), nullable=False)  # Store the path of the uploaded document
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(6), nullable=False)
    blocked = db.Column(db.Boolean, default=False)  # Add this line
    is_approved = db.Column(db.Boolean, default=False, nullable=False)  # Add this line for approval status
    service_requests = db.relationship("ServiceRequest", backref="professional", lazy=True)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    time_required = db.Column(db.String(50), nullable=True)
    service_requests = db.relationship('ServiceRequest', backref='service', lazy=True)



class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey("service_professional.id"), nullable=True)
    date_of_request = db.Column(db.DateTime, nullable=False)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    service_status = db.Column(db.String(50), default="requested", nullable=False)  # requested/assigned/closed
    remarks = db.Column(db.Text, nullable=True)

    # customer = db.relationship('Customer', backref=db.backref('service_requests', lazy=True))
    # service = db.relationship('Service', backref=db.backref('service_requests', lazy=True))