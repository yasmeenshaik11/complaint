from datetime import datetime
from extensions import db
class ComplaintUpdate(db.Model):
    __tablename__ = 'complaint_updates'
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id', ondelete='CASCADE'), nullable=False, index=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    old_status = db.Column(db.String(30))
    new_status = db.Column(db.String(30), nullable=False)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    complaint = db.relationship('Complaint', back_populates='updates')
    updater = db.relationship('User', back_populates='updates')
    def to_dict(self): return {'id':self.id,'old_status':self.old_status,'new_status':self.new_status,'note':self.note,'updated_by':self.updated_by,'updated_by_name':self.updater.name if self.updater else None,'created_at':self.created_at.isoformat()}
