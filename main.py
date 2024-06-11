from bs4 import BeautifulSoup
import aiohttp
import asyncio
import re
import json
import webbrowser
import time
import urllib
import tkinter as tk
import tkhtmlview as tkhtml

# header, bagian search, bagian manga, batasan segment, title filter, filter out, image inside, filter title
# 0 = spesial, 1 = request, 2 = playwright

# buka gambar manga pill perlu referer https://mangapill.com/

async def mangadex(title, session):
# def mangadex(title):
    # Dari docs API https://api.mangadex.org/docs/swagger.html#/Manga/get-search-manga
    # Docs API sikok lagi buruk nian, yang ini biso simulate url
    site = "https://mangadex.org"
    print("Fetching", site)
    async with session.get(f"https://api.mangadex.org/manga?title={title_url(title)}&contentRating%5B%5D=safe&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&order%5Brelevance%5D=desc&hasAvailableChapters=true&includes%5B%5D=cover_art") as response:
        results = []
        r = await response.json()
        for manga in r["data"]:
            title = list(manga['attributes']['title'].values())[0]
            id = manga['id']
            image = [r['attributes']['fileName'] for r in manga['relationships'] if r['type'] == 'cover_art'][0]
            image_url = f"https://uploads.mangadex.org/covers/{id}/{image}.512.jpg"
            results.append(parse_manga(title, f"{site}/title/{id}", image_url))
    print(site, "done")
    return {"site": "MangaDex", "site_url": site, "results": results[0:limit]}

async def asuratoons(title, session):
    site = "https://asuratoon.com"
    print("Fetching", site)
    async with session.get(f"{site}/?s={title_url(title)}") as response:
        raw_response = await response.text()
    soup = BeautifulSoup(raw_response, 'html.parser')
    manga_list = soup.find_all("div", attrs={"class": re.compile("bsx")})

    results = []
    for manga in manga_list:
        a_href = manga.find("a", attrs={"href": re.compile(f"^{site}/manga/"), "title": re.compile(r"\w")})
        img = a_href.img

        manga_title = a_href['title']
        url = a_href['href']
        image_url = img["src"]
        results.append(parse_manga(manga_title, url, image_url))
    print(site, "done")
    return {"site": "AsuraToons", "site_url": site, "results": results[0:limit]}

async def flamecomics(title, session):
    site = "https://flamecomics.me"
    print("Fetching", site)
    async with session.get(f"{site}/?s={title_url(title)}") as response:
        raw_response = await response.text()
    soup = BeautifulSoup(raw_response, 'html.parser')
    manga_list = soup.find_all("div", attrs={"class": re.compile("bsx")})

    results = []
    for manga in manga_list:
        a_href = manga.find("a", attrs={"href": re.compile(f"^{site}/series/"), "title": re.compile(r"\w")})
        img = a_href.img

        manga_title = a_href['title']
        url = a_href['href']
        image_url = img["src"]
        results.append(parse_manga(manga_title, url, image_url))
    print(site, "done")
    return {"site": "FlameComics", "site_url": site, "results": results[0:limit]}

async def mangapill(title, session):
    site = "https://mangapill.com"
    print("Fetching", site)
    async with session.get(f"{site}/search?q={title_url(title)}&type=&status=") as response:
        raw_response = await response.text()
    soup = BeautifulSoup(raw_response, 'html.parser')
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
    print(site, "done")
    return {"site": "MangaPill", "site_url": site, "results": results[0:limit]}

async def mangapark(title, session):
    site = "https://mangapark.net"
    print("Fetching", site)
    async with session.get(f"{site}/search?word={title_url(title)}") as response:
        raw_response = await response.text()
    soup = BeautifulSoup(raw_response, 'html.parser')
    manga_list = soup.find_all("img", attrs={"title": re.compile(r"\w")})

    results = []
    for manga in manga_list:
        a_href = manga.parent

        manga_title = manga['title']
        url = a_href['href']
        image_url = manga['src']
        results.append(parse_manga(manga_title, url, image_url))
    print(site, "done")
    return {"site": "MangaPark", "site_url": site, "results": results[0:limit]}

async def mangareader(title, session):
    site = "https://mangareader.to"
    print("Fetching", site)
    async with session.get(f"{site}/search?keyword={title_url(title)}") as response:
        raw_response = await response.text()
    soup = BeautifulSoup(raw_response, 'html.parser')
    manga_list = soup.find_all("div", attrs={"class": re.compile("item item-spc")})

    results = []
    for manga in manga_list:
        a_href = manga.find('a', attrs={"title": re.compile(r"\w")})
        img = manga.img

        manga_title = a_href.string
        url = a_href['href']
        image_url = img['src']
        results.append(parse_manga(manga_title, url, image_url))
    print(site, "done")
    return {"site": "MangaReader", "site_url": site, "results": results[0:limit]}

async def mangafire(title, session):
    site = "https://mangafire.to"
    print("Fetching", site)
    async with session.get(f"{site}/filter?keyword={title_url(title)}") as response:
        raw_response = await response.text()
    soup = BeautifulSoup(raw_response, 'html.parser')
    manga_list = soup.find_all("div", attrs={"class": re.compile("unit item")})

    results = []
    for manga in manga_list:
        a_href = manga.find('div', attrs={"class": re.compile("info")}).find('a', attrs={"href": re.compile("/manga/")})
        img = manga.img

        manga_title = a_href.string
        url = a_href['href']
        image_url = img['src']
        results.append(parse_manga(manga_title, url, image_url))
    print(site, "done")
    return {"site": "MangaFire", "site_url": site, "results": results[0:limit]}
    
async def mangafreak(title, session):
    site = "https://ww1.mangafreak.me"
    print("Fetching", site)
    async with session.get(f"{site}/Find/{title_url(title)}") as response:
        raw_response = await response.text()
    soup = BeautifulSoup(raw_response, 'html.parser')
    manga_list = soup.find_all("div", attrs={"class": re.compile("manga_search_item")})

    results = []
    for manga in manga_list:
        a_href = manga.h3.find('a', attrs={"href": re.compile("/Manga/")})
        img = manga.img

        manga_title = a_href.string
        url = a_href['href']
        image_url = img['src']
        results.append(parse_manga(manga_title, url, image_url))
    print(site, "done")
    return {"site": "MangaFreak", "site_url": site, "results": results[0:limit]}

def title_url(title):
    return urllib.parse.quote_plus(title)

def parse_manga(title, url, image):
    return {"title": title, "url": url, "image": image}

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
#         mangafire(title),
#         mangafreak(title),
#     )
#     for result in results:
#         print(result['site'])
#         for index, manga in enumerate(result['results']):
#             print(f"{index+1}.\t{manga['title']}")

async def aggregate(title):
    global canvas
    async with aiohttp.ClientSession() as session:
        funcs = [
            mangadex, asuratoons, mangapill, mangapark,
            flamecomics, mangareader, mangafire, mangafreak
        ]
        tasks = [
            asyncio.create_task(coro=search_site(f, title, session)) for f in funcs
        ]
        await asyncio.gather(*tasks, return_exceptions=False)

def search():
    global content_frame
    for child in content_frame.winfo_children(): child.destroy()
    title = title_variable.get()
    asyncio.run(aggregate(title))
    
async def search_site(func, title, session):
    global content_frame, canvas

    results = await func(title, session)
    site_frame = tk.Frame(content_frame, padx=5)
    site_frame.pack(fill=tk.X, side=tk.TOP)
    site_frame.grid_rowconfigure(1, weight=1, uniform='site_frame_row')
    
    site_label = tk.Label(site_frame, padx=5, text=results['site'], font=("Segoe UI", 11, "italic"))
    site_label.grid(column=0, row=0, sticky='W', pady=10)

    site_result = tk.Frame(site_frame)
    site_result.grid(column=0, row=1, sticky='WE')

    for result in results['results']:
        manga = tk.Frame(site_result)
        manga.pack(fill=tk.X, side=tk.TOP)
        manga.grid_columnconfigure(1, weight=1, uniform='manga_col')

        manga_image = tkhtml.HTMLLabel(manga, html=f"<img src={result['image']} height='80' width='60'>", width=10, height=5)
        manga_image.grid(column=0, row=0, sticky='WENS')

        manga_title = tk.Label(manga, text=result['title'], anchor='nw', font=("Segoe UI", 11, "normal"))
        manga_title.grid(column=1, row=0, sticky='WE')

        manga.bind("<Button-1>", lambda e, url=result['url']: webbrowser.open_new_tab(url))
        manga_image.bind("<Button-1>", lambda e, url=result['image']: webbrowser.open_new_tab(url))
        manga_title.bind("<Button-1>", lambda e, url=result['url']: webbrowser.open_new_tab(url))

def main():
    global content_frame, canvas
    root.geometry('800x600')
    root.grid_columnconfigure(0, weight=1, uniform='root_col')
    root.grid_rowconfigure(0, weight=1, uniform='root_row')

    app_frame = tk.Frame(root, height=600, width=800, borderwidth=2, relief='groove')
    app_frame.grid(sticky='WENS')
    app_frame.grid_columnconfigure(1, weight=1, uniform='app_frame_col')
    app_frame.grid_rowconfigure(0, pad=2, weight=1, uniform='app_frame_row')
    
    # Side Frame
    side_frame = tk.Frame(app_frame, padx=5, pady=5, borderwidth=2, relief='groove')
    side_frame.grid(column=0, row=0, sticky='NS')

    search_label = tk.Label(side_frame, padx=5, pady=10, text="Search", font=("Segoe UI", 12))
    search_label.grid(column=0, row=0,sticky="WN")

    search_entry = tk.Entry(side_frame, textvariable=title_variable)
    search_entry.grid(column=0, row=1, sticky="WEN")

    search_button = tk.Button(side_frame, padx=5, text="Search", command=search)
    search_button.grid(column=0, row=2, sticky='EN', pady=5)

    # Main Frame
    main_frame = tk.Frame(app_frame, relief='groove')
    main_frame.grid(column=1, row=0, sticky="WENS")
    main_frame.grid_columnconfigure(0, weight=1, uniform="main_frame_col")
    main_frame.grid_rowconfigure(1, weight=1, uniform='main_frame_row')

    # Top Frame
    top_frame = tk.Frame(main_frame, padx=20, pady=10, borderwidth=2, relief='groove')
    top_frame.grid(column=0, row=0, columnspan=2, sticky='WEN')
    top_frame.grid_columnconfigure(0, weight=1, uniform='top_frame_col')

    results_label = tk.Label(top_frame, text="Results:", font=("Segoe UI", 12))
    results_label.grid(column=0, row=0, sticky='W')

    about_button = tk.Button(top_frame, text="MA", width=5, command=search)
    about_button.grid(column=1, row=0, sticky='E')

    # Content Frame
    canvas = tk.Canvas(main_frame, borderwidth=2, relief='groove')
    canvas.grid(column=0, row=1, sticky='WENS')
    scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.grid(column=1, row=1, sticky='NS')
    canvas.configure(yscrollcommand=scrollbar.set)
    content_frame = tk.Frame(canvas, padx=10)
    content_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0,0), window=content_frame, anchor='nw')

    root.mainloop()

limit = 5

if __name__ == "__main__":
    root = tk.Tk()
    title_variable = tk.StringVar()
    main()
    # title = input("Search for: ")
    # asyncio.run(search(title.replace(" ", "+")))