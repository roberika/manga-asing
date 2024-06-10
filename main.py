from typing import Any, Awaitable, Callable
from bs4 import BeautifulSoup
import requests
import asyncio
import random
import json
import time
import re
import json
import logging
import webbrowser
import os
import subprocess
import sys
import time
import urllib
from tkinter import *
from urllib.parse import unquote, urlparse
from urllib.request import urlopen
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

# [
#     {
#         "site": str,
#         "site_url": str
#         "results": [
#             "title": str,
#             "url": str,
#             "image":str
#         ]
#     }
# ]

# async def search(title):
#     results = await asyncio.gather(
#         mangadex(title), 
#         asuratoons(title),
#         mangapill(title),
#         mangapark(title),
#         flamecomics(title),
#         mangareader(title),
#         mangafreak(title),
#     )
#     for result in results:
#         print(result['site'])
#         for index, manga in enumerate(result['results']):
#             print(f"{index+1}.\t{manga['title']}")

def search():
    title = title_variable.get()
    asyncio.run(search_site(mangadex, title))
    asyncio.run(search_site(asuratoons, title))
    asyncio.run(search_site(mangapill, title))
    asyncio.run(search_site(mangapark, title))
    asyncio.run(search_site(flamecomics, title))
    asyncio.run(search_site(mangareader, title))
    asyncio.run(search_site(mangafreak, title))

def open_url(url):
    webbrowser.open(url, new=2)

async def search_site(func, title):
    global content_frame, canvas
    results = await func(title)
    site_frame = Frame(content_frame, padx=5, pady=5)
    site_frame.pack(fill=X, side=TOP)
    site_frame.grid_rowconfigure(1, weight=1, uniform='site_frame_row')
    
    site_label = Label(site_frame, padx=5, pady=0, text=results['site'])
    site_label.grid(column=0, row=0, sticky='W')

    site_result = Frame(site_frame)
    site_result.grid(column=0, row=1, sticky='WE')

    for result in results['results']:
        u = urlopen(result['image'])
        raw_image = u.read()
        u.close()

        manga = Frame(site_result)
        manga.pack(fill=X, side=TOP)
        manga.grid_columnconfigure(1, weight=1, uniform='manga_col')

        # manga_image = Label(manga, image=raw_image, padx=5, pady=5)
        manga_image = Label(manga, text="Empty", padx=5, pady=5)
        manga_image.grid(column=0, row=0, sticky='WE')

        manga_title = Label(manga, text=result['title'])
        manga_title.grid(column=1, row=0, sticky='W')

    root.geometry('800x600')

def main():
    global content_frame, canvas
    root.geometry('799x599')
    root.grid_columnconfigure(0, weight=1, uniform='root_col')
    root.grid_rowconfigure(0, weight=1, uniform='root_row')

    app_frame = Frame(root, height=600, width=800, borderwidth=2, relief='groove')
    app_frame.grid(sticky='WENS')
    app_frame.grid_columnconfigure(1, weight=1, uniform='app_frame_col')
    app_frame.grid_rowconfigure(0, weight=1, uniform='app_frame_row')
    
    # Side Frame
    side_frame = Frame(app_frame, padx=20, pady=20, borderwidth=2, relief='groove')
    side_frame.grid(column=0, row=0, sticky='NS')

    search_label = Label(side_frame, text="Search")
    search_label.grid(column=0, row=0,sticky="WN")

    search_entry = Entry(side_frame, textvariable=title_variable)
    search_entry.grid(column=0, row=1, sticky="WEN")

    search_button = Button(side_frame, text="Search", command=search)
    search_button.grid(column=0, row=2, sticky='EN')

    # Main Frame
    main_frame = Frame(app_frame, relief='groove')
    main_frame.grid(column=1, row=0, sticky="WENS")
    main_frame.grid_columnconfigure(0, weight=1, uniform="main_frame_col")
    main_frame.grid_rowconfigure(1, weight=1, uniform='main_frame_row')

    # Top Frame
    top_frame = Frame(main_frame, padx=20, pady=5, borderwidth=2, relief='groove')
    top_frame.grid(column=0, row=0, columnspan=2, sticky='WEN')
    top_frame.grid_columnconfigure(0, weight=1, uniform='top_frame_col')

    results_label = Label(top_frame, text="Results:")
    results_label.grid(column=0, row=0, sticky='W')

    about_button = Button(top_frame, text="MA", width=5, command=search)
    about_button.grid(column=1, row=0, sticky='E')

    # Content Frame
    canvas = Canvas(main_frame)
    canvas.grid(column=0, row=1, sticky='WENS')
    scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
    scrollbar.grid(column=1, row=1, sticky='NS')
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    content_frame = Frame(canvas, padx=10, pady=10)
    content_frame.grid(column=0, row=1, sticky='WENS')
    canvas.create_window((0,0), window=content_frame, anchor='nw')

    root.mainloop()

if __name__ == "__main__":
    root = Tk()
    title_variable = StringVar()
    main()
    # title = input("Search for: ")
    # asyncio.run(search(title.replace(" ", "+")))