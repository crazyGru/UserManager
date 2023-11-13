from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
import mysql.connector
import stripe

router = APIRouter()

# Establish a connection to your MySQL database
db = mysql.connector.connect(
    host="ditmar.cu7mfbovde5z.us-east-1.rds.amazonaws.com",
    user="admin",
    password="123456789",
    database="harmony"
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
    query = "SELECT * FROM users WHERE email = %s AND pass = %s"
    values = (user.email, user.password)
    cursor.execute(query, values)
    result = cursor.fetchone()

    if result:
        print(result)
        print(type(result))
        return {"message": "Sign-in successful", "name":result['username'], "level":result['lvl'], "expire":result['expire_day']}
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
                pass VARCHAR(255) NOT NULL,
                lvl INT DEFAULT 0,
                expire_day DATE
            )
        """)

    # Check if the username or email already exists
    query = "SELECT id FROM users WHERE username = %s OR email = %s"
    values = (user.username, user.email)
    cursor.execute(query, values)
    existing_user = cursor.fetchone()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Insert the new user into the 'users' table
    query = "INSERT INTO users (username, email, pass) VALUES (%s, %s, %s)"
    values = (user.username, user.email, user.password)
    cursor.execute(query, values)
    db.commit()

    return {"message": "Sign-up successful"}

@router.get("/")
def helps():
    print("Running")
    return {"message": "Connection successful"}


@router.post('/premium')
async def process_premium(payment_detila: dict):
    try:
        payment_intent =stripe.PaymentIntent.create(
            amount=1799,
            currency='usd',
            payment_method_types=['card'],
        )
        return payment_intent
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))