from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from . import models, auth

TRIAL_PERIOD_DAYS = 30

def create_user(db: Session, username: str, password: str):
    user = models.User(
        username=username,
        password_hash=auth.hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    # Create initial trial license
    expires_at = datetime.now() + timedelta(days=TRIAL_PERIOD_DAYS)
    license = models.License(
        username=user.username,
        license_type="trial",
        issued_at=datetime.now(),
        expires_at=expires_at,
        is_active=True
    )
    db.add(license)
    db.commit()
    return user

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not auth.verify_password(password, user.password_hash):
        return None
    return user

def get_active_license(db: Session, username: str):
    now = datetime.now()
    return db.query(models.License)\
        .filter(models.License.username == username)\
        .filter(models.License.is_active == True)\
        .filter(models.License.expires_at > now)\
        .order_by(models.License.expires_at.desc())\
        .first()

def activate_full_license(db: Session, username: str, duration_days: int = 365):
    # Deactivate old licenses
    db.query(models.License)\
        .filter(models.License.username == username, models.License.is_active == True)\
        .update({models.License.is_active: False})
    expires_at = datetime.now() + timedelta(days=duration_days)
    license = models.License(
        username=username,
        license_type="full",
        issued_at=datetime.now(),
        expires_at=expires_at,
        is_active=True
    )
    db.add(license)
    user = get_user(db, username)
    if user:
        user.has_active_license = True
    db.commit()
    return license