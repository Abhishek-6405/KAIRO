from playwright.sync_api import sync_playwright, Browser, BrowserContext
from bs4 import BeautifulSoup
import time

# Global browser instance — stays open until YOU say close
_playwright = None
_browser = None
_context = None

def open_browser():
    global _playwright, _browser, _context
    if _browser is None:
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(
            headless=False,
            args=["--start-maximized"]
        )
        _context = _browser.new_context(viewport={"width": 1280, "height": 800})
    return _context

def close_browser():
    global _playwright, _browser, _context
    if _browser:
        _browser.close()
        _playwright.stop()
        _browser = None
        _context = None
        _playwright = None
        print("KAIRO: Browser closed.")

def search_and_show(query):
    print(f"KAIRO: Searching for '{query}'...")
    context = open_browser()
    results_text = []

    page = context.new_page()
    page.goto(f"https://www.google.com/search?q={query}")
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    content = page.content()
    soup = BeautifulSoup(content, "html.parser")
    for g in soup.find_all('div', class_='BNeawe')[:5]:
        text = g.get_text()
        if len(text) > 40:
            results_text.append(text)

    return " | ".join(results_text[:3]) if results_text else "No results found."

def get_news():
    print("KAIRO: Fetching latest news...")
    context = open_browser()
    results_text = []

    sources = [
        ("Times of India", "https://timesofindia.indiatimes.com"),
        ("NDTV", "https://www.ndtv.com"),
        ("News18", "https://www.news18.com"),
    ]

    for name, url in sources:
        tab = context.new_page()
        tab.goto(url)

    time.sleep(4)

    for name, url in sources:
        try:
            pages = context.pages
            for p in pages:
                if any(s in p.url for s in ["timesofindia", "ndtv", "news18"]):
                    content = p.content()
                    soup = BeautifulSoup(content, "html.parser")
                    headlines = []
                    for tag in soup.find_all(['h1', 'h2', 'h3'])[:5]:
                        text = tag.get_text().strip()
                        if len(text) > 20:
                            headlines.append(text)
                    if headlines:
                        results_text.append(f"{name}: " + " | ".join(headlines[:3]))
        except:
            continue

    return "\n".join(results_text) if results_text else "Could not fetch news."

def open_specific_site(query, name):
    """Google the site name and open the first result automatically"""
    print(f"KAIRO: Searching for {name}...")
    context = open_browser()

    # Open Google and search for the site
    search_page = context.new_page()
    search_page.goto(f"https://www.google.com/search?q={query}+official+website")
    search_page.wait_for_load_state("networkidle")
    time.sleep(2)

    content = search_page.content()
    soup = BeautifulSoup(content, "html.parser")

    # Get the first real result link
    first_url = None
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/url?q='):
            actual_url = href.split('/url?q=')[1].split('&')[0]
            if actual_url.startswith('http') and 'google' not in actual_url:
                first_url = actual_url
                break

    if first_url:
        # Open the actual website in a new tab
        site_tab = context.new_page()
        site_tab.goto(first_url, timeout=15000)
        site_tab.wait_for_load_state("networkidle", timeout=10000)
        time.sleep(2)

        # Read the page
        content = site_tab.content()
        soup = BeautifulSoup(content, "html.parser")
        headlines = []
        for tag in soup.find_all(['h1', 'h2', 'h3'])[:5]:
            text = tag.get_text().strip()
            if len(text) > 10:
                headlines.append(text)

        return " | ".join(headlines[:5]) if headlines else "Page opened successfully."
    
    return ""

def search_jobs(role, location):
    print(f"KAIRO: Searching jobs for {role} in {location}...")
    context = open_browser()
    results_text = []

    sites = [
        f"https://www.linkedin.com/jobs/search/?keywords={role}&location={location}",
        f"https://www.naukri.com/{role.replace(' ', '-')}-jobs-in-{location.replace(' ', '-')}",
        f"https://internshala.com/jobs/{role.replace(' ', '-')}-jobs-in-{location.replace(' ', '-')}",
    ]

    for url in sites:
        tab = context.new_page()
        tab.goto(url)

    time.sleep(5)

    for page in context.pages[1:]:
        try:
            content = page.content()
            soup = BeautifulSoup(content, "html.parser")
            jobs = []
            for tag in soup.find_all(['h3', 'h4'])[:5]:
                text = tag.get_text().strip()
                if len(text) > 10:
                    jobs.append(text)
            if jobs:
                results_text.append(" | ".join(jobs[:3]))
        except:
            continue

    return "\n".join(results_text) if results_text else "Could not find jobs right now."