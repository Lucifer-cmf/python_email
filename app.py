import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import FastAPI, Request, HTTPException, status
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_APP_PASSWORD = os.getenv("SENDER_APP_PASSWORD") 
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app = FastAPI()

# --- Pydantic Models ---
class WelcomePayload(BaseModel):
    email: EmailStr
    username: str

class ResetPasswordPayload(BaseModel):
    email: EmailStr
    username: str
    reset_url: str


# -----------------------------
# Helper function: send email
# -----------------------------
def send_gmail(receiver_email: str, subject: str, html_content: str):
    """Handles SMTP connection and email sending."""
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"SMBJugaad LMS <{SENDER_EMAIL}>"
    message["To"] = receiver_email

    message.attach(MIMEText(html_content, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, message.as_string())


# -----------------------------
# 1️⃣ Send Welcome Email
# -----------------------------
@app.post("/send-welcome-email")
async def send_welcome_email_endpoint(payload: WelcomePayload, request: Request):
    api_key = request.headers.get("x-internal-api-key")
    if not api_key or api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    try:
        login_url = f"{FRONTEND_URL}/login?email={payload.email}"
        html = f"""
          <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
            <h2 style="color:#4f46e5;">Welcome to SMBJugaad LMS, {payload.username} 🎉</h2>
            <p>We’re thrilled to have you on board! Start exploring your courses now:</p>
            <a href="{login_url}" style="background-color:#4f46e5;color:white;padding:10px 20px;
               text-decoration:none;border-radius:6px;">Login to SMBJugaad</a>
            <p style="font-size:14px;">If the button doesn’t work, copy this link:</p>
            <p>{login_url}</p>
            <hr/>
            <p style="font-size:12px;color:#999;">© 2025 SMBJugaad LMS</p>
          </div>
        """
        send_gmail(payload.email, "Welcome to SMBJugaad LMS 🎉", html)
        print(f"✅ Welcome email sent to {payload.email}")
        return {"message": "Welcome email sent successfully."}
    except Exception as e:
        print(f"❌ Failed to send welcome email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# 2️⃣ Send Password Reset Email
# -----------------------------
@app.post("/send-password-reset-email")
async def send_reset_password_email_endpoint(payload: ResetPasswordPayload, request: Request):
    api_key = request.headers.get("x-internal-api-key")
    if not api_key or api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    try:
        html = f"""
          <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
            <h2 style="color:#4f46e5;">Password Reset Request</h2>
            <p>Hi {payload.username},</p>
            <p>We received a request to reset your password. Click the button below to continue:</p>
            <a href="{payload.reset_url}" style="background-color:#4f46e5;color:white;
               padding:10px 20px;text-decoration:none;border-radius:6px;">Reset Password</a>
            <p style="font-size:14px;">If you didn’t request this, you can safely ignore this email.</p>
            <p style="font-size:14px;">Or copy and paste this link into your browser:</p>
            <p>{payload.reset_url}</p>
            <hr/>
            <p style="font-size:12px;color:#999;">© 2025 SMBJugaad LMS</p>
          </div>
        """
        send_gmail(payload.email, "Reset your SMBJugaad LMS password", html)
        print(f"✅ Password reset email sent to {payload.email}")
        return {"message": "Password reset email sent successfully."}
    except Exception as e:
        print(f"❌ Failed to send reset email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# Run locally for testing
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
