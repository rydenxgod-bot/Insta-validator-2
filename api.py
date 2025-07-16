from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from playwright.async_api import async_playwright
import re
import json

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

            # Check for invalid username
            if "<title>Page Not Found" in content or "content=\"404\"" in content:
                return JSONResponse({
                    "status": "fail",
                    "message": f"Username '{username}' not found.",
                    "username": username
                }, status_code=404)

            # Parse embedded JSON from window._sharedData
            shared_data_match = re.search(r"window\._sharedData\s*=\s*(\{.*\});</script>", content)
            if not shared_data_match:
                return JSONResponse({
                    "status": "error",
                    "message": "Unable to extract Instagram profile data.",
                    "username": username
                }, status_code=500)

            shared_data = json.loads(shared_data_match.group(1))
            user = shared_data['entry_data']['ProfilePage'][0]['graphql']['user']

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