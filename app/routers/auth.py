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
    database="mysql"
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

    # Check if the table exists
    cursor.execute("SHOW TABLES LIKE 'users'")
    table_exists = cursor.fetchone()

    if not table_exists:
        # Create the 'users' table if it doesn't exist
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                level INT DEFAULT 0,
                expire_day DATE
            )
        """)

    # Insert the new user into the 'users' table
    query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
    values = (user.username, user.email, user.password)
    cursor.execute(query, values)
    db.commit()

    return {"message": "Sign-up successful"}

@router.get("/")
def helps():
    print("Running")
    return {"message": "Connection successful"}