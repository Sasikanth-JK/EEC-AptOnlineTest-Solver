import os

class Config:
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCGItNfRGlok5xr5ND_ebnYqQMJlg-6U7c")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-pro") # https://ai.google.dev/gemini-api/docs/models for other model names
    
    # Portal Credentials
    USER_ID = os.getenv("USER_ID")
    PASSWORD = os.getenv("PASSWORD")
    PORTAL_URL = os.getenv("PORTAL_URL", "https://oxygen.aptonlinetest.co.in/hurricane")