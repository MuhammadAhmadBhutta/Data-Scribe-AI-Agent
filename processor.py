import pandas as pd
import polars as pl
import numpy as np
import json
from datetime import datetime

class DataProcessor:
    def __init__(self):
        pass
        
    def process_scraped_data(self, data, log_callback=None):
        if log_callback: log_callback("Scribe: Cleaning data with Polars...")
        
        # Convert headings to a Polars DataFrame for fast processing
        df_pl = pl.DataFrame({
            "content": data.get("headings", []),
            "type": ["heading"] * len(data.get("headings", []))
        })
        
        if log_callback: log_callback("Scribe: Transforming data with Pandas...")
        # Convert to Pandas for more complex transformations if needed
        df_pd = df_pl.to_pandas()
        df_pd['length'] = df_pd['content'].apply(len)
        df_pd['timestamp'] = datetime.now().isoformat()
        
        if log_callback: log_callback("Scribe: Generating numerical aggregations with NumPy...")
        avg_len = np.mean(df_pd['length']) if not df_pd.empty else 0
        max_len = np.max(df_pd['length']) if not df_pd.empty else 0
        
        summary = {
            "avg_heading_length": float(avg_len),
            "max_heading_length": int(max_len),
            "total_items": len(df_pd),
            "processed_at": datetime.now().isoformat()
        }
        
        if log_callback: log_callback("Scribe: Data processing complete.")
        return df_pd.to_dict(orient='records'), summary

    def save_to_log(self, data, summary, url):
        log_entry = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "sample_data": data[:5]
        }
        
        log_file = "scribe_log.json"
        logs = []
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                try:
                    logs = json.load(f)
                except:
                    logs = []
        
        logs.append(log_entry)
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=4)
        
        return log_entry

import os
