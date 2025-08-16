from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import requests
import os

app = FastAPI()

DEEPAI_API_KEY = os.getenv("DEEPAI_API_KEY")

@app.get("/", response_class=HTMLResponse)
def home():
    # Simple form for entering the logo description
    return """
    <html>
        <head>
            <title>AI Logo Generator</title>
        </head>
        <body>
            <h1>AI Logo Generator</h1>
            <form action="/generate" method="post">
                <label for="prompt">Describe your logo:</label>
                <input type="text" id="prompt" name="prompt" required>
                <button type="submit">Generate Logo</button>
            </form>
        </body>
    </html>
    """

@app.post("/generate", response_class=HTMLResponse)
def generate_logo(prompt: str = Form(...)):
    url = "https://api.deepai.org/api/logo-generator"
    response = requests.post(
        url,
        data={"text": prompt},
        headers={"api-key": DEEPAI_API_KEY}
    )
    result = response.json()
    logo_url = result.get("output_url", None)

    if logo_url is None:
        return f"<h2>Failed to generate logo. Please try again.</h2>"

    return f"""
    <html>
        <head><title>Logo Result</title></head>
        <body>
            <h1>Your Logo</h1>
            <img src="{logo_url}" alt="Generated Logo" style="max-width:300px;"/>
            <p><a href="/">Generate another</a></p>
        </body>
    </html>
    """
                  
