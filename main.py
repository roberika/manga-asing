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

# header, bagian search, bagian manga, batasan segment, title filter, filter out, image inside, filter title
# 0 = spesial, 1 = request, 2 = playwright

# buka gambar manga pill perlu referer https://mangapill.com/

async def mangadex(title):
# def mangadex(title):
    # Dari docs API https://api.mangadex.org/docs/swagger.html#/Manga/get-search-manga
    # Docs API sikok lagi buruk nian, yang ini biso simulate url
    site = "https://mangadex.org"
    r = requests.get(f"https://api.mangadex.org/manga?title={title_url(title)}&contentRating%5B%5D=safe&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&order%5Brelevance%5D=desc&hasAvailableChapters=true&includes%5B%5D=cover_art")
    
    results = []
    for manga in r.json()["data"]:
        title = list(manga['attributes']['title'].values())[0]
        id = manga['id']
        image = [r['attributes']['fileName'] for r in manga['relationships'] if r['type'] == 'cover_art'][0]
        image_url = f"https://uploads.mangadex.org/covers/{id}/{image}.512.jpg"
        results.append(parse_manga(title, f"{site}/title/{id}", image_url))
    return {"site": "MangaDex", "site_url": site, "results": results[0:limit]}

async def asuratoons(title):
    site = "https://asuratoon.com"
    raw_response = requests.get(f"{site}/?s={title_url(title)}")
    raw_response.encoding = 'utf-8'
    soup = BeautifulSoup(raw_response.text, 'html.parser')
    manga_list = soup.find_all("div", attrs={"class": re.compile("bsx")})

    results = []
    for manga in manga_list:
        a_href = manga.find("a", attrs={"href": re.compile(f"^{site}/manga/"), "title": re.compile(r"\w")})
        img = a_href.img

        manga_title = a_href['title']
        url = a_href['href']
        image_url = img["src"]
        results.append(parse_manga(manga_title, url, image_url))
    return {"site": "Asura Toons", "site_url": site, "results": results[0:limit]}

async def flamecomics(title):
    site = "https://flamecomics.me"
    raw_response = requests.get(f"{site}/?s={title_url(title)}")
    raw_response.encoding = 'utf-8'
    soup = BeautifulSoup(raw_response.text, 'html.parser')
    manga_list = soup.find_all("div", attrs={"class": re.compile("bsx")})

    results = []
    for manga in manga_list:
        a_href = manga.find("a", attrs={"href": re.compile(f"^{site}/series/"), "title": re.compile(r"\w")})
        img = a_href.img

        manga_title = a_href['title']
        url = a_href['href']
        image_url = img["src"]
        results.append(parse_manga(manga_title, url, image_url))
    return {"site": "Flame Comics", "site_url": site, "results": results[0:limit]}

async def mangapill(title):
    site = "https://mangapill.com"
    raw_response = requests.get(f"{site}/search?q={title_url(title)}&type=&status=")
    raw_response.encoding = 'utf-8'
    soup = BeautifulSoup(raw_response.text, 'html.parser')
    manga_list = [a.parent for a in soup.find_all("a", attrs={"href": re.compile("^/manga/")}) if len(a.parent.attrs) == 0]

    results = []
    for manga in manga_list:
        a_href = manga.find("a", attrs={"class": re.compile("mb-2")})
        img = manga.img
        div = a_href.find()

        manga_title = div.string
        url = a_href['href']
        image_url = img['data-src']
        results.append(parse_manga(manga_title, url, image_url))
    return {"site": "MangaPill", "site_url": site, "results": results[0:limit]}

async def mangapark(title):
    site = "https://mangapark.net"
    raw_response = requests.get(f"{site}/search?word={title_url(title)}")
    raw_response.encoding = 'utf-8'
    soup = BeautifulSoup(raw_response.text, 'html.parser')
    manga_list = soup.find_all("img", attrs={"title": re.compile(r"\w")})

    results = []
    for manga in manga_list:
        a_href = manga.parent

        manga_title = manga['title']
        url = a_href['href']
        image_url = manga['src']
        results.append(parse_manga(manga_title, url, image_url))
    return {"site": "MangaPark", "site_url": site, "results": results[0:limit]}

async def mangareader(title):
    site = "https://mangareader.to"
    raw_response = requests.get(f"{site}/search?keyword={title_url(title)}")
    raw_response.encoding = 'utf-8'
    soup = BeautifulSoup(raw_response.text, 'html.parser')
    manga_list = soup.find_all("div", attrs={"class": re.compile("item item-spc")})

    results = []
    for manga in manga_list:
        a_href = manga.find('a', attrs={"title": re.compile(r"\w")})
        img = manga.img

        manga_title = a_href.string
        url = a_href['href']
        image_url = img['src']
        results.append(parse_manga(manga_title, url, image_url))
    return {"site": "MangaReader", "site_url": site, "results": results[0:limit]}

async def mangafire(title):
    site = "https://mangafire.to"
    raw_response = requests.get(f"{site}/filter?keyword={title_url(title)}")
    raw_response.encoding = 'utf-8'
    soup = BeautifulSoup(raw_response.text, 'html.parser')
    manga_list = soup.find_all("div", attrs={"class": re.compile("unit item")})

    results = []
    for manga in manga_list:
        a_href = manga.find('div', attrs={"class": re.compile("info")}).find('a', attrs={"href": re.compile("/manga/")})
        img = manga.img

        manga_title = a_href.string
        url = a_href['href']
        image_url = img['src']
        results.append(parse_manga(manga_title, url, image_url))
    return {"site": "MangaFire", "site_url": site, "results": results[0:limit]}
    
async def mangafreak(title):
    site = "https://ww1.mangafreak.me"
    raw_response = requests.get(f"{site}/Find/{title_url(title)}")
    raw_response.encoding = 'utf-8'
    soup = BeautifulSoup(raw_response.text, 'html.parser')
    manga_list = soup.find_all("div", attrs={"class": re.compile("manga_search_item")})

    results = []
    for manga in manga_list:
        a_href = manga.h3.find('a', attrs={"href": re.compile("/Manga/")})
        img = manga.img

        manga_title = a_href.string
        url = a_href['href']
        image_url = img['src']
        results.append(parse_manga(manga_title, url, image_url))
    return {"site": "MangaFreak", "site_url": site, "results": results[0:limit]}

def title_url(title):
    return urllib.parse.quote_plus(title)

def parse_manga(title, url, image):
    return {"title": title, "url": url, "image": image}

limit = 5

async def search(title):
    results = await asyncio.gather(
        mangadex(title), 
        asuratoons(title),
        mangapill(title),
        mangapark(title),
        flamecomics(title),
        mangareader(title),
        mangafreak(title),
    )
    for result in results:
        print(result['site'])
        for index, manga in enumerate(result['results']):
            print(f"{index+1}.\t{manga['title']}")

if __name__ == "__main__":
    title = input("Search for: ")
    asyncio.run(search(title.replace(" ", "+")))