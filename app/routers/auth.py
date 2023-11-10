from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
import mysql.connector

router = APIRouter()

# Establish a connection to your MySQL database
db = mysql.connector.connect(
    host="ditmar.cu7mfbovde5z.us-east-1.rds.amazonaws.com",
    user="admin",
    password="123456789",
    database="your_database"
)

class UserSignIn(BaseModel):
    email: str
    password: str

class UserSignUp(BaseModel):
    username: str
    email: str
    password: str

@router.post("/signin")
def sign_in(user: UserSignIn):
    # Implement your sign-in logic here
    # Validate the user credentials and return a response
    cursor = db.cursor()
    query = "SELECT * FROM users WHERE email = %s AND password = %s"
    values = (user.email, user.password)
    cursor.execute(query, values)
    result = cursor.fetchone()

    if result:
        return {"message": "Sign-in successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/signup")
def sign_up(user: UserSignUp):
    # Implement your sign-up logic here
    # Create a new user with the provided details and return a response
    cursor = db.cursor()
    query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
    values = (user.username, user.email, user.password)
    cursor.execute(query, values)
    db.commit()

    return {"message": "Sign-up successful"}