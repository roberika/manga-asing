pushd "%~dp0"
py -m pip install virtualenv
py -m venv mangaasing
call .\mangaasing\Scripts\activate.bat
py -m pip install beautifulsoup4
py -m pip install asyncio
py -m pip install aiohttp
py -m pip install requests
py -m pip install tkhtmlview==0.2.0
py -m pip install pillow==9.5.0
set /p asd="Press Enter to continue..."
