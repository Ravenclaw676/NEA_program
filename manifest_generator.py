import requests
import re
import os
import json
import PyPDF2


def download_pdf(URL: str, manifest: list) -> list:
    """uses the requests library to download the PDF specified in the URL"""
    if os.path.exists("./faction_pdfs/" + URL[63:83]):
        print(f"{URL[63:83]} has already been downloaded")
        manifest.append(URL[63:83])
        return manifest

    response = requests.get(URL)
    faction_pdf = open("./faction_pdfs/" + URL[63:83], "xb")
    faction_pdf.write(response.content)
    print(f"{URL[63:83]} was successfully downloaded")
    faction_pdf.close()
    pdf = PyPDF2.PdfReader("./faction_pdfs/" + URL[63:83])
    if re.findall("Warhammer 40,000", pdf.pages[0].extract_text()):
        os.remove("./faction_pdfs/" + URL[63:83])
        print("file has been deleted")
    else:
        manifest.append(URL[63:83])
    return manifest


def download_pdfs() -> list:
    # the google cache version of the site is used because the real site has a DDOS prrot
    URL = "https://webcache.googleusercontent.com/search?q=cache:https://www.warhammer-community.com/warhammer-40000-downloads/"
    HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
    response = requests.get(URL, headers=HEADERS)
    text = response.text
    matchs = re.findall('''"resources-button" href="(.+)" ?(?=target=".+)''', text)
    matchs = matchs[4:72]
    manifest = []
    for match in matchs:
        manifest = download_pdf(match, manifest)

    with open("./faction_pdfs/manifest.json", "w") as manifest_json:
        json.dump(manifest, manifest_json)

    return manifest
