import requests
import json
import os
import shortuuid
import xml.etree.ElementTree as ET
from typing import List
from bs4 import BeautifulSoup
from langdetect import detect

class WebScapper:

    def __init__(self, folder_path: str ) -> None:

        files = [f for f in os.listdir(folder_path)]
        for file in files:
            file_urls = []

            # Collect all the urls from the sitemap files excluding the pdf files
            with open(os.path.join(folder_path, file), 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if "loc" in line and ".pdf" not in line:
                        line = line.replace("<loc>", "").replace("</loc>", "").strip() 
                        file_urls.append(line)

            temp_file = file.strip(".xml")
            with open(f"./dataset/{temp_file}.en.jsonl", 'a') as f_en, open(f"./dataset/{temp_file}.it.jsonl", 'a') as f_it:        
                for url in file_urls:
                    doc = self.scrap_webpage(url)  
                    if doc:
                        if doc["lang"] == "en":
                            f_en.write(json.dumps(doc) + "\n")
                        elif doc["lang"] == "it":
                            f_it.write(json.dumps(doc) + "\n")

    
    def scrap_webpage(self, url: str ) -> dict or None:

        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')

            meta_desc = soup.find("meta", attrs={"name": "description"})

            title = soup.title.string
            description = meta_desc['content'] if meta_desc else ""
            url = response.url
            text = soup.get_text(separator="\n", strip=True)
            lang = detect(text)
            doc = {
                "doc_id": shortuuid.ShortUUID().random(length=10),
                "title": title,
                "description": description,
                "url": url,
                "lang": lang,
                "text": text
            }
            print(doc)
            return doc

        else:
            print("Error: ", response.status_code)
            return None

if __name__ == "__main__":
    webscrapper = WebScapper("./sitemaps")
