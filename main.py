from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
import time
import sys
from pathlib import Path

def is_video_file(href: str) -> bool:
    if not href:
        return False
    lower = href.lower().rstrip('/')
    return lower.endswith(('.mp4', '.mov'))

def normalize_url(url: str) -> str:
    return url.rstrip('/') + '/'

def crawl_directory(driver, base_url: str, output_file: str, visited: set, depth: int = 0, max_depth: int = 8):
    if base_url in visited or depth > max_depth:
        return
    visited.add(base_url)

    print(f"{'  ' * depth}→ Opening: {base_url}")

    try:
        driver.get(base_url)
        time.sleep(3)  # Wait for load + JS (adjust down if too slow)

        # Optional: scroll if lazy-loaded junk exists
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        links = driver.find_elements(By.TAG_NAME, "a")

        sub_dirs = []
        videos_found = []

        for link in links:
            try:
                href = link.get_attribute("href") or ""
                if not href:
                    continue
                full_url = urljoin(base_url, href.strip())

                # Skip junk / parent / current
                clean_href = href.strip().rstrip('/')
                if clean_href in ("", ".", "..", "./", "../"):
                    continue

                if href.endswith('/'):
                    if full_url not in visited:
                        sub_dirs.append(full_url)
                elif is_video_file(href):
                    print(f"{'  ' * (depth + 1)}VIDEO: {full_url}")
                    videos_found.append(full_url)

            except:
                pass  # ignore stale elements

        # Save immediately per folder
        if videos_found:
            with open(output_file, "a", encoding="utf-8") as f:
                for v in videos_found:
                    f.write(v + "\n")

        # Recurse subfolders
        for sub in sub_dirs:
            crawl_directory(driver, sub, output_file, visited, depth + 1, max_depth)

    except Exception as e:
        print(f"{'  ' * depth}  Crash at {base_url}: {str(e)}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py https://porncorporation.com/42/")
        sys.exit(1)

    start_url = normalize_url(sys.argv[1])
    output = "weburl.txt"
    Path(output).write_text("")  # clear old

    print(f"Start → {start_url}")
    print(f"Videos → {output}\nBrowser visible — don't close manually!\n")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    visited = set()

    try:
        crawl_directory(driver, start_url, output, visited)
    finally:
        driver.quit()
        print("\nDone. Check weburl.txt")

if __name__ == "__main__":
    main()