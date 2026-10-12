import os, joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

BASE=os.path.dirname(__file__)
CATEGORY_DATA=[
('large pothole on road causing accidents','Pothole/Road Damage'),('road is damaged with deep potholes','Pothole/Road Damage'),('broken road near school','Pothole/Road Damage'),
('garbage overflowing near houses','Garbage/Waste'),('waste collection not happening','Garbage/Waste'),('trash dumped on street','Garbage/Waste'),
('water pipe leakage on main road','Water Leakage'),('water leaking continuously from pipeline','Water Leakage'),('major water leakage near hospital','Water Leakage'),
('street light is not working','Broken Streetlight'),('broken lamp on main road','Broken Streetlight'),('streetlight is off at night','Broken Streetlight'),
('drainage blocked after rain','Drainage/Sewage'),('sewage overflowing in street','Drainage/Sewage'),('blocked drain causing flooding','Drainage/Sewage'),
('park needs maintenance','Other'),('public issue needs attention','Other'),('community facility damaged','Other')]
PRIORITY_DATA=[
('large pothole near school causing accidents','HIGH'),('major water leakage blocking road','HIGH'),('drainage blockage causing flooding','HIGH'),('electrical hazard streetlight sparks','HIGH'),('unsafe road causing injury risk','HIGH'),
('garbage overflowing near residential area','MEDIUM'),('water leakage on local street','MEDIUM'),('streetlight not working on main road','MEDIUM'),('blocked drain with bad smell','MEDIUM'),
('small litter issue in park','LOW'),('minor streetlight issue','LOW'),('small pothole with no immediate danger','LOW'),('general maintenance request','LOW')]

def train_models():
    x=[a for a,b in CATEGORY_DATA]; y=[b for a,b in CATEGORY_DATA]
    cv=TfidfVectorizer(ngram_range=(1,2),sublinear_tf=True); cx=cv.fit_transform(x); cm=LogisticRegression(max_iter=2000).fit(cx,y)
    x2=[a for a,b in PRIORITY_DATA]; y2=[b for a,b in PRIORITY_DATA]
    pv=TfidfVectorizer(ngram_range=(1,2),sublinear_tf=True); px=pv.fit_transform(x2); pm=LogisticRegression(max_iter=2000).fit(px,y2)
    joblib.dump(cm,os.path.join(BASE,'category_model.pkl')); joblib.dump(pm,os.path.join(BASE,'priority_model.pkl')); joblib.dump(cv,os.path.join(BASE,'category_vectorizer.pkl')); joblib.dump(pv,os.path.join(BASE,'priority_vectorizer.pkl'))
    return cm,pm
if __name__=='__main__': train_models(); print('Baseline models trained.')
