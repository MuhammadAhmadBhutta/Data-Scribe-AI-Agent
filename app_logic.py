import os
import time
import json
import numpy as np
import pandas as pd
import polars as pl
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class ScribeAgent:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    def log(self, msg):
        if self.log_callback:
            self.log_callback(f"[SYSTEM] {msg}")
        print(f"[SYSTEM] {msg}")

    def scrape(self, url, custom_filename=None):
        self.log(f"Launching Headless Chrome for {url}...")
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.options)
            driver.set_page_load_timeout(30)
            
            self.log(f"Loading DOM for {url}...")
            driver.get(url)
            time.sleep(3) # Wait for potential JS execution
            page_source = driver.page_source
            driver.quit()
        except Exception as e:
            self.log(f"Selenium error: {str(e)}")
            raise e

        self.log("Parsing HTML structure with BeautifulSoup...")
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # 1. Extract Tables -> Polars
        tables = soup.find_all('table')
        extracted_tables = []
        if tables:
            self.log(f"Found {len(tables)} tables. Processing with Polars...")
            for idx, table in enumerate(tables):
                try:
                    df_pd = pd.read_html(str(table))[0]
                    # Cleanup: Force convert strings to numbers where possible
                    for col in df_pd.columns:
                        df_pd[col] = pd.to_numeric(df_pd[col], errors='ignore')
                    
                    df_pl = pl.from_pandas(df_pd)
                    extracted_tables.append({
                        "id": idx,
                        "data": df_pl.to_dicts(),
                        "columns": df_pl.columns
                    })
                except Exception as table_err:
                    self.log(f"Skipping table {idx} due to error: {str(table_err)}")

        # 2. Extract Lists -> If no tables
        extracted_lists = []
        if not extracted_tables:
            self.log("No structured tables found. Searching for <ul> and <ol> lists...")
            lists = soup.find_all(['ul', 'ol'])
            for idx, lst in enumerate(lists):
                items = [li.get_text().strip() for li in lst.find_all('li') if li.get_text().strip()]
                if len(items) > 2: # Ignore very short lists
                    extracted_lists.append({
                        "id": idx,
                        "items": items[:50] # Cap for visualization
                    })
            if extracted_lists:
                self.log(f"Extracted {len(extracted_lists)} lists.")

        # 3. Extract Headers
        headers = {
            "h1": [h.get_text().strip() for h in soup.find_all('h1')],
            "h2": [h.get_text().strip() for h in soup.find_all('h2')],
            "h3": [h.get_text().strip() for h in soup.find_all('h3')]
        }
        self.log(f"Headers captured: {len(headers['h1'])} H1s, {len(headers['h2'])} H2s.")

        # Final Validation
        if not extracted_tables and not extracted_lists and not any(headers.values()):
            return {"status": "error", "message": "No structured data found on this URL"}

        # Store to Scribe Log
        result = {
            "status": "success",
            "url": url,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tables": extracted_tables,
            "lists": extracted_lists,
            "headers": headers,
            "stats": {
                "tables_count": len(extracted_tables),
                "lists_count": len(extracted_lists),
                "headers_count": sum(len(v) for v in headers.values())
            }
        }
        self.save_log(result, custom_filename=custom_filename)
        return result

    def save_log(self, data, custom_filename=None):
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        timestamp = time.strftime("%H%M%S")
        base_name = custom_filename if custom_filename else f"scrape_{time.strftime('%Y%m%d_%H%M%S')}"
        
        # 1. Update Global JSON Log
        log_file = os.path.join(data_dir, "scribe_log.json")
        logs = []
        if os.path.exists(log_file):
            try:
                with open(log_file, "r") as f:
                    logs = json.load(f)
            except:
                logs = []
        
        logs.append(data)
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=4)
        
        # 2. Save Individual JSON Scrape
        session_file = os.path.join(data_dir, f"{base_name}_{timestamp}.json")
        if custom_filename:
            session_file = os.path.join(data_dir, f"{custom_filename}.json")

        with open(session_file, "w") as f:
            json.dump(data, f, indent=4)
            
        # 3. Export Tables to CSV
        if data['tables']:
            for table in data['tables']:
                try:
                    df = pd.DataFrame(table['data'])
                    csv_name = f"{base_name}_table_{table['id']}.csv"
                    csv_path = os.path.join(data_dir, csv_name)
                    df.to_csv(csv_path, index=False)
                    self.log(f"Table {table['id']} exported as {csv_name}.")
                except Exception as e:
                    self.log(f"Failed to export CSV for Table {table['id']}: {str(e)}")

        # 4. Export Text Content to Markdown
        md_name = f"{base_name}_content.md"
        md_path = os.path.join(data_dir, md_name)
        try:
            with open(md_path, "w", encoding="utf-8") as md:
                md.write(f"# Scribe Agent Extraction: {data['url']}\n")
                md.write(f"- **Timestamp:** {data['timestamp']}\n")
                md.write(f"- **Total Items:** {data['stats']['headers_count'] + data['stats']['lists_count']}\n\n")
                
                md.write("## Headers (Categories)\n")
                for lvl in ['h1', 'h2', 'h3']:
                    if data['headers'][lvl]:
                        md.write(f"### {lvl.upper()}\n")
                        for item in data['headers'][lvl]:
                            md.write(f"- {item}\n")
                
                if data['lists']:
                    md.write("\n## Extracted Lists\n")
                    for lst in data['lists']:
                        md.write(f"### Segment {lst['id']}\n")
                        for item in lst['items']:
                            md.write(f"- {item}\n")
            self.log(f"Text content exported as {md_name}.")
        except Exception as e:
            self.log(f"Failed to export Markdown: {str(e)}")
            
        self.log(f"Multi-format logs updated in /{data_dir} folder.")

if __name__ == "__main__":
    agent = ScribeAgent()
    print(agent.scrape("https://example.com"))
