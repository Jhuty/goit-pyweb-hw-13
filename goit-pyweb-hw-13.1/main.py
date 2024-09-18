from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
import crud
import models
import db
from schemas import Contact, ContactCreate
from typing import List, Optional
from datetime import datetime, timedelta
from auth import verify_token, create_access_token, create_refresh_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import EmailStr, BaseModel

from db import get_db
from models import User
from passlib.context import CryptContext

from main import get_current_user

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_limiter import FastAPILimiter
from redis import Redis

from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
import os

redis = Redis(host="localhost", port=6379, db=0)
FastAPILimiter.init(redis)

load_dotenv()
models.Base.metadata.create_all(bind=db.engine)

SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
CLOUD_NAME = os.getenv("CLOUD_NAME")
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI()

@app.post("/contacts/", response_model=Contact, status_code=201)
@limiter.limit("5/minute") 
def create_contact(contact: ContactCreate, db: Session = Depends(db.get_db), current_user: User = Depends(get_current_user)):
    return crud.create_contact(db=db, contact=contact, user_id=current_user.id)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Contacts API"}

@app.post("/contacts/", response_model=Contact, status_code=201)
def create_contact(contact: ContactCreate, db: Session = Depends(db.get_db), current_user: User = Depends(get_current_user)):
    return crud.create_contact(db=db, contact=contact, user_id=current_user.id)

@app.get("/contacts/{contact_id}", response_model=Contact)
def read_contact(contact_id: int, db: Session = Depends(db.get_db), current_user: User = Depends(get_current_user)):
    db_contact = crud.get_contact(db, contact_id=contact_id)
    if db_contact is None or db_contact.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

def update_contact(contact_id: int, contact: ContactCreate, db: Session = Depends(db.get_db), current_user: User = Depends(get_current_user)):
    db_contact = crud.update_contact(db=db, contact_id=contact_id, contact=contact, user_id=current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found or not authorized")
    return db_contact

@app.delete("/contacts/{contact_id}", response_model=Contact)
def delete_contact(contact_id: int, db: Session = Depends(db.get_db)):
    db_contact = crud.delete_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.get("/contacts/search", response_model=List[Contact])
def search_contacts(
    name: Optional[str] = None,
    surname: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(db.get_db)
):
    query = db.query(Contact)
    if name:
        query = query.filter(Contact.first_name.ilike(f"%{name}%"))
    if surname:
        query = query.filter(Contact.last_name.ilike(f"%{surname}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    
    results = query.all()
    if not results:
        raise HTTPException(status_code=404, detail="Contacts not found")
    return results

@app.get("/contacts/upcoming-birthdays", response_model=List[Contact])
def get_upcoming_birthdays(db: Session = Depends(db.get_db)):
    today = datetime.today()
    upcoming = today + timedelta(days=7)
    
    contacts = db.query(Contact).filter(
        Contact.birthday.between(today, upcoming)
    ).all()
    
    if not contacts:
        raise HTTPException(status_code=404, detail="No upcoming birthdays found")
    
    return contacts

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = verify_token(token, credentials_exception)
    user = db.query(User).filter(User.username == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(username: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists")
    hashed_password = get_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@router.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30))
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = verify_token(refresh_token, credentials_exception)
    new_access_token = create_access_token(data={"sub": user_id}, expires_delta=timedelta(minutes=30))

    return {"access_token": new_access_token, "token_type": "bearer"}

@app.get("/verify/{token}")
def verify_email(token: str, db: Session = Depends(db.get_db)):
    user_id = verify_token(token, credentials_exception)
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_verified = True
        db.commit()
        return {"message": "Email verified successfully"}
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/send-email")
async def send_verification_email(background_tasks: BackgroundTasks, body: EmailSchema, token: str):
    message = MessageSchema(
        subject="Email Verification",
        recipients=[body.email],
        template_body={"fullname": "Billy Jones", "verification_link": f"http://localhost:8000/verify/{token}"},
        subtype=MessageType.html
    )

    fm = FastMail(conf)

    background_tasks.add_task(fm.send_message, message, template_name="verification_email.html")

    return {"message": "Verification email has been sent"}


@app.post("/users/{user_id}/avatar")
def upload_avatar(user_id: int, file: UploadFile = File(...), db: Session = Depends(db.get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Upload file to Cloudinary
    result = cloudinary.uploader.upload(file.file, folder="avatars")
    user.avatar_url = result.get("url")
    db.commit()

    return {"avatar_url": user.avatar_url}