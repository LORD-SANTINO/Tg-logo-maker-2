from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
import requests
import os
import time

app = FastAPI()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
REPLICATE_MODEL_VERSION = "7b995189f2b87bee1696ac0b457fea3886f0c5e9963d6d9cc765f6de61215092"  # Stable Diffusion 2 logo-ish model example, update if needed

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head><title>AI Logo Generator using Replicate</title></head>
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
    if not REPLICATE_API_TOKEN:
        raise HTTPException(status_code=500, detail="Replicate API token not configured")

    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }
    json_data = {
        "version": REPLICATE_MODEL_VERSION,
        "input": {
            "prompt": prompt,
        },
    }

    try:
        # Kick off prediction
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=json_data
        )
        response.raise_for_status()
        prediction = response.json()

        # Poll for completion
        prediction_url = prediction["urls"]["get"]
        status = prediction["status"]

        while status not in ("succeeded", "failed", "canceled"):
            time.sleep(1)
            r = requests.get(prediction_url, headers=headers)
            r.raise_for_status()
            prediction = r.json()
            status = prediction["status"]

        if status != "succeeded":
            return f"<h2>Prediction failed with status: {status}</h2>"

        # Get output image(s)
        output = prediction.get("output", [])
        # Replicate may return a list of image URLs
        logo_url = output[0] if isinstance(output, list) and output else None

        if not logo_url:
            return "<h2>Failed to generate logo image URL.</h2>"

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
    except Exception as e:
        return f"<h2>Error during logo generation: {e}</h2>"
