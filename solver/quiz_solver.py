import time
from bs4 import BeautifulSoup
import base64
import json
import requests

from solver.browser import get_browser

async def solve_quiz(req):
    start_time = time.time()

    email = req.email
    secret = req.secret
    url = req.url

    playwright, browser, page = await get_browser()

    try:
        while True:

            if time.time() - start_time > 175:  # small safety margin
                raise Exception("Time limit exceeded (3 minutes).")

            # Go to quiz page
            await page.goto(url, wait_until="networkidle")

            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")

            # Extract JS-rendered text
            text = soup.get_text()

            # ----- EXTRACT QUESTION -----
            # Each quiz page will have its own question wording.
            # You must write custom logic to detect patterns.
            # For now, we detect common patterns.

            answer = await interpret_and_solve_question(page, soup, text)

            # Find submit URL inside HTML
            submit_url = extract_submit_url(text)
            if not submit_url:
                raise Exception("Submit URL not found on quiz page.")

            # Submit answer
            payload = {
                "email": email,
                "secret": secret,
                "url": url,
                "answer": answer
            }

            r = requests.post(submit_url, json=payload, timeout=30)
            result = r.json()

            if not result.get("correct"):
                # wrong — try again, or move to provided next URL
                next_url = result.get("url")
                if next_url:
                    url = next_url
                    continue
                else:
                    raise Exception("Incorrect answer and no next url provided.")

            # correct — check if quiz ends or continue
            next_url = result.get("url")
            if not next_url:
                return {"status": "completed", "answer": answer}

            url = next_url

    finally:
        await browser.close()
        await playwright.stop()


import re

def extract_submit_url(text):
    match = re.search(r'https?://[^\s"]+/submit', text)
    return match.group(0) if match else None


async def interpret_and_solve_question(page, soup, text):
    text_lower = text.lower()

    # Example: sum of "value" column
    if "sum of the" in text_lower and "value" in text_lower:
        # Download file link
        links = soup.find_all("a")
        for link in links:
            href = link.get("href")
            if href.endswith(".pdf") or href.endswith(".csv"):
                return compute_sum_from_file(href)

    # Add more patterns as quizzes appear
    # Example: count rows, average, max, boolean, JSON creation.

    # Default fallback (should rarely be hit)
    raise Exception("Question format not recognized.")
