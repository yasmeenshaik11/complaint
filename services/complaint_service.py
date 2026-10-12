from extensions import db
from models.complaint import Complaint
from models.complaint_update import ComplaintUpdate
from services.ai_service import predict

def create_complaint(user_id, description, latitude=None, longitude=None, address=None, image_path=None):
    ai = predict(description)
    c = Complaint(user_id=user_id,description=description,category=ai['category'],priority=ai['priority'],ai_confidence=ai['confidence'],latitude=latitude,longitude=longitude,address=address,image_path=image_path,status='PENDING',ai_signals=ai['signals'])
    db.session.add(c); db.session.flush()
    db.session.add(ComplaintUpdate(complaint_id=c.id,updated_by=user_id,old_status=None,new_status='PENDING',note='Complaint submitted and AI analysis completed.'))
    db.session.commit(); return c

def update_status(c, actor_id, new_status, note=None):
    old=c.status; c.status=new_status
    db.session.add(ComplaintUpdate(complaint_id=c.id,updated_by=actor_id,old_status=old,new_status=new_status,note=note)); db.session.commit(); return c
