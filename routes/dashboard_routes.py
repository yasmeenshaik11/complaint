from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from extensions import db
from models.user import User
from models.complaint import Complaint

dashboard_bp=Blueprint('dashboard',__name__)
def auth_user(): return db.session.get(User,int(get_jwt_identity()))
@dashboard_bp.get('/dashboard')
@jwt_required()
def dashboard():
    u=auth_user(); q=Complaint.query if u.role in ('AUTHORITY','ADMIN') else Complaint.query.filter_by(user_id=u.id)
    total=q.count(); pending=q.filter_by(status='PENDING').count(); progress=q.filter_by(status='IN PROGRESS').count(); resolved=q.filter_by(status='RESOLVED').count(); high=q.filter_by(priority='HIGH').count(); med=q.filter_by(priority='MEDIUM').count(); low=q.filter_by(priority='LOW').count()
    recent=q.order_by(Complaint.created_at.desc()).limit(8).all()
    return jsonify(success=True,message='Dashboard data.',data={'stats':{'total':total,'pending':pending,'in_progress':progress,'resolved':resolved,'high':high,'medium':med,'low':low},'recent':[x.to_dict() for x in recent]})

@dashboard_bp.get('/analytics')
@jwt_required()
def analytics():
    u=auth_user()
    if u.role not in ('AUTHORITY','ADMIN'): return jsonify(success=False,message='Unauthorized access.',data={}),403
    cat=db.session.query(Complaint.category,func.count(Complaint.id)).group_by(Complaint.category).all()
    pri=db.session.query(Complaint.priority,func.count(Complaint.id)).group_by(Complaint.priority).all()
    sta=db.session.query(Complaint.status,func.count(Complaint.id)).group_by(Complaint.status).all()
    daily=db.session.query(func.date(Complaint.created_at),func.count(Complaint.id)).group_by(func.date(Complaint.created_at)).order_by(func.date(Complaint.created_at)).all()
    return jsonify(success=True,message='Analytics data.',data={'by_category':dict(cat),'by_priority':dict(pri),'by_status':dict(sta),'over_time':{str(k):v for k,v in daily}})
