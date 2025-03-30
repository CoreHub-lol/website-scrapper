# 🕸️ WebScraperApp

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Built with Kivy](https://img.shields.io/badge/built%20with-Kivy-ff69b4)](https://kivy.org/)
[![Selenium](https://img.shields.io/badge/Selenium-Enabled-brightgreen?logo=selenium)]
[![WebScraping](https://img.shields.io/badge/Web-Scraping-orange)](https://github.com/topics/web-scraping)

## ✨ Overview

**WebScraperApp** is a modern and user-friendly GUI application that allows you to scrape any website, collect its resources (images, scripts, stylesheets), and save them locally in a clean ZIP archive. If access is blocked by services like Cloudflare, the app automatically switches to **Selenium** to bypass restrictions.

## 💡 Key Features

- 🌐 **Scrape websites using Cloudscraper or Selenium**
- 🖥️ **Minimalistic and functional GUI** built with [Kivy](https://kivy.org/)
- 📥 **Download and store all HTML, JS, CSS, and image assets**
- 🗜️ **Creates a ZIP archive of the collected data**
- 📊 **Real-time progress bar for download tracking**
- 🔄 **Automatic fallback to Selenium if Cloudscraper fails**
- 📝 **Generates a summary file with page info and complexity level**

## 📸 Screenshot

> _(Optional: Add a screenshot of the app's interface here)_

## 🧩 Requirements

Install all dependencies with pip:

```bash
pip install kivy requests beautifulsoup4 cloudscraper selenium webdriver-manager tqdm
