from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
admin_bp=Blueprint('admin',__name__)
@admin_bp.get('/authorities')
@jwt_required()
def authorities():
    u=db.session.get(User,int(get_jwt_identity()))
    if not u or u.role not in ('AUTHORITY','ADMIN'): return jsonify(success=False,message='Unauthorized access.',data={}),403
    users=User.query.filter(User.role.in_(['AUTHORITY','ADMIN'])).order_by(User.name).all()
    return jsonify(success=True,message='Authorities.',data=[{'id':x.id,'name':x.name,'email':x.email,'role':x.role} for x in users])
