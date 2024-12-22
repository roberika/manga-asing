## Web Access
import aiohttp
import webbrowser

## Paralellism
import threading
import asyncio

## Utils
from bs4 import BeautifulSoup
import re
import time
import urllib

## UI
import tkinter as tk
import tkhtmlview as tkhtml

async def mangadex(title, session):
# def mangadex(title):
    # Dari docs API https://api.mangadex.org/docs/swagger.html#/Manga/get-search-manga
    # Docs API sikok lagi buruk nian, yang ini biso simulate url
    site = "https://mangadex.org"
    print("Fetching", site, "\t", time.perf_counter() - time_start)
    try:
        async with session.get(f"https://api.mangadex.org/manga?title={title_url(title)}&contentRating%5B%5D=safe&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&order%5Brelevance%5D=desc&hasAvailableChapters=true&includes%5B%5D=cover_art") as response:
            results = []
            r = await response.json()
            for manga in r["data"]:
                title = list(manga['attributes']['title'].values())[0]
                id = manga['id']
                image = [r['attributes']['fileName'] for r in manga['relationships'] if r['type'] == 'cover_art'][0]
                image_url = f"https://uploads.mangadex.org/covers/{id}/{image}.512.jpg"
                results.append(parse_manga(title, f"{site}/title/{id}", image_url))
        print(site, "done", "\t", time.perf_counter() - time_start)
        return {"site": "MangaDex", "site_url": site, "results": results[0:limit]}
    except asyncio.exceptions.TimeoutError as e:
        print(site, "timed out", "\t", time.perf_counter() - time_start)
        return None

async def asuratoons(title, session):
    site = "https://asuratoon.com"
    print("Fetching", site, "\t", time.perf_counter() - time_start)
    try:
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
        print(site, "done", "\t", time.perf_counter() - time_start)
        return {"site": "AsuraToons", "site_url": site, "results": results[0:limit]}
    except asyncio.exceptions.TimeoutError as e:
        print(site, "timed out", "\t", time.perf_counter() - time_start)
        return None

async def flamecomics(title, session):
    site = "https://flamecomics.me"
    print("Fetching", site, "\t", time.perf_counter() - time_start)
    try:
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
        print(site, "done", "\t", time.perf_counter() - time_start)
        return {"site": "FlameComics", "site_url": site, "results": results[0:limit]}
    except asyncio.exceptions.TimeoutError as e:
        print(site, "timed out", "\t", time.perf_counter() - time_start)
        return None

async def mangapill(title, session):
    site = "https://mangapill.com"
    print("Fetching", site, "\t", time.perf_counter() - time_start)
    try:
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
        print(site, "done", "\t", time.perf_counter() - time_start)
        return {"site": "MangaPill", "site_url": site, "results": results[0:limit]}
    except asyncio.exceptions.TimeoutError as e:
        print(site, "timed out", "\t", time.perf_counter() - time_start)
        return None

async def mangapark(title, session):
    site = "https://mangapark.net"
    print("Fetching", site, "\t", time.perf_counter() - time_start)
    try:
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
        print(site, "done", "\t", time.perf_counter() - time_start)
        return {"site": "MangaPark", "site_url": site, "results": results[0:limit]}
    except asyncio.exceptions.TimeoutError as e:
        print(site, "timed out", "\t", time.perf_counter() - time_start)
        return None

async def mangareader(title, session):
    site = "https://mangareader.to"
    print("Fetching", site, "\t", time.perf_counter() - time_start)
    try:
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
        print(site, "done", "\t", time.perf_counter() - time_start)
        return {"site": "MangaReader", "site_url": site, "results": results[0:limit]}
    except asyncio.exceptions.TimeoutError as e:
        print(site, "timed out", "\t", time.perf_counter() - time_start)
        return None

async def mangafire(title, session):
    site = "https://mangafire.to"
    print("Fetching", site, "\t", time.perf_counter() - time_start)
    try:
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
        print(site, "done", "\t", time.perf_counter() - time_start)
        return {"site": "MangaFire", "site_url": site, "results": results[0:limit]}
    except asyncio.exceptions.TimeoutError as e:
        print(site, "timed out", "\t", time.perf_counter() - time_start)
        return None
    
async def mangafreak(title, session):
    site = "https://ww1.mangafreak.me"
    print("Fetching", site, "\t", time.perf_counter() - time_start)
    try:
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
        print(site, "done", "\t", time.perf_counter() - time_start)
        return {"site": "MangaFreak", "site_url": site, "results": results[0:limit]}
    except asyncio.exceptions.TimeoutError as e:
        print(site, "timed out", "\t", time.perf_counter() - time_start)
        return None

def title_url(title):
    return urllib.parse.quote_plus(title)

def parse_manga(title, url, image):
    return {"title": title, "url": url, "image": image}

def flip_selection():
    target = (mdex.get() + 1) % 2
    vals = [mdex, asurat, mpill, mpark, flamec, mreader, mfire, mfreak]
    for val in vals:
        val.set(target)

async def aggregate(title):
    session_timeout = aiohttp.ClientTimeout(total=None,sock_connect=timeout,sock_read=timeout)
    async with aiohttp.ClientSession(timeout=session_timeout) as session:
        funcs = []
        if mdex.get() == 0    :funcs.append(mangadex)
        if asurat.get() == 0  :funcs.append(asuratoons)
        if mpill.get() == 0   :funcs.append(mangapill)
        if mpark.get() == 0   :funcs.append(mangapark)
        if flamec.get() == 0  :funcs.append(flamecomics)
        if mreader.get() == 0 :funcs.append(mangareader)
        if mfire.get() == 0   :funcs.append(mangafire)
        if mfreak.get() == 0  :funcs.append(mangafreak)
        tasks = [
            asyncio.create_task(coro=display(func, title, session)) for func in funcs
        ]
        await asyncio.gather(*tasks, return_exceptions=False)

def search():
    global time_start
    time_start = time.perf_counter()
    for child in content_frame.winfo_children(): child.destroy()
    title = title_variable.get()
    asyncio.run(aggregate(title))
    content_frame.config(width=600)
    root.geometry('800x600')
    
async def display(func, title, session):
    results = await func(title, session)
    if results == None : return

    print("Appending", results['site'], "\t", time.perf_counter() - time_start)
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
        manga.grid_columnconfigure(1, weight=1, uniform='manga_column')

        manga_image = tkhtml.HTMLLabel(manga, html=f"<img src={result['image']} height='80' width='60'>", width=10, height=5)
        manga_image.grid(column=0, row=0, sticky='WENS')

        manga_title = tk.Message(manga, text=result['title'], anchor='nw', font=("Segoe UI", 11, "normal"), width=500)
        manga_title.grid(column=1, row=0, sticky='WEN', pady=5)

        manga.bind("<Button-1>", lambda e, url=result['url']: webbrowser.open_new_tab(url))
        manga_image.bind("<Button-1>", lambda e, url=result['image']: webbrowser.open_new_tab(url))
        manga_title.bind("<Button-1>", lambda e, url=result['url']: webbrowser.open_new_tab(url))
    print(results['site'], "displayed", "\t", time.perf_counter() - time_start)

def main():
    global content_frame, canvas
    root.geometry('600x600')
    root.grid_columnconfigure(0, weight=1, uniform='root_col')
    root.grid_rowconfigure(0, weight=1, uniform='root_row')

    app_frame = tk.Frame(root, borderwidth=2, relief='groove')
    app_frame.grid(sticky='WENS')
    app_frame.grid_columnconfigure(1, weight=1, uniform='app_frame_col')
    app_frame.grid_rowconfigure(0, pad=2, weight=1, uniform='app_frame_row')
    
    # Side Frame
    side_frame = tk.Frame(app_frame, padx=5, pady=5, borderwidth=2, relief='groove')
    side_frame.grid(column=0, row=0, sticky='NS')

    ## Search
    search_label = tk.Label(side_frame, padx=5, pady=10, text="Search", font=("Segoe UI", 12))
    search_label.pack(fill=tk.NONE, anchor='nw')

    search_entry = tk.Entry(side_frame, textvariable=title_variable)
    search_entry.pack(fill=tk.X, side=tk.TOP, pady=5)

    search_button = tk.Button(side_frame, padx=5, text="Search", 
        command=lambda: threading.Thread(target=search).start())
    search_button.pack(fill=tk.NONE, anchor='ne', pady=10)

    ## Manga Site selector
    manga_label = tk.Label(side_frame, padx=5, pady=10, text="Manga Sites", font=("Segoe UI", 12))
    manga_label.pack(fill=tk.NONE, anchor='nw')

    names = ["Mangadex", "Asuratoons", "Mangapill", "Mangapark", 
             "Flamecomics", "Mangareader", "Mangafire", "Mangafreak"]
    vals = [mdex, asurat, mpill, mpark, flamec, mreader, mfire, mfreak]
    for name, val in zip(names, vals):
        site_check_box = tk.Checkbutton(side_frame, text=name, variable=val, onvalue=0, offvalue=1)
        site_check_box.pack(fill=tk.NONE, anchor='nw')

    flip_button = tk.Button(side_frame, padx=5, text="Check All", command=flip_selection)
    flip_button.pack(fill=tk.NONE, anchor='ne', pady=10)

    # Main Frame
    main_frame = tk.Frame(app_frame, relief='groove')
    main_frame.grid(column=1, row=0, sticky="WENS")
    main_frame.grid_columnconfigure(0, weight=1, uniform="main_frame_col")
    main_frame.grid_rowconfigure(1, weight=1, uniform='main_frame_row')

    # Top Frame
    top_frame = tk.Frame(main_frame, borderwidth=2, relief='groove')
    top_frame.grid(column=0, row=0, columnspan=2, sticky='WEN')
    top_frame.grid_columnconfigure(0, weight=1, uniform='top_frame_col')

    results_label = tk.Label(top_frame, text="Results:", font=("Segoe UI", 12))
    results_label.grid(column=0, row=0, sticky='W', pady=10, padx=10)

    about_button = tkhtml.HTMLLabel(top_frame, html=f"<a href='https://github.com/roberika/manga-asing'><img src='https://raw.githubusercontent.com/roberika/dataset/main/logo-mangaasingicon.ico' height='30' width='30'></a>", width=4, height=2)
    about_button.grid(column=1, row=0, sticky='E')

    # Content Frame
    canvas = tk.Canvas(main_frame)
    canvas.grid(column=0, row=1, sticky='WENS')
    scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.grid(column=1, row=1, sticky='NS')
    canvas.configure(yscrollcommand=scrollbar.set)
    content_frame = tk.Frame(canvas, padx=10)
    content_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0,0), window=content_frame, anchor='nw')

    root.mainloop()

async def baseline():
    global time_start
    time_start = time.perf_counter()
    print("Running scraping sequentially")
    session_timeout = aiohttp.ClientTimeout(total=None,sock_connect=timeout,sock_read=timeout)
    async with aiohttp.ClientSession(timeout=session_timeout) as session:
        funcs = [mangadex, asuratoons, mangapill, mangapark, flamecomics, mangareader, mangafire, mangafreak]
        for func in funcs:
            await func("isekai", session)

async def asyncline():
    global time_start
    time_start = time.perf_counter()
    print("Running scraping asynchronously")
    session_timeout = aiohttp.ClientTimeout(total=None,sock_connect=timeout,sock_read=timeout)
    async with aiohttp.ClientSession(timeout=session_timeout) as session:
        funcs = [mangadex, asuratoons, mangapill, mangapark, flamecomics, mangareader, mangafire, mangafreak]
        tasks = [asyncio.create_task(coro=func("isekai", session)) for func in funcs]
        await asyncio.gather(*tasks, return_exceptions=False)

limit = 5
timeout = 5
time_start = None

if __name__ == "__main__":
    root = tk.Tk(className="manga asing")
    title_variable = tk.StringVar()
    mdex = tk.IntVar()
    asurat = tk.IntVar()
    mpill = tk.IntVar()
    mpark = tk.IntVar()
    flamec = tk.IntVar()
    mreader = tk.IntVar()
    mfire = tk.IntVar()
    mfreak = tk.IntVar()
    main()