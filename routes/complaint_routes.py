from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import case, desc, asc, or_, func
from extensions import db
from models.user import User
from models.complaint import Complaint
from services.complaint_service import create_complaint, update_status
from services.file_service import save_image

complaint_bp=Blueprint('complaints',__name__)
PRIORITY_ORDER=case((Complaint.priority=='HIGH',1),(Complaint.priority=='MEDIUM',2),(Complaint.priority=='LOW',3),else_=4)

def user(): return db.session.get(User,int(get_jwt_identity()))
def guard_authority(): return user().role in ('AUTHORITY','ADMIN')

def payload():
    if request.form: return request.form
    return request.get_json(silent=True) or {}

@complaint_bp.post('/complaints')
@jwt_required()
def create():
    u=user(); d=payload(); description=(d.get('description') or '').strip()
    if not description: return jsonify(success=False,message='Complaint description is required.',data={}),400
    try:
        image_path=save_image(request.files.get('image'),current_app.config['UPLOAD_FOLDER']) if request.files.get('image') else None
        lat=float(d['latitude']) if d.get('latitude') else None; lng=float(d['longitude']) if d.get('longitude') else None
        c=create_complaint(u.id,description,lat,lng,d.get('address'),image_path)
        return jsonify(success=True,message='Complaint submitted successfully',data=c.to_dict()),201
    except ValueError as e: return jsonify(success=False,message=str(e),data={}),400
    except Exception: db.session.rollback(); current_app.logger.exception('Complaint creation failed'); return jsonify(success=False,message='Unable to submit complaint.',data={}),500

@complaint_bp.get('/complaints')
@jwt_required()
def list_complaints():
    u=user(); q=Complaint.query
    if u.role=='CITIZEN': q=q.filter_by(user_id=u.id)
    for field in ('priority','category','status'):
        val=request.args.get(field)
        if val: q=q.filter(getattr(Complaint,field)==val)
    search=request.args.get('search','').strip()
    if search:
        q=q.filter(or_(Complaint.description.ilike(f'%{search}%'),Complaint.address.ilike(f'%{search}%'),Complaint.category.ilike(f'%{search}%'),func.cast(Complaint.id,db.String).ilike(f'%{search}%')))
    order=request.args.get('sort','priority')
    if order=='oldest': q=q.order_by(asc(Complaint.created_at))
    elif order=='newest': q=q.order_by(desc(Complaint.created_at))
    elif order=='lowest': q=q.order_by(desc(PRIORITY_ORDER),desc(Complaint.created_at))
    else: q=q.order_by(PRIORITY_ORDER,desc(Complaint.created_at))
    page=max(1,int(request.args.get('page',1))); per=min(100,max(1,int(request.args.get('per_page',50))))
    items=q.paginate(page=page,per_page=per,error_out=False)
    return jsonify(success=True,message='Complaints retrieved.',data={'items':[x.to_dict() for x in items.items],'page':page,'pages':items.pages,'total':items.total})

@complaint_bp.get('/complaints/<int:cid>')
@jwt_required()
def detail(cid):
    u=user(); c=db.session.get(Complaint,cid)
    if not c: return jsonify(success=False,message='Complaint not found.',data={}),404
    if u.role=='CITIZEN' and c.user_id!=u.id: return jsonify(success=False,message='Unauthorized access.',data={}),403
    data=c.to_dict(); data['timeline']=[x.to_dict() for x in c.updates]; return jsonify(success=True,message='Complaint details.',data=data)

@complaint_bp.put('/complaints/<int:cid>')
@jwt_required()
def update(cid):
    u=user(); c=db.session.get(Complaint,cid)
    if not c: return jsonify(success=False,message='Complaint not found.',data={}),404
    if not guard_authority(): return jsonify(success=False,message='Unauthorized access.',data={}),403
    d=request.get_json(silent=True) or {}
    if d.get('priority') in ('HIGH','MEDIUM','LOW'): c.priority=d['priority']
    if d.get('category'): c.category=d['category']
    if d.get('description'): c.description=d['description'].strip()
    db.session.commit(); return jsonify(success=True,message='Complaint updated.',data=c.to_dict())

@complaint_bp.delete('/complaints/<int:cid>')
@jwt_required()
def delete(cid):
    u=user(); c=db.session.get(Complaint,cid)
    if not c: return jsonify(success=False,message='Complaint not found.',data={}),404
    if u.role not in ('ADMIN',) and c.user_id!=u.id: return jsonify(success=False,message='Unauthorized access.',data={}),403
    db.session.delete(c); db.session.commit(); return jsonify(success=True,message='Complaint deleted.',data={})

@complaint_bp.post('/complaints/<int:cid>/status')
@jwt_required()
def status(cid):
    u=user(); c=db.session.get(Complaint,cid)
    if not c or not guard_authority(): return jsonify(success=False,message='Complaint not found or unauthorized.',data={}),404
    d=request.get_json(silent=True) or {}; new=d.get('status'); allowed={'PENDING','ASSIGNED','IN PROGRESS','RESOLVED','REJECTED'}
    if new not in allowed: return jsonify(success=False,message='Invalid status.',data={}),400
    update_status(c,u.id,new,d.get('note')); return jsonify(success=True,message='Status updated successfully.',data=c.to_dict())

@complaint_bp.post('/complaints/<int:cid>/assign')
@jwt_required()
def assign(cid):
    u=user(); c=db.session.get(Complaint,cid)
    if not c or not guard_authority(): return jsonify(success=False,message='Complaint not found or unauthorized.',data={}),404
    d=request.get_json(silent=True) or {}; aid=d.get('assigned_to')
    a=db.session.get(User,int(aid)) if aid else None
    if not a or a.role not in ('AUTHORITY','ADMIN'): return jsonify(success=False,message='Invalid authority.',data={}),400
    c.assigned_to=a.id
    if c.status=='PENDING': update_status(c,u.id,'ASSIGNED','Complaint assigned to authority.')
    else: db.session.commit()
    return jsonify(success=True,message='Complaint assigned successfully.',data=c.to_dict())

@complaint_bp.get('/complaints/priority/high')
@jwt_required()
def high():
    if not guard_authority(): return jsonify(success=False,message='Unauthorized access.',data={}),403
    items=Complaint.query.filter_by(priority='HIGH').order_by(desc(Complaint.created_at)).all(); return jsonify(success=True,message='High-priority complaints.',data=[x.to_dict() for x in items])

@complaint_bp.get('/categories')
def categories(): return jsonify(success=True,message='Categories.',data=['Pothole/Road Damage','Garbage/Waste','Water Leakage','Broken Streetlight','Drainage/Sewage','Other'])
@complaint_bp.get('/statuses')
def statuses(): return jsonify(success=True,message='Statuses.',data=['PENDING','ASSIGNED','IN PROGRESS','RESOLVED','REJECTED'])
