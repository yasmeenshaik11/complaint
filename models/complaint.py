from datetime import datetime
from extensions import db

class Complaint(db.Model):
    __tablename__ = 'complaints'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False, index=True)
    priority = db.Column(db.Enum('HIGH','MEDIUM','LOW'), nullable=False, index=True)
    ai_confidence = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(500))
    image_path = db.Column(db.String(500))
    status = db.Column(db.Enum('PENDING','ASSIGNED','IN PROGRESS','RESOLVED','REJECTED'), default='PENDING', nullable=False, index=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    ai_signals = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    user = db.relationship('User', foreign_keys=[user_id], back_populates='complaints')
    assignee = db.relationship('User', foreign_keys=[assigned_to], back_populates='assigned_complaints')
    updates = db.relationship('ComplaintUpdate', back_populates='complaint', cascade='all, delete-orphan', order_by='ComplaintUpdate.created_at')
    def to_dict(self):
        return {'id':self.id,'user_id':self.user_id,'description':self.description,'category':self.category,'priority':self.priority,'ai_confidence':round(self.ai_confidence,4),'latitude':self.latitude,'longitude':self.longitude,'address':self.address,'image_path':self.image_path,'status':self.status,'assigned_to':self.assigned_to,'assigned_to_name':self.assignee.name if self.assignee else None,'created_at':self.created_at.isoformat(),'updated_at':self.updated_at.isoformat(),'ai_signals':self.ai_signals or []}
