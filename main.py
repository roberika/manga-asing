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
from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath
from playwright.async_api import async_playwright

# header, bagian search, bagian manga, batasan segment, title, filter out
# 0 = spesial, 1 = request, 2 = playwright
sites = [
    ["https://mangadex.org", "/search?q=", "/title/", None, False, None],
    ["https://asuratoon.com", "/?s=", "https://asuratoon.com/manga/", None, False, {"class" : "series"}],
    ["https://mangapill.com", "/search?q=", "/manga/", None, False, None],
    ["https://mangapark.net", "/search?word=", "/title/", None, False, None],
    ["https://flamecomics.me", "/?s=", "https://flamecomics.me/series/", 3, True, None],
    ["https://mangareader.to", "/search?keyword=", r'/.*-[0-9]+$', 2, True, None],
    ["https://mangafire.to", "/filter?keyword=", '/manga/', None, False, None],
    ["https://ww1.mangafreak.me", "/Find/", '/Manga/', None, False, None],

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
    soup = BeautifulSoup(raw_response.text, 'html.parser')
    a_hrefs = soup.find_all("a", attrs=({"href": re.compile("^"+site[2])}))

    for a in a_hrefs:
        print(a.prettify())
    print(soup.prettify())
    # Filter elemen yang punya title (flamescomic, mangareader)
    if(site[4]):
        a_hrefs = [a_href for a_href in a_hrefs if a_href.has_attr('title')]

    # Filter elemen yang bukan manga
    if(site[5] != None):
        a_hrefs = [a_href for a_href in a_hrefs if a_href.find(attrs=site[5]) == None]
    a_hrefs = [a_href["href"] for a_href in a_hrefs]

    # Filter link ke halaman bab
    if(site[3] != None): 
        a_hrefs = ["/" + "/".join(PurePosixPath(unquote(urlparse(a_href).path)).parts[1:site[3]]) for a_href in a_hrefs]
    a_hrefs = list(set(a_hrefs))[0:limit]

    for a_href in a_hrefs:
      results.append(site[0] + a_href)
    
    print(site[0])

# Comick memakai JS untuk meload data, sehingga perlu diolah terpisah dengan playwright
async def comick(title):
    async with async_playwright() as playwright:
        playwright_version = str(subprocess.getoutput("playwright --version")).strip().split(" ")[1]
        capabilities["LT:Options"]["playwrightClientVersion"] = playwright_version
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://comick.io/search?q=" + title_url(title))
        
        loaded = page.locator("id=__next")
        outerHTML = await loaded.evaluate("el => el.outerHTML")
        soup = BeautifulSoup("".join(outerHTML), 'html.parser')
        a_hrefs = soup.find_all("a", attrs=({"href": re.compile("^/comic/")}))
        
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

    print("https://mangadex.org")

def title_url(title):
    return urllib.parse.quote_plus(title)

limit = 999

async def search(title):
    await asyncio.gather(
        # mangadex(title), 
        # request(sites[1], title),
        # request(sites[2], title),
        # request(sites[3], title),
        # request(sites[4], title),
        # request(sites[5], title),
        # request(sites[6], title),
        # request(sites[7], title),
    )
    for result in results:
        print(result)


if __name__ == "__main__":
    title = input("Search for: ")
    asyncio.run(search(title.replace(" ", "+")))