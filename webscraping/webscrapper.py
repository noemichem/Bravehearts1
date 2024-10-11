import requests
from typing import List
from bs4 import BeautifulSoup

class WebScapper:
    
    urls = []

    def __init__(self, url: str, urls: List[str] | None ) -> None:
        if urls is None:
            self.urls.append(url)
        else:
            self.urls =  urls.append(url)

    def get_urls(self) -> List[str]:
        return self.urls

    def start_scraping(self) -> None:
        for url in self.urls:
            self.scrap_webpage(url)
    
    def scrap_webpage(self, url: str) -> None:
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            # Extracting the title
            title = soup.title.string
            print(f"Title: {title}")

            # # Extracting meta description
            # meta_desc = soup.find("meta", attrs={"name": "description"})
            # if meta_desc:
            #     print(f"Meta Description: {meta_desc['content']}")
            print(soup.get_text(separator="\n", strip=True))

        else:
            print("Error: ", response.status_code)

if __name__ == "__main__":
    url = "https://www.unipi.it/index.php/tuition-fees-and-financial-support/item/13589-tuition-fees-reduction"
    webscrapper = WebScapper(url, None)
    webscrapper.start_scraping()