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

# header, bagian search, bagian manga, batasan segment, tipe
# 0 = spesial, 1 = request, 2 = playwright
sites = [
    ["https://mangadex.org", "/search?q=", "/title/", 0],
    ["https://asuratoon.com", "/?s=", "/manga/", 0],
    ["https://mangapill.com", "/search?q=", "/manga/", 1],
    ["https://mangapark.net", "/search?word=", "/title/", 1]
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
    link = site[0] + site[1] + title_url(title)

    raw_response = requests.get(link)
    raw_response.encoding = 'utf-8'
    a_hrefs = get_a_hrefs(raw_response.text, site[2])

    for a_href in a_hrefs:
      results.append(site[0] + a_href)

# Untuk scrape situs yang tidak bisa dihandali oleh request biasa (SPA, JS-heavy, dst)
async def playwright(site, title):
    async with async_playwright() as playwright:
        playwright_version = str(subprocess.getoutput("playwright --version")).strip().split(" ")[1]
        capabilities["LT:Options"]["playwrightClientVersion"] = playwright_version
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(site[0] + site[1] + title_url(title))

        outerHTML = await page.evaluate("el => el.outerHTML")
        a_hrefs = get_a_hrefs("".join(outerHTML), site[2])
        
        for a_href in a_hrefs:
            results.append(site[0] + a_href)
        await browser.close()

# Asura pakai playwright
async def asuratoon(title):
    async with async_playwright() as playwright:
        playwright_version = str(subprocess.getoutput("playwright --version")).strip().split(" ")[1]
        capabilities["LT:Options"]["playwrightClientVersion"] = playwright_version
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://asuratoon.com/?s=" + title_url(title))
        
        locator = page.locator(".listupd")
        outerHTML = await locator.evaluate("el => el.outerHTML")
        a_hrefs = get_a_hrefs("".join(outerHTML), "^https://asuratoon.com/manga/")
        
        for a_href in a_hrefs:
            results.append(a_href)
        await browser.close()

# MangaDex ada API-nya jadi gak ada alasan untuk nggak pake
async def mangadex(title):
# def mangadex(title):
    # Dari docs API https://api.mangadex.org/docs/swagger.html#/Manga/get-search-manga
    # Docs API sikok lagi buruk nian, yang ini biso simulate url
    r = requests.get(f"https://api.mangadex.org/manga?title={title_url(title)}&contentRating%5B%5D=safe&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&order%5Brelevance%5D=desc&hasAvailableChapters=true")
    for manga in r.json()["data"][0:limit]:
        results.append(f"https://mangadex.org/title/{manga['id']}")

def title_url(title):
    return urllib.parse.quote_plus(title)

def get_a_hrefs(outerHTML, header):
    soup = BeautifulSoup(outerHTML, 'html.parser')
    a_hrefs = soup.find_all("a", attrs={"href": re.compile("^"+header)})
    a_hrefs = sorted(list(set([a_href["href"] for a_href in a_hrefs])))
    return a_hrefs[0:limit]

limit = 999

async def search(title):
    await asyncio.gather(
        mangadex(title), 
        asuratoon(title),
        request(sites[2], title),
        request(sites[3], title)
    )
    for result in results:
        print(result)


if __name__ == "__main__":
    title = input("Search for: ")
    asyncio.run(search(title.replace(" ", "+")))