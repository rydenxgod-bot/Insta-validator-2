from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from playwright.async_api import async_playwright
import asyncio
import re

app = FastAPI()

@app.get("/")
async def root(username: str = Query(..., description="Instagram username to check")):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(
                f"https://www.instagram.com/{username}/",
                timeout=30000,
                wait_until="domcontentloaded"
            )

            html = await page.content()
            await browser.close()

            # Check title tag
            if "<title>Page Not Found" in html or "content=\"404\"" in html:
                return JSONResponse({
                    "status": "fail",
                    "message": f"Username '{username}' not found.",
                    "username": username
                }, status_code=404)

            # Extract full name from <title> tag (optional)
            match = re.search(r'<title>(.*?) \(@' + re.escape(username) + r'\)', html)
            full_name = match.group(1).strip() if match else None

            return JSONResponse({
                "status": "success",
                "message": f"Username '{username}' found.",
                "username": username,
                "full_name": full_name
            }, status_code=200)

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": "Something went wrong",
            "error": str(e),
            "username": username
        }, status_code=500)