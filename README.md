# 🕸️ WebScraperApp

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Made with Kivy](https://img.shields.io/badge/made%20with-Kivy-ff69b4)](https://kivy.org/)
[![Selenium](https://img.shields.io/badge/Selenium-Used-brightgreen?logo=selenium)]
[![WebScraping](https://img.shields.io/badge/Web-Scraping-orange)](https://github.com/topics/web-scraping)

## ✨ Beschreibung

Ein moderner Web-Scraper mit GUI (gebaut mit [Kivy](https://kivy.org/)), der Webseiten analysiert, verlinkte Ressourcen herunterlädt und alles sauber als ZIP-Datei speichert. Bei Problemen mit normalen Anfragen wird automatisch auf **Selenium** zurückgegriffen.

## 🛠️ Features

- 🌐 **Website-Scraping mit Cloudscraper & Selenium**
- 🎛️ **Intuitive Benutzeroberfläche** (Kivy)
- 📁 **Automatische Speicherung von HTML & Ressourcen**
- 🗜️ **ZIP-Erstellung aller gesammelten Dateien**
- 📊 **Dynamische Fortschrittsanzeige**
- 📑 **Zusätzliche Metadaten-Speicherung zur Website**
- 🔄 **Fallback zu Selenium bei geschützten Seiten (z. B. Cloudflare)**

## 🖥️ Screenshot

> _(Optional: Du kannst hier ein Screenshot deines Tools einfügen, z. B. aus der GUI)_

## 🧰 Abhängigkeiten

- `kivy`
- `requests`
- `beautifulsoup4`
- `cloudscraper`
- `selenium`
- `webdriver-manager`
- `tqdm`

Installation (z. B. mit `pip`):
```bash
pip install kivy requests beautifulsoup4 cloudscraper selenium webdriver-manager tqdm
