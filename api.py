from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from playwright.async_api import async_playwright
import asyncio

app = FastAPI()

@app.get("/")
async def root(username: str = Query(..., description="Instagram username to check")):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(f"https://www.instagram.com/{username}/", timeout=30000)

            content = await page.content()
            await browser.close()

            if "Sorry, this page isn't available" in content or "Page Not Found" in content:
                return JSONResponse({
                    "status": "fail",
                    "message": f"Username '{username}' not found.",
                    "username": username
                }, status_code=404)
            else:
                return JSONResponse({
                    "status": "success",
                    "message": f"Username '{username}' found.",
                    "username": username
                })

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": "Something went wrong",
            "error": str(e),
            "username": username
        }, status_code=500)