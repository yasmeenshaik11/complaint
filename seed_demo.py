from app import create_app, db
from models.user import User
from models.complaint import Complaint
from services.complaint_service import create_complaint, update_status
app=create_app()
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='citizen.demo@example.com').first():
        c=User(name='Demo Citizen',email='citizen.demo@example.com',phone='9000000001',role='CITIZEN'); c.set_password('Citizen@123'); db.session.add(c)
    if not User.query.filter_by(email='authority.demo@example.com').first():
        a=User(name='Demo Authority',email='authority.demo@example.com',phone='9000000002',role='AUTHORITY'); a.set_password('Authority@123'); db.session.add(a)
    db.session.commit()
    c=User.query.filter_by(email='citizen.demo@example.com').first(); a=User.query.filter_by(email='authority.demo@example.com').first()
    if Complaint.query.count()==0:
        examples=[
        ('Large pothole near school causing accidents','Pothole/Road Damage','HIGH','PENDING'),
        ('Garbage overflowing near residential area','Garbage/Waste','MEDIUM','IN PROGRESS'),
        ('Water pipeline leakage near main road','Water Leakage','HIGH','PENDING'),
        ('Streetlight not working on main road','Broken Streetlight','MEDIUM','RESOLVED'),
        ('Drainage blockage after rainfall','Drainage/Sewage','HIGH','IN PROGRESS'),
        ('Small litter issue in park','Garbage/Waste','LOW','PENDING')]
        for desc,_,__,status in examples:
            item=create_complaint(c.id,desc,address='Gudlavalleru')
            if status != 'PENDING':
                item.assigned_to=a.id
                db.session.commit()
                update_status(item,a.id,status,'Seed/demo status.')
            else:
                db.session.commit()
    print('Demo ready. Citizen: citizen.demo@example.com / Citizen@123; Authority: authority.demo@example.com / Authority@123')
