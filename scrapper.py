import os
import requests
import zipfile
import random
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.core.window import Window

class WebScraperApp(App):
    def build(self):
        Window.size = (600, 400)
        Window.clearcolor = (0.95, 0.95, 0.97, 1)
        self.downloaded_files = []
        return MainLayout()

class MainLayout(BoxLayout):
    progress_value = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=20)
        self.scraper = cloudscraper.create_scraper()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        self.setup_ui()

    def setup_ui(self):
        self.add_widget(Label(
            text="Web Scraper",
            font_size=32,
            color=(0.2, 0.2, 0.2, 1),
            bold=True
        ))

        self.url_input = TextInput(
            hint_text="Enter website URL",
            size_hint=(1, 0.2),
            font_size=18,
            background_color=(1, 1, 1, 1),
            foreground_color=(0.3, 0.3, 0.3, 1),
            cursor_color=(0, 0.5, 1, 1),
            padding=[10, 10]
        )
        self.add_widget(self.url_input)

        self.start_button = Button(
            text="Start Scraping",
            size_hint=(1, 0.2),
            background_color=(0.1, 0.6, 0.9, 1),
            background_normal="",
            color=(1, 1, 1, 1),
            font_size=18
        )
        self.start_button.bind(on_press=self.start_scraping)
        self.add_widget(self.start_button)

        self.progress_bar = ProgressBar(
            max=100,
            value=self.progress_value,
            size_hint=(1, 0.1)
        )
        self.add_widget(self.progress_bar)

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, color=(0.2, 0.2, 0.2, 1)),
            size_hint=(0.8, 0.4),
            auto_dismiss=True
        )
        popup.open()

    def start_scraping(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.show_popup("Warning", "Please enter a URL!")
            return
        
        self.start_button.disabled = True
        Clock.schedule_once(lambda dt: self.scrape_website(url), 0.1)

    def get_headers(self):
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive"
        }

    def scrape_with_selenium(self, url):
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={random.choice(self.user_agents)}")
        options.add_argument("--headless")  # Run without opening a browser window
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        try:
            driver.get(url)
            time.sleep(5)  # Wait for JavaScript to load
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            return soup
        finally:
            driver.quit()

    def scrape_website(self, url):
        # Try cloudscraper first
        try:
            response = self.scraper.get(url, headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            self.show_popup("Info", f"Cloudscraper failed ({e}), switching to Selenium...")
            soup = self.scrape_with_selenium(url)
            if not soup:
                self.show_popup("Error", "Failed to scrape with Selenium too!")
                self.start_button.disabled = False
                return

        download_dir = os.path.join(os.getcwd(), "scraped_files")
        os.makedirs(download_dir, exist_ok=True)
        self.downloaded_files = []

        html_path = os.path.join(download_dir, "source.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        self.downloaded_files.append(html_path)

        all_links = self.collect_links(soup, url)
        self.progress_bar.max = len(all_links)

        for i, link in enumerate(tqdm(all_links, desc="Downloading", leave=False)):
            self.download_file(link, download_dir)
            self.progress_value = i + 1
            Clock.schedule_once(lambda dt: setattr(self.progress_bar, "value", self.progress_value), 0)
            time.sleep(random.uniform(0.5, 1.5))

        self.create_zip(download_dir)
        self.save_info(soup, url, download_dir, len(all_links))
        self.show_popup("Success", "Scraping completed!")
        self.start_button.disabled = False
        self.progress_value = 0

    def collect_links(self, soup, base_url):
        links = []
        for tag in soup.find_all(["link", "script", "img"]):
            src = tag.get("href") if tag.name == "link" else tag.get("src")
            if src:
                links.append(urljoin(base_url, src))
        return links

    def download_file(self, file_url, download_dir):
        try:
            filename = os.path.basename(file_url)
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            if not filename:
                return
            
            file_path = os.path.join(download_dir, filename)
            response = self.scraper.get(file_url, headers=self.get_headers(), timeout=5)
            response.raise_for_status()
            
            with open(file_path, "wb") as f:
                f.write(response.content)
            self.downloaded_files.append(file_path)
        except requests.RequestException:
            pass

    def create_zip(self, download_dir):
        zip_path = os.path.join(download_dir, "downloaded_files.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file in self.downloaded_files:
                zipf.write(file, os.path.relpath(file, download_dir))

    def save_info(self, soup, url, download_dir, link_count):
        title = soup.title.string if soup.title else "No title found"
        file_count = len(self.downloaded_files)
        complexity = ("simple" if file_count < 5 else 
                     "moderate" if file_count < 15 else "complex")

        info_path = os.path.join(download_dir, "website_info.txt")
        with open(info_path, "w", encoding="utf-8") as f:
            f.write(f"Website Title: {title}\n")
            f.write(f"Website URL: {url}\n")
            f.write(f"Collected Links: {link_count}\n")
            f.write(f"Downloaded Files: {file_count}\n")
            f.write(f"Complexity Level: {complexity}\n")

if __name__ == "__main__":
    WebScraperApp().run()
