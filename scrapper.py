import os
import requests
import zipfile
import random
import time
import webbrowser
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
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
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse, Line
from kivy.core.text import LabelBase

# Registriere eine moderne Schriftart (z. B. Roboto)
LabelBase.register(name="Roboto", fn_regular="Roboto-Regular.ttf")

# Setze Vollbildmodus und dunklen Hintergrund
Window.maximize()
Window.clearcolor = (0.02, 0.02, 0.05, 1)

# --- Custom Widgets ---

# NeonButton mit Schatten- und Glow-Effekt
class NeonButton(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        self.button_color = kwargs.pop('button_color', (0, 0.8, 1, 0.8))
        super().__init__(**kwargs)
        self.color = (1, 1, 1, 1)  # Weißer Text
        self.font_size = dp(20)
        self.font_name = "Roboto"
        self.size_hint = (None, None)
        self.size = kwargs.get('size', (dp(180), dp(50)))
        self.halign = "center"
        self.valign = "middle"
        self.bind(size=self.update_graphics, pos=self.update_graphics)
        self.update_graphics()

    def update_graphics(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Schatteneffekt
            Color(0, 0, 0, 0.3)
            RoundedRectangle(pos=(self.x + 5, self.y - 5),
                             size=self.size, radius=[dp(15)])
            # Button mit Neon-Farbverlauf
            Color(*self.button_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(15)])

    def on_press(self):
        Animation(color=(0.8, 1, 1, 1), duration=0.2).start(self)

    def on_release(self):
        Animation(color=(1, 1, 1, 1), duration=0.2).start(self)

# NeonProgressBar mit Glow-Effekt
class NeonProgressBar(ProgressBar):
    def __init__(self, **kwargs):
        self.bg_color = kwargs.pop('bg_color', (0.2, 0.2, 0.2, 0.8))
        self.bar_color = kwargs.pop('bar_color', (0, 0.8, 1, 1))
        super().__init__(**kwargs)
        self.bind(pos=self.update_graphics, size=self.update_graphics, value=self.update_graphics)

    def update_graphics(self, *args):
        self.canvas.before.clear()
        self.canvas.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        with self.canvas:
            Color(*self.bar_color)
            bar_width = self.width * (self.value / self.max)
            RoundedRectangle(pos=self.pos, size=(bar_width, self.height), radius=[dp(8)])
            Color(0, 0.8, 1, 0.3)
            RoundedRectangle(pos=(self.x, self.y - 2), size=(bar_width, self.height + 4), radius=[dp(8)])

# NeonTextInput für ein modernes, abgerundetes Eingabefeld
class NeonTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.1, 0.1, 0.15, 0.9)
        self.foreground_color = (1, 1, 1, 1)
        self.cursor_color = (0, 0.8, 1, 1)
        self.font_size = dp(22)
        self.font_name = "Roboto"
        self.hint_text_color = (0.5, 0.5, 0.5, 1)
        self.padding = [dp(15), dp(15)]
        self.multiline = False
        # Entferne Standard-Hintergründe
        self.background_active = ""
        self.background_normal = ""
        self.bind(focus=self.on_focus_change, pos=self.update_graphics, size=self.update_graphics)
        self.update_graphics()

    def on_focus_change(self, instance, value):
        self.update_graphics()

    def update_graphics(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.1, 0.1, 0.15, 0.9)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
            # Dynamischer Rahmen: helleres Neon bei Fokus
            Color(0, 0.8, 1, 1 if self.focus else 0.7)
            Line(rounded_rectangle=[self.x, self.y, self.width, self.height, dp(10)], width=1.5)

# --- Main Application ---

class WebScraperApp(App):
    def build(self):
        self.downloaded_files = []
        self.is_scraping = False
        return MainLayout()

class MainLayout(FloatLayout):
    progress_value = NumericProperty(0)
    log_text = StringProperty("")
    is_scraping = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scraper = cloudscraper.create_scraper()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/14.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        self.setup_ui()
        self.scraping_links = []
        self.current_url = None
        self.download_dir = None
        # Partikel für dynamischen Hintergrund
        self.particles = []
        self.create_particles()

    def create_particles(self):
        for _ in range(50):
            particle = Ellipse(pos=(random.randint(0, Window.width), random.randint(0, Window.height)),
                               size=(dp(3), dp(3)))
            self.particles.append({
                'ellipse': particle,
                'speed_x': random.uniform(-1, 1),
                'speed_y': random.uniform(-1, 1)
            })
        Clock.schedule_interval(self.update_particles, 1/60)

    def update_particles(self, dt):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.02, 0.02, 0.05, 1)
            Rectangle(pos=(0, 0), size=Window.size)
            Color(0, 0.8, 1, 0.2)
            for particle in self.particles:
                ellipse = particle['ellipse']
                new_x = ellipse.pos[0] + particle['speed_x']
                new_y = ellipse.pos[1] + particle['speed_y']
                if new_x < 0 or new_x > Window.width:
                    particle['speed_x'] *= -1
                if new_y < 0 or new_y > Window.height:
                    particle['speed_y'] *= -1
                ellipse.pos = (new_x, new_y)
                self.canvas.before.add(ellipse)

    def setup_ui(self):
        # Hintergrund
        with self.canvas.before:
            Color(0.02, 0.02, 0.05, 1)
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)

        # Haupt-Container
        main_box = BoxLayout(orientation="vertical", padding=dp(50), spacing=dp(30),
                             size_hint=(0.6, 0.9), pos_hint={'center_x': 0.5, 'center_y': 0.5})

        # Titel
        title_label = Label(text="[b]Web Scraper Pro[/b]", font_size=dp(60),
                            font_name="Roboto", color=(0, 0.8, 1, 1), markup=True, size_hint=(1, 0.1))
        main_box.add_widget(title_label)

        # URL-Eingabe mit NeonTextInput
        url_box = BoxLayout(orientation="horizontal", spacing=dp(15), size_hint=(1, 0.1))
        self.url_input = NeonTextInput(hint_text="Enter website URL (e.g., https://example.com)")
        url_box.add_widget(self.url_input)
        main_box.add_widget(url_box)

        # Einstellungen
        settings_box = GridLayout(cols=2, spacing=dp(20), size_hint=(1, 0.15), padding=dp(10))
        settings_box.add_widget(Label(text="File Types to Scrape:", font_size=dp(20),
                                      font_name="Roboto", color=(0.9, 0.9, 0.9, 1)))
        file_types_box = BoxLayout(orientation="horizontal", spacing=dp(20))
        self.scrape_css = CheckBox(active=True, color=(0, 0.8, 1, 1))
        file_types_box.add_widget(self.scrape_css)
        file_types_box.add_widget(Label(text="CSS", font_name="Roboto", color=(0.9, 0.9, 0.9, 1)))
        self.scrape_js = CheckBox(active=True, color=(0, 0.8, 1, 1))
        file_types_box.add_widget(self.scrape_js)
        file_types_box.add_widget(Label(text="JS", font_name="Roboto", color=(0.9, 0.9, 0.9, 1)))
        self.scrape_images = CheckBox(active=True, color=(0, 0.8, 1, 1))
        file_types_box.add_widget(self.scrape_images)
        file_types_box.add_widget(Label(text="Images", font_name="Roboto", color=(0.9, 0.9, 0.9, 1)))
        settings_box.add_widget(file_types_box)
        settings_box.add_widget(Label(text="Scraping Depth:", font_size=dp(20),
                                      font_name="Roboto", color=(0.9, 0.9, 0.9, 1)))
        self.depth_spinner = Spinner(text="1", values=("1", "2", "3"), size_hint=(0.5, 1),
                                     background_color=(0.1, 0.1, 0.15, 0.9), color=(1, 1, 1, 1),
                                     font_name="Roboto")
        settings_box.add_widget(self.depth_spinner)
        main_box.add_widget(settings_box)

        # Steuerungs-Buttons
        control_box = BoxLayout(orientation="horizontal", spacing=dp(30), size_hint=(1, 0.1))
        self.start_button = NeonButton(text="Start Scraping", button_color=(0, 0.8, 1, 0.9))
        self.start_button.bind(on_press=self.start_scraping)
        control_box.add_widget(self.start_button)
        self.pause_button = NeonButton(text="Pause", button_color=(1, 0.5, 0, 0.9))
        self.pause_button.bind(on_press=self.pause_scraping)
        self.pause_button.disabled = True
        control_box.add_widget(self.pause_button)
        self.cancel_button = NeonButton(text="Cancel", button_color=(1, 0, 0, 0.9))
        self.cancel_button.bind(on_press=self.cancel_scraping)
        self.cancel_button.disabled = True
        control_box.add_widget(self.cancel_button)
        main_box.add_widget(control_box)

        # Fortschrittsanzeige
        self.progress_bar = NeonProgressBar(max=100, value=self.progress_value, size_hint=(1, 0.05),
                                           bg_color=(0.2, 0.2, 0.25, 0.8), bar_color=(0, 0.8, 1, 1))
        main_box.add_widget(self.progress_bar)

        # Log-Fenster
        log_container = BoxLayout(size_hint=(1, 0.3), padding=dp(15))
        with log_container.canvas.before:
            Color(0.1, 0.1, 0.15, 0.9)
            RoundedRectangle(pos=log_container.pos, size=log_container.size, radius=[dp(15)])
        log_scroll = ScrollView()
        self.log_label = Label(text="", text_size=(None, None), size_hint_y=None, height=dp(300),
                               color=(0.9, 0.9, 0.9, 1), font_name="Roboto", halign="left", valign="top")
        self.log_label.bind(size=self.log_label.setter('text_size'))
        log_scroll.add_widget(self.log_label)
        log_container.add_widget(log_scroll)
        main_box.add_widget(log_container)

        # Vorschau-Button
        self.preview_button = NeonButton(text="Preview Scraped Page", button_color=(0.2, 0.6, 0.2, 0.9),
                                         size=(dp(300), dp(60)), font_size=dp(22))
        self.preview_button.bind(on_press=self.show_preview)
        self.preview_button.disabled = True
        main_box.add_widget(self.preview_button)

        self.add_widget(main_box)

    def add_log(self, message):
        self.log_text += f"[*] {message}\n"
        self.log_label.text = self.log_text

    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message, color=(1, 1, 1, 1), font_name="Roboto"),
                      size_hint=(0.5, 0.3), background_color=(0.1, 0.1, 0.15, 0.9))
        popup.open()

    def start_scraping(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.show_popup("Warning", "Please enter a URL!")
            return
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        self.is_scraping = True
        self.start_button.disabled = True
        self.pause_button.disabled = False
        self.cancel_button.disabled = False
        self.preview_button.disabled = True
        self.log_text = ""
        self.add_log(f"Starting scraping for {url}")
        Clock.schedule_once(lambda dt: self.scrape_website(url), 0.1)

    def pause_scraping(self, instance):
        if self.is_scraping:
            self.is_scraping = False
            self.pause_button.text = "Resume"
            self.add_log("Scraping paused")
        else:
            self.is_scraping = True
            self.pause_button.text = "Pause"
            self.add_log("Scraping resumed")
            Clock.schedule_once(lambda dt: self.continue_scraping(), 0.1)

    def cancel_scraping(self, instance):
        self.is_scraping = False
        self.start_button.disabled = False
        self.pause_button.disabled = True
        self.cancel_button.disabled = True
        self.progress_value = 0
        self.add_log("Scraping cancelled")
        self.scraping_links = []

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
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        try:
            driver.get(url)
            time.sleep(5)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            return soup
        finally:
            driver.quit()

    def scrape_website(self, url, depth=1):
        self.current_url = url
        domain = urlparse(url).netloc
        self.download_dir = os.path.join(os.getcwd(), f"scraped_{domain}")
        os.makedirs(self.download_dir, exist_ok=True)
        self.downloaded_files = []
        try:
            response = self.scraper.get(url, headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            self.add_log(f"Cloudscraper failed ({e}), switching to Selenium...")
            soup = self.scrape_with_selenium(url)
            if not soup:
                self.show_popup("Error", "Failed to scrape with Selenium too!")
                self.start_button.disabled = False
                self.pause_button.disabled = True
                self.cancel_button.disabled = True
                return
        # Collect links
        all_links = self.collect_links(soup, url)
        if int(self.depth_spinner.text) > 1 and depth < int(self.depth_spinner.text):
            page_links = self.collect_page_links(soup, url)
            all_links.extend(page_links)
        self.scraping_links = all_links
        self.progress_bar.max = len(self.scraping_links) or 1
        # Save the initial HTML
        html_path = os.path.join(self.download_dir, "index.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(str(soup.prettify()))
        self.downloaded_files.append(html_path)
        self.continue_scraping()

    def continue_scraping(self):
        if not self.is_scraping or not self.scraping_links:
            self.finalize_scraping()
            return
        link = self.scraping_links.pop(0)
        self.download_file(link, self.download_dir, self.current_url)
        self.progress_value = ((self.progress_bar.max - len(self.scraping_links)) / self.progress_bar.max) * 100
        Clock.schedule_once(lambda dt: self.continue_scraping(), random.uniform(0.5, 1.5))

    def finalize_scraping(self):
        soup = BeautifulSoup(open(os.path.join(self.download_dir, "index.html"), "r", encoding="utf-8").read(), "html.parser")
        self.adjust_html_paths(soup, self.download_dir)
        html_path = os.path.join(self.download_dir, "index.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(str(soup.prettify()))
        self.downloaded_files.append(html_path)
        for file_path in self.downloaded_files:
            if file_path.endswith('.css'):
                self.process_css_file(file_path, self.download_dir, self.current_url)
        self.create_zip(self.download_dir)
        self.save_info(soup, self.current_url, self.download_dir, len(self.scraping_links))
        self.show_popup("Success", f"Scraping completed! Files saved in {self.download_dir}")
        self.start_button.disabled = False
        self.pause_button.disabled = True
        self.cancel_button.disabled = True
        self.preview_button.disabled = False
        self.progress_value = 0
        self.add_log("Scraping completed")

    def collect_links(self, soup, base_url):
        links = set()
        if self.scrape_css.active:
            for css_link in soup.find_all("link", rel=["stylesheet", "preload"]):
                href = css_link.get("href")
                if href:
                    links.add(urljoin(base_url, href))
        if self.scrape_js.active:
            for script in soup.find_all("script"):
                src = script.get("src")
                if src:
                    links.add(urljoin(base_url, src))
        if self.scrape_images.active:
            for img in soup.find_all("img"):
                src = img.get("src")
                if src:
                    links.add(urljoin(base_url, src))
        return list(links)

    def collect_page_links(self, soup, base_url):
        links = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag.get("href")
            if href and not href.startswith('#'):
                absolute_url = urljoin(base_url, href)
                if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                    links.add(absolute_url)
        return list(links)

    def download_file(self, file_url, download_dir, base_url):
        if not self.is_scraping:
            return
        try:
            parsed_url = urlparse(file_url)
            path = parsed_url.path
            if not path or path == '/':
                return
            filename = os.path.basename(path)
            if not filename:
                filename = f"file_{len(self.downloaded_files)}.bin"
            if '.' not in filename:
                if 'css' in file_url.lower():
                    filename += '.css'
                elif 'js' in file_url.lower():
                    filename += '.js'
                elif 'image' in parsed_url.path.lower():
                    filename += '.jpg'
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            file_path = os.path.join(download_dir, filename)
            base_name, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(file_path):
                file_path = os.path.join(download_dir, f"{base_name}_{counter}{ext}")
                counter += 1
            response = self.scraper.get(file_url, headers=self.get_headers(), timeout=5)
            response.raise_for_status()
            with open(file_path, "wb") as f:
                f.write(response.content)
            self.downloaded_files.append(file_path)
            self.add_log(f"Downloaded: {file_url}")
        except requests.RequestException as e:
            self.add_log(f"Failed to download {file_url}: {e}")

    def adjust_html_paths(self, soup, download_dir):
        for css_link in soup.find_all("link", rel=["stylesheet", "preload"]):
            href = css_link.get("href")
            if href:
                parsed_url = urlparse(href)
                filename = os.path.basename(parsed_url.path)
                if '.' not in filename:
                    filename += '.css'
                filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                for downloaded_file in self.downloaded_files:
                    if os.path.basename(downloaded_file) == filename:
                        css_link['href'] = os.path.basename(downloaded_file)
                        break
        for script in soup.find_all("script"):
            src = script.get("src")
            if src:
                parsed_url = urlparse(src)
                filename = os.path.basename(parsed_url.path)
                if '.' not in filename:
                    filename += '.js'
                filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                for downloaded_file in self.downloaded_files:
                    if os.path.basename(downloaded_file) == filename:
                        script['src'] = os.path.basename(downloaded_file)
                        break
        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                parsed_url = urlparse(src)
                filename = os.path.basename(parsed_url.path)
                if '.' not in filename:
                    filename += '.jpg'
                filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                for downloaded_file in self.downloaded_files:
                    if os.path.basename(downloaded_file) == filename:
                        img['src'] = os.path.basename(downloaded_file)
                        break

    def process_css_file(self, css_path, download_dir, base_url):
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                content = f.read()
            url_pattern = r'url\(["\']?(.*?)["\']?\)'
            css_urls = re.findall(url_pattern, content)
            for url in css_urls:
                if url.startswith(('http', 'https')):
                    absolute_url = url
                elif url.startswith('/'):
                    absolute_url = urljoin(base_url, url)
                else:
                    css_base = os.path.dirname(urlparse(base_url).path)
                    absolute_url = urljoin(base_url, os.path.join(css_base, url))
                if not absolute_url.startswith(('http', 'https')):
                    continue
                self.download_file(absolute_url, download_dir, base_url)
            def replacer(match):
                url = match.group(1)
                if url.startswith(('data:', 'http', 'https')):
                    absolute_url = url if url.startswith(('http', 'https')) else urljoin(base_url, url)
                    parsed_url = urlparse(absolute_url)
                    filename = os.path.basename(parsed_url.path)
                    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                    for downloaded_file in self.downloaded_files:
                        if os.path.basename(downloaded_file) == filename:
                            return f'url("{os.path.basename(downloaded_file)}")'
                return match.group(0)
            new_content = re.sub(url_pattern, replacer, content)
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except Exception as e:
            self.add_log(f"Error processing CSS file {css_path}: {e}")

    def create_zip(self, download_dir):
        zip_path = os.path.join(download_dir, "downloaded_files.zip")
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            for file in self.downloaded_files:
                zipf.write(file, os.path.relpath(file, download_dir))
        self.add_log(f"Created ZIP: {zip_path}")

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
            f.write(f"Download Directory: {download_dir}\n")
        self.add_log(f"Saved info: {info_path}")

    def show_preview(self, instance):
        html_path = os.path.join(self.download_dir, "index.html")
        if os.path.exists(html_path):
            webbrowser.open(f"file://{os.path.abspath(html_path)}")
            self.add_log(f"Opened preview for {html_path}")
        else:
            self.show_popup("Error", "HTML file not found for preview!")

if __name__ == "__main__":
    WebScraperApp().run()
