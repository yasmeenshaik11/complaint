from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from extensions import db
from models.user import User

auth_bp=Blueprint('auth',__name__)
def resp(success=True,message='',data=None,status=200): return jsonify(success=success,message=message,data=data or {}),status

def current_user():
    ident=get_jwt_identity(); return db.session.get(User,int(ident)) if ident else None

@auth_bp.post('/register')
def register():
    d=request.get_json(silent=True) or {}
    name=d.get('name','').strip(); email=d.get('email','').strip().lower(); phone=d.get('phone','').strip(); password=d.get('password','')
    if not name or not email or not password: return resp(False,'Name, email and password are required.',status=400)
    if len(password)<8: return resp(False,'Password must be at least 8 characters.',status=400)
    if db.session.query(User).filter_by(email=email).first(): return resp(False,'Email is already registered.',status=409)
    u=User(name=name,email=email,phone=phone,role='CITIZEN'); u.set_password(password); db.session.add(u); db.session.commit()
    return resp(True,'Registration successful.',{'id':u.id,'name':u.name,'email':u.email,'role':u.role},201)

@auth_bp.post('/login')
def login():
    d=request.get_json(silent=True) or {}; email=d.get('email','').strip().lower(); password=d.get('password','')
    u=db.session.query(User).filter_by(email=email).first()
    if not u or not u.check_password(password): return resp(False,'Invalid login credentials.',status=401)
    token=create_access_token(identity=str(u.id)); return resp(True,'Login successful.',{'access_token':token,'user':{'id':u.id,'name':u.name,'email':u.email,'role':u.role}})

@auth_bp.post('/logout')
@jwt_required()
def logout(): return resp(True,'Logged out. Client should discard its token.')

@auth_bp.get('/me')
@jwt_required()
def me():
    u=current_user(); return resp(True,'Current user.',{'id':u.id,'name':u.name,'email':u.email,'phone':u.phone,'role':u.role}) if u else resp(False,'User not found.',status=404)
