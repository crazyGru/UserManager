from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
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
        return {"message": "Sign-in successful", "name":result[1], "mail":result[2], "level":result[4], "expire":result[5]}
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


@router.post("/create-checkout-session")
async def create_checkout_session():
    session = await stripe.checkout.sessions.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "T-shirt",
                    },
                    "unit_amount": 2000,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="localhost:8000/home",
        cancel_url="localhost:8000/pricing",
    )
    return JSONResponse(content={"url": session.url})

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.json()  # This line extracts the JSON payload from the request

    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, "we_1OCOuVItQ91j83DiPPMX5hgi"
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail=f"Invalid signature: {e}")

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        # Payment succeeded, update your database or perform other actions
        print('Payment succeeded!')

    return {"status": "success"}