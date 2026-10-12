import os, re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

BASE = os.path.dirname(os.path.dirname(__file__))
ML_DIR = os.path.join(BASE, 'ml')
CATEGORY = ['Pothole/Road Damage','Garbage/Waste','Water Leakage','Broken Streetlight','Drainage/Sewage','Other']
PRIORITIES = ['HIGH','MEDIUM','LOW']
HIGH_SIGNALS = ['accident','danger','emergency','school','hospital','fire','flooding','severe','life threatening','major leakage','blocked road','unsafe','immediate','electrical hazard','injury','risk']

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s/]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def _paths(kind): return os.path.join(ML_DIR, f'{kind}_model.pkl'), os.path.join(ML_DIR, f'{kind}_vectorizer.pkl')

def load(kind):
    mp, vp = _paths(kind)
    if not (os.path.exists(mp) and os.path.exists(vp)): return None, None
    return joblib.load(mp), joblib.load(vp)

def ensure_models():
    c, cv = load('category'); p, pv = load('priority')
    if c and p: return
    from ml.train_model import train_models
    train_models()

def predict(description):
    ensure_models()
    text = clean_text(description)
    cm, cv = load('category'); pm, pv = load('priority')
    cat_vec = cv.transform([text]); pri_vec = pv.transform([text])
    category = cm.predict(cat_vec)[0]
    priority_ml = pm.predict(pri_vec)[0]
    confidence = float(max(pm.predict_proba(pri_vec)[0])) if hasattr(pm,'predict_proba') else 0.75
    signals = [s for s in HIGH_SIGNALS if s in text]
    # Explainable safety layer: strong public-safety terms can elevate a baseline ML result.
    if signals and priority_ml != 'HIGH': priority = 'HIGH'
    else: priority = priority_ml
    if priority == 'HIGH' and signals: confidence = max(confidence, min(0.99, 0.72 + 0.04*len(signals)))
    return {'category':category,'priority':priority,'confidence':round(confidence,4),'signals':signals}
