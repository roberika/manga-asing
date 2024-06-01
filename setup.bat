pushd "%~dp0"
py -m pip install virtualenv
py -m venv mangaasing
call .\mangaasing\Scripts\activate.bat
set /p asd="Press Enter to continue..."
py -m pip install playwright
py -m pip install beautifulsoup4
py -m pip install asyncio
py -m pip install requests
set /p asd="Press Enter to continue..."
playwright install
