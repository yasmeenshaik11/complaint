from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(190), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(30))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('CITIZEN','AUTHORITY','ADMIN'), default='CITIZEN', nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    complaints = db.relationship('Complaint', foreign_keys='Complaint.user_id', back_populates='user')
    assigned_complaints = db.relationship('Complaint', foreign_keys='Complaint.assigned_to', back_populates='assignee')
    updates = db.relationship('ComplaintUpdate', foreign_keys='ComplaintUpdate.updated_by', back_populates='updater')
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)
