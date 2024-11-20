import requests
from bs4 import BeautifulSoup

from models import Season, Episode, Show, ShowsResponse, StreamingService

class StreamingCommunityWorker:
    def __init__(self):
        # autoUrl = requests.get("https://api.matt05.ml/streaming-api/v1/eurostreaming")
        # Get json data
        # self.url = autoUrl.json()["message"]
        self.url = "https://streamingcommunity.computer/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0.1 Safari/605.1.15"
        }
        self.timeout = 5

    def checkStatus(self):
        try:
            r = requests.get(self.url, headers=self.headers,
                             timeout=self.timeout)
            if r.status_code == 200:
                return True
            else:
                return False
        except:
            return False

    def getHome(self):
        # For all .slider-row divs, get the title .row-title and .ssr-title-card
        # CARD: <div data-v-54496308="" data-v-0967ab25="" class="ssr-title-card" style="--a5f83fe4: url(https\:\/\/cdn\.streamingcommunity\.computer\/images\/f29ecafb-8f91-4a95-9d3e-5ea8b6b12d60\.webp); --fe3acb60: url(https\:\/\/cdn\.streamingcommunity\.computer\/images\/30b78d97-21e6-4168-89ff-b66d6642b2e2\.webp);"><a data-v-54496308="" href="https://streamingcommunity.computer/titles/10534-kiff"><!----><div data-v-54496308="" class="boxart"><!----><!----></div><!----></a><!----></div>

        try:
            r = requests.get(self.url, headers=self.headers,
                             timeout=self.timeout)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, "html.parser")
                # Get all .slider-row divs
                sliderRows = soup.find_all("div", class_="slider-row")
                homepage = []
                for sliderRow in sliderRows:
                    categoryTitle = sliderRow.find("span").text

                    categoryShows = []
                    # Get all .ssr-title-card divs
                    titleCards = sliderRow.find_all("div", class_="ssr-title-card")
                    for titleCard in titleCards:
                        url = titleCard.find("a")["href"]
                        id = url.split("/")[-1].split("-")[0]
                        image = titleCard["style"].split("url(")[1].split(")")[0]
                        categoryShows.append(Show(id=id, url=url, image=image))
                    homepage.append(ShowsResponse(category_title=categoryTitle, shows=categoryShows))

                # Remove last element
                homepage.pop()
                return homepage
            else:
                return []
        except Exception as e:
            print(e)
            return []
        
    def getShow(self, url):
        # get title inside .title-container. Title is an image and a span
        # get overview-tab and get all span inside .features 
        # get description from .plot
        # Get show id from url XXXX-title
        show_id = url.split("/")[-1].split("-")[0]

        try:
            r = requests.get(url, headers=self.headers,
                             timeout=self.timeout)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, "html.parser")
                background_images = soup.find("picture", class_="background-image-loader").find_all("source")
                background_images = [img["srcset"] for img in background_images]
                try:
                    logo_image = soup.find("div", class_="title-container").find("img", class_="logo-image")["src"]
                    if logo_image == "":
                        logo_image = None
                except:
                    logo_image = None
                title = soup.find("div", class_="title-container").find("span").text
                image = soup.find("div", class_="title-container").find("img")["src"]

                description = soup.find("div", class_="plot").text
                features = soup.find("div", class_="features").find_all("span")
                features = [f.text for f in features if f.text != "-"]

                # Get exta details
                details = soup.find_all("div", class_="extra")
                details_text = []
                for detail in details:
                    spans = detail.find_all("span")
                    detail_str = ""
                    for span in spans:
                        detail_str += span.text.strip() + " "
                    details_text.append(detail_str.strip())

                return Show(id=show_id, title=title, url=url, title_image=logo_image, image=image, description=description, features=features, details=details_text, background_images=background_images)
            else:
                return Show()
        except Exception as e:
            print(e)
            return Show()
        
    def watchShow(self, show_id, episode_id = None):
        e_string = "?e={episode_id}" if episode_id else ""
        url = f"{self.url}/iframe/{show_id}"
        
        try:
            r = requests.get(url, headers=self.headers,
                             timeout=self.timeout)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, "html.parser")
                # Find iframe and get src
                iframe = soup.find("iframe")
                if iframe:
                    return iframe["src"]
                
            else:
                return ""
        except Exception as e:
            print(e)
            return ""

#worker = StreamingCommunityWorker()
#print(worker.watchShow(9997))
