from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# origin = ["http://127.0.0.1:8005", "http://localhost:8005", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LOGIN

@app.post("/login")
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    # Retrieve the user from the database
    db_user = crud.get_user_by_email(db, email=user.email)
    
    # Check if user exists and the password is correct
    if db_user is None or db_user.hashed_password != user.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create a session for the user
    db_session = crud.create_session(db, user_id=db_user.id)
    
    # Return success along with the user ID and session token
    return {"success": True, "userId": db_user.id, "sessionId": db_session.token}

# LOGOUT

# Route for logging out and deleting the session from the database
@app.post("/logout")
def logout_user(response: Response, db: Session = Depends(get_db)):
    session_token = response.cookies.get("session_id") 
    if session_token:
        session = crud.get_session_by_token(db, session_token)
        if session:
            crud.delete_session(db, session.id)
    return {"message": "Logout successful"}

# Route for deleting a specific session
@app.delete("/session/{session_token}")
def delete_session(session_token: str, response: Response, db: Session = Depends(get_db)):
    session = crud.delete_session(db, session_token=session_token)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    response.delete_cookie("session_id")
    response.delete_cookie("isLoggedIn")
    return {"message": "Session deleted successfully"}

# USERS

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=list[schemas.User])
def read_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_all_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    updated_user = crud.update_user(db=db, user_id=user_id, user_update=user_update)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.delete_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ITEMS

@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db=db, item=item)

@app.get("/items/", response_model=list[schemas.Item])
def read_all_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.read_all_items(db, skip=skip, limit=limit)
    return items

@app.get("/users/{user_id}/items/", response_model=list[schemas.Item])
def read_items_by_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items_by_user_id(db, user_id=user_id, skip=skip, limit=limit)
    return items

@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_item_by_id(db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item_update: schemas.ItemUpdate, db: Session = Depends(get_db)):
    updated_item = crud.update_item(db=db, item_id=item_id, item_update=item_update)
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item

@app.delete("/items/{item_id}", response_model=schemas.Item)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.delete_item(db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/items/{item_id}/toggle", response_model=schemas.Item)
def toggle_item_status(item_id: int, db: Session = Depends(get_db)):
    # First, retrieve the item from the database
    item = crud.get_item_by_id(db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Toggle the completed status
    item.is_completed = not item.is_completed

    # Update the item in the database
    updated_item = crud.update_item(db=db, item_id=item_id, item_update=item)
    return updated_item