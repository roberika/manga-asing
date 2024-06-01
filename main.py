from bs4 import BeautifulSoup
import requests
import asyncio
import random
import json
import time
import re
import json
import logging
import os
import subprocess
import sys
import time
import urllib
from playwright.sync_api import sync_playwright

# 0 = spesial, 1 = request, 2 = playwright, 3 = ???
sites = [
    ["https://mangadex.org/search?q=", "https://mangadex.org/title/", 0]
]

results = []

capabilities = {
    "browserName": "Chrome",  # Browsers allowed: `Chrome`, `MicrosoftEdge`, `pw-chromium`, `pw-firefox` and `pw-webkit`
    "browserVersion": "latest",
    "LT:Options": {
        "platform": "Windows 11",
        "build": "Manga Asing Scrape Build",
        "name": "Scrape Manga Search Results",
        "network": False,
        "video": True,
        "console": True,
        "tunnel": False,  # Localhost
        "tunnelName": "",  # Optional, localhost dst
        "geoLocation": "ID",
    },
}

# Untuk scrape situs yang tidak bisa dihandali oleh request biasa (SPA, JS-heavy, dst)
async def playwright(sites):
    with sync_playwright() as playwright:
        playwright_version = (
            str(subprocess.getoutput("playwright --version")).strip().split(" ")[1]
        )
        capabilities["LT:Options"]["playwrightClientVersion"] = playwright_version
        browser = playwright.chromium.launch(headless=False) 
        page = browser.new_page()
        try:            
            # section to navigate to software category  
            page.goto("https://ecommerce-playground.lambdatest.io/")
            page.wait_for_selector("")
        except Exception as ex:
            print(str(ex))
        finally:
            print(page.inner_html())

# MangaDex ada API-nya jadi gak ada alasan untuk nggak pake
async def mangadex(title):
# def mangadex(title):
    # Dari docs API https://api.mangadex.org/docs/swagger.html#/Manga/get-search-manga
    # Docs API sikok lagi buruk nian, yang ini biso simulate url
    print("Loading...")
    await asyncio.sleep(5)
    print("Starting...")
    r = requests.get(f"https://api.mangadex.org/manga?title={title}&contentRating%5B%5D=safe&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&order%5Brelevance%5D=desc&hasAvailableChapters=true")
    await asyncio.sleep(5)
    print([f"https://mangadex.org/title/{manga['id']}" for manga in r.json()["data"]])

async def main():
    await asyncio.gather(
        mangadex("a manga"), 
        mangadex("a manga")
    )

if __name__ == "__main__":
    asyncio.run(main())