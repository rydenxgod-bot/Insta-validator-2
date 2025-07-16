from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from playwright.async_api import async_playwright
import json
import re

app = FastAPI()

@app.get("/")
async def check_instagram(username: str = Query(..., description="Instagram username to check")):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            url = f"https://www.instagram.com/{username}/"
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            content = await page.content()
            await browser.close()

            # Detect invalid usernames
            if "<title>Page Not Found" in content or "content=\"404\"" in content:
                return JSONResponse({
                    "status": "fail",
                    "message": f"Username '{username}' not found.",
                    "username": username
                }, status_code=404)

            # Extract __NEXT_DATA__ script JSON
            match = re.search(r'<script type="application/json" id="__NEXT_DATA__">(.+?)</script>', content)
            if not match:
                return JSONResponse({
                    "status": "error",
                    "message": "Unable to extract Instagram profile data.",
                    "username": username
                }, status_code=500)

            data = json.loads(match.group(1))
            user = data["props"]["pageProps"]["graphql"]["user"]

            return JSONResponse({
                "status": "success",
                "message": f"Username '{username}' found.",
                "username": username,
                "full_name": user.get("full_name"),
                "is_verified": user.get("is_verified"),
                "profile_pic_url": user.get("profile_pic_url_hd"),
                "posts": user["edge_owner_to_timeline_media"]["count"],
                "followers": user["edge_followed_by"]["count"],
                "following": user["edge_follow"]["count"]
            }, status_code=200)

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": "Something went wrong",
            "error": str(e),
            "username": username
        }, status_code=500)