from sqlalchemy.orm import Session
from . import models, schemas
import secrets
import string

# USERS

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_pass = user.password + "examplehash"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_pass)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db:Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
#     db_user = db.query(models.User).filter(models.User.id == user_id).first()
#     if db_user:
#         for attr, value in user_update.dict().items():
#             setattr(db_user, attr, value)
#         db.commit()
#         db.refresh(db_user)
#     return db_user

def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(user)
    db.commit()
    return user

# ITEMS

def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.dict(), is_completed=False)  # Set is_completed to False by default
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def read_all_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def get_items_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Item).filter(models.Item.owner_id == user_id).offset(skip).limit(limit).all()

def get_item_by_id(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def update_item(db: Session, item_id: int, item_update: schemas.ItemUpdate):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        for attr, value in item_update.__dict__.items():
            if hasattr(db_item, attr):
                setattr(db_item, attr, value)
        db.commit()
        db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    db.delete(item)
    db.commit()
    return item

def generate_session_token(length=32):
    # Generate a random session token using letters and digits
    alphabet = string.ascii_letters + string.digits
    session_token = ''.join(secrets.choice(alphabet) for _ in range(length))
    return session_token

def create_session(db: Session, user_id: int):
    session_token = generate_session_token()  # You'll need to implement this function to generate a unique session token
    db_session = models.Session(token=session_token, user_id=user_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def delete_session(db: Session, session_token: str):
    session = db.query(models.Session).filter(models.Session.token == session_token).first()
    if session:
        db.delete(session)
        db.commit()
        return session
    return None
