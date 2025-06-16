from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from . import models, schemas, crud, auth
from .db import SessionLocal, engine, Base
from .auth import create_access_token
from datetime import timedelta

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Sentinel Licensing API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/signup", response_model=schemas.Token)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    user_obj = crud.create_user(db, user.username, user.password)
    access_token = create_access_token({"sub": user_obj.username})
    return {"access_token": access_token}

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.username})
    # Log login
    models.LoginLog(username=user.username, ip_address="") # Optionally log IP here
    return {"access_token": access_token}

@app.post("/license/check", response_model=schemas.LicenseInfo)
def check_license(data: schemas.LicenseCheck, db: Session = Depends(get_db)):
    user = crud.get_user(db, data.username)
    if not user or user.uuid != data.uuid:
        raise HTTPException(status_code=404, detail="User or UUID not found")
    lic = crud.get_active_license(db, data.username)
    if not lic:
        raise HTTPException(status_code=403, detail="No active license. Trial expired or not activated.")
    return schemas.LicenseInfo(
        license_type=lic.license_type,
        issued_at=lic.issued_at,
        expires_at=lic.expires_at,
        is_active=lic.is_active
    )

@app.post("/license/activate", response_model=schemas.LicenseInfo)
def activate_license(username: str, db: Session = Depends(get_db)):
    # This would be called after purchase, e.g. admin or payment webhook
    lic = crud.activate_full_license(db, username)
    return schemas.LicenseInfo(
        license_type=lic.license_type,
        issued_at=lic.issued_at,
        expires_at=lic.expires_at,
        is_active=lic.is_active
    )