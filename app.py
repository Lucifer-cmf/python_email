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

class OTPPayload(BaseModel):
    email: EmailStr
    username: str
    otp: str

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
            <p>We're thrilled to have you on board! Start exploring your courses now:</p>
            <a href="{login_url}" style="background-color:#4f46e5;color:white;padding:10px 20px;
               text-decoration:none;border-radius:6px;">Login to SMBJugaad</a>
            <p style="font-size:14px;">If the button doesn't work, copy this link:</p>
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
# 2️⃣ Send OTP Email for Login
# -----------------------------
@app.post("/send-otp-email")
async def send_otp_email_endpoint(payload: OTPPayload, request: Request):
    api_key = request.headers.get("x-internal-api-key")
    if not api_key or api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    try:
        html = f"""
          <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 30px; border-radius: 10px; text-align: center;">
              <h2 style="color: white; margin: 0;">Your Login OTP</h2>
            </div>
            
            <div style="background: #f7fafc; padding: 30px; border-radius: 10px; margin-top: 20px;">
              <p style="font-size: 16px; color: #2d3748;">Hi {payload.username},</p>
              <p style="font-size: 14px; color: #4a5568;">
                Use the following One-Time Password (OTP) to log in to your SMBJugaad LMS account:
              </p>
              
              <div style="background: white; border: 2px dashed #667eea; border-radius: 8px; 
                          padding: 20px; margin: 30px 0; text-align: center;">
                <p style="font-size: 12px; color: #718096; margin: 0 0 10px 0;">YOUR OTP CODE</p>
                <h1 style="color: #667eea; font-size: 36px; letter-spacing: 8px; margin: 0; 
                           font-family: 'Courier New', monospace;">{payload.otp}</h1>
              </div>
              
              <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; 
                          border-radius: 4px; margin: 20px 0;">
                <p style="margin: 0; font-size: 14px; color: #856404;">
                  ⚠️ <strong>Important:</strong> This OTP is valid for <strong>5 minutes</strong> only.
                </p>
              </div>
              
              <p style="font-size: 13px; color: #718096; margin-top: 20px;">
                If you didn't request this OTP, please ignore this email or contact support if you have concerns.
              </p>
            </div>
            
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;"/>
            
            <div style="text-align: center;">
              <p style="font-size: 12px; color: #a0aec0; margin: 5px 0;">
                © 2025 SMBJugaad LMS. All rights reserved.
              </p>
              <p style="font-size: 11px; color: #cbd5e0;">
                This is an automated message, please do not reply to this email.
              </p>
            </div>
          </div>
        """
        send_gmail(payload.email, "Your SMBJugaad LMS Login OTP", html)
        print(f"✅ OTP email sent to {payload.email}")
        return {"message": "OTP email sent successfully."}
    except Exception as e:
        print(f"❌ Failed to send OTP email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# 3️⃣ Send Password Reset Email (kept for account recovery)
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
            <p style="font-size:14px;">If you didn't request this, you can safely ignore this email.</p>
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
# Health check endpoint
# -----------------------------
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SMBJugaad Email Service"}


# -----------------------------
# Run locally for testing
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
