import os
import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime, timedelta

base_dir = "/Users/ibe/Desktop/spark/notebooks/Arxiv_2025"
os.makedirs(base_dir, exist_ok=True)

start_date = datetime(2025, 1, 1)
end_date = datetime(2026, 1, 1)

ns = {'atom': 'http://www.w3.org/2005/Atom'}

day = timedelta(days=1)
total_count = 0

while start_date < end_date:
    from_str = start_date.strftime("%Y%m%d%H%M")
    to_str = (start_date + day).strftime("%Y%m%d%H%M")
    print(f"Retrieving: {from_str} until {to_str}")

    url = f"https://export.arxiv.org/api/query?search_query=submittedDate:[{from_str}+TO+{to_str}]&max_results=2000"

    response = requests.get(url)
    if response.status_code != 200:
        print("Error --> SKIP")
        start_date += day
        continue

    root = ET.fromstring(response.content)
    entries = root.findall('atom:entry', ns)
    print(f"🔹 {len(entries)} articles found")

    for entry in entries:
        aid_raw = entry.find('atom:id', ns).text
        aid = aid_raw.split('/')[-1]

        item = {
            'id': aid_raw,
            'title': entry.find('atom:title', ns).text.strip(),
            'summary': entry.find('atom:summary', ns).text.strip(),
            'published': entry.find('atom:published', ns).text,
            'updated': entry.find('atom:updated', ns).text,
            'authors': [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)],
            'categories': [cat.attrib['term'] for cat in entry.findall('atom:category', ns)]
        }

        filename = f"{aid}.json"
        filepath = os.path.join(base_dir, filename)

        if not os.path.exists(filepath):
            with open(filepath, "w") as f:
                json.dump(item, f, indent=2)
            total_count += 1

    start_date += day

print(f"Total {total_count}")
