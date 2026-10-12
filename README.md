# AI-Based Smart Public Complaint Prioritization System

A production-oriented Flask + MySQL civic complaint platform. Citizens submit public issues with text, image and location; Python NLP/ML classifies the complaint, predicts priority, returns confidence and stores the result in MySQL. Authorities receive a priority queue ordered HIGH → MEDIUM → LOW, with newest complaints first within the same priority.

## Stack
- Python 3.x, Flask REST APIs, Flask-SQLAlchemy, Flask-JWT-Extended
- MySQL + PyMySQL
- scikit-learn, pandas, NumPy, TF-IDF, Logistic Regression, Joblib
- HTML5/CSS3/vanilla JavaScript, Fetch API, Chart.js
- Werkzeug password hashing and Pillow image validation

## Project structure
See the `models/`, `routes/`, `services/`, `ml/`, `templates/`, `static/`, and `database/` directories. `app.py` is the application entry point.

## 1. MySQL setup
```sql
CREATE DATABASE complaint_system;
```
Then:
```bash
mysql -u root -p complaint_system < database/schema.sql
```

## 2. Python environment
Windows:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Environment variables
Copy `.env.example` to `.env` and set a strong `SECRET_KEY`, `JWT_SECRET_KEY`, and the MySQL connection string.

Example:
```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost/complaint_system
SECRET_KEY=replace-with-a-long-random-secret
JWT_SECRET_KEY=replace-with-another-long-random-secret
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=5242880
PORT=5000
```

## 4. Train the baseline model
```bash
python ml/train_model.py
```
This creates `category_model.pkl`, `priority_model.pkl`, `category_vectorizer.pkl`, and `priority_vectorizer.pkl`. The demo corpus is intentionally small and should be replaced with a validated real dataset for deployment.

## 5. Seed demo accounts/data
```bash
python seed_demo.py
```
Demo credentials for local demonstration only:
- Citizen: `citizen.demo@example.com` / `Citizen@123`
- Authority: `authority.demo@example.com` / `Authority@123`

Change these credentials before any real deployment.

## 6. Run
```bash
python app.py
```
Open `http://localhost:5000`.
For deployment, use a WSGI server such as:
```bash
gunicorn app:app
```

## Functional flow
Login → Submit Complaint → Upload Image → Select Location → AI Analysis → HIGH/MEDIUM/LOW → Authority Dashboard → Assign → In Progress → Resolved → Citizen Tracks Resolution.

## REST API
- POST `/api/register`
- POST `/api/login`
- POST `/api/logout`
- GET `/api/me`
- POST `/api/complaints`
- GET `/api/complaints`
- GET `/api/complaints/<id>`
- PUT `/api/complaints/<id>`
- DELETE `/api/complaints/<id>`
- POST `/api/complaints/<id>/status`
- POST `/api/complaints/<id>/assign`
- GET `/api/complaints/priority/high`
- GET `/api/dashboard`
- GET `/api/analytics`
- GET `/api/categories`
- GET `/api/statuses`
- GET `/api/authorities`

## AI behavior
Text is normalized, vectorized with TF-IDF and classified by persisted scikit-learn Logistic Regression models. Priority uses the trained baseline plus an explainable safety-signal layer for terms such as accident, danger, school, hospital, flooding, electrical hazard and blocked road. The UI explicitly labels this as a baseline AI prediction rather than human-level intelligence.

## Security notes
Passwords are hashed. JWT authentication and role checks protect authority APIs. Image uploads are restricted to JPG/JPEG/PNG/WEBP, validated as actual images, renamed with UUIDs and limited to 5 MB. Secrets and database credentials are environment variables. For a public deployment, also put Flask behind HTTPS, use a production secret, rotate demo credentials, configure CORS narrowly, add rate limiting/CSRF strategy appropriate to the authentication architecture, and move uploads to object storage.

## Testing checklist
1. Register/login citizen and verify invalid login rejection.
2. Login with authority account and verify citizen cannot open authority APIs.
3. Submit a complaint with an image and location.
4. Verify category, priority and confidence are generated server-side.
5. Verify the complaint is persisted in MySQL.
6. Verify HIGH complaints appear before MEDIUM and LOW.
7. Search/filter/sort complaints.
8. Assign a complaint and change status through the workflow.
9. Verify the citizen timeline reflects status changes.
10. Verify analytics are computed from database records.

## Important limitation
The included ML dataset is a demonstration baseline, not a production-grade public-service model. Before real government use, train and evaluate against representative, labeled local complaint data, document precision/recall and bias checks, and add human review for safety-critical cases.
