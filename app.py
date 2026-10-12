import os
from flask import Flask, render_template, jsonify
from werkzeug.exceptions import RequestEntityTooLarge
from config import Config
from extensions import db, jwt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)

    from routes.auth_routes import auth_bp
    from routes.complaint_routes import complaint_bp
    from routes.admin_routes import admin_bp
    from routes.dashboard_routes import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(complaint_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api')

    @app.get('/')
    def index():
        return render_template('index.html')

    @app.get('/login')
    def login_page():
        return render_template('login.html')

    @app.get('/authority/login')
    def authority_login_page():
        return render_template('authority/login.html')

    @app.get('/register')
    def register_page():
        return render_template('register.html')

    @app.get('/citizen')
    def citizen_page():
        return render_template('citizen/dashboard.html')

    @app.get('/citizen/submit')
    def citizen_submit():
        return render_template('citizen/submit.html')

    @app.get('/citizen/complaints')
    def citizen_complaints():
        return render_template('citizen/complaints.html')

    @app.get('/citizen/complaints/<int:complaint_id>')
    def citizen_detail(complaint_id):
        return render_template('citizen/detail.html', complaint_id=complaint_id)

    @app.get('/authority')
    def authority_page():
        return render_template('authority/dashboard.html')

    @app.get('/authority/complaints')
    def authority_complaints():
        return render_template('authority/complaints.html')

    @app.get('/authority/complaints/<int:complaint_id>')
    def authority_detail(complaint_id):
        return render_template('authority/detail.html', complaint_id=complaint_id)

    @app.get('/authority/analytics')
    def authority_analytics():
        return render_template('authority/analytics.html')

    @app.errorhandler(RequestEntityTooLarge)
    def too_large(_):
        return jsonify(success=False, message='Image/file is too large. Maximum size is 5 MB.'), 413

    @app.errorhandler(404)
    def not_found(_):
        return jsonify(success=False, message='Resource not found.'), 404

    @app.errorhandler(500)
    def server_error(_):
        return jsonify(success=False, message='An internal server error occurred.'), 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', '0') == '1'
    )
