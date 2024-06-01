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
from playwright.async_api import async_playwright

# 0 = spesial, 1 = request, 2 = playwright, 3 = ???
sites = [
    ["https://mangadex.org/search?q=", "https://mangadex.org/title/", 0],
    ["https://asuratoon.com/?s=", "https://asuratoon.com/manga/", 1],
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

# Untuk scrape situs yang bisa dihandali oleh request biasa
async def request(site, title):
    # "https://www.wuxiaworld.com/q=122221"
    link = site[0] + title.replace(" ", "+")

    raw_response = requests.get(link)
    raw_response.encoding = 'utf-8'
    soup = BeautifulSoup(raw_response.text, 'html.parser')
    a_hrefs = soup.find_all("a", attrs={"href": re.compile("^"+site[1])})

    print(soup.prettify())
    print()

    for a_href in a_hrefs:
      results.append(a_href['href'])

# Untuk scrape situs yang tidak bisa dihandali oleh request biasa (SPA, JS-heavy, dst)
async def playwright(site, title):
    async with async_playwright() as playwright:
        playwright_version = str(subprocess.getoutput("playwright --version")).strip().split(" ")[1]
        capabilities["LT:Options"]["playwrightClientVersion"] = playwright_version
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(site[0] + title)
        
        locator = page.locator(".listupd")
        outerHTML = await locator.evaluate("el => el.outerHTML")
        soup = BeautifulSoup("".join(outerHTML), 'html.parser')
        a_hrefs = soup.find_all("a", attrs={"href": re.compile("^"+site[1])})
        
        for a_href in a_hrefs:
            results.append(a_href['href'])
        await browser.close()

# MangaDex ada API-nya jadi gak ada alasan untuk nggak pake
async def mangadex(title):
# def mangadex(title):
    # Dari docs API https://api.mangadex.org/docs/swagger.html#/Manga/get-search-manga
    # Docs API sikok lagi buruk nian, yang ini biso simulate url
    r = requests.get(f"https://api.mangadex.org/manga?title={title}&contentRating%5B%5D=safe&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&order%5Brelevance%5D=desc&hasAvailableChapters=true")
    for manga in r.json()["data"]:
        results.append(f"https://mangadex.org/title/{manga['id']}")

async def search(title):
    await asyncio.gather(
        mangadex(title), 
        playwright(sites[1], title)
    )
    for result in results:
        print(result)

if __name__ == "__main__":
    title = input("Search for: ")
    asyncio.run(search(title))