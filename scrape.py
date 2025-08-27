import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

BASE_URL = "https://nvsc.lrv.lt"
URL_TEMPLATE = "https://nvsc.lrv.lt/lt/uzkreciamuju-ligu-valdymas/statistika-apie-uzkreciamasias-ligas/sergamumas-uzkreciamosiomis-ligomis-lietuvoje-{}m-statistine-ataskaitos-forma-nr-4-menesine/"

# Month names (for renaming)
MONTHS = [
    "01_January", "02_February", "03_March", "04_April", "05_May", "06_June",
    "07_July", "08_August", "09_September", "10_October", "11_November", "12_December"
]

# Loop over years
for year in [2011,2014,2017]:
    year_url = URL_TEMPLATE.format(year)
    print(f"\nProcessing year {year} → {year_url}")
    
    # Make year folder
    year_folder = os.path.join("nvsc_reports", str(year))
    os.makedirs(year_folder, exist_ok=True)

    try:
        resp = requests.get(year_url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ Could not access page for {year}: {e}")
        continue

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table")
    if not table:
        print(f"⚠️ No table found for {year}")
        continue
    
    rows = table.find_all("tr")

    # Determine which column is the file link column
    max_cols = max(len(r.find_all("td")) for r in rows if r.find_all("td"))
    file_col_index = max_cols - 1  # last "real" column
    
    month_idx = 0  # keep track of months

    for row in rows[1:]:  # skip header
        cols = row.find_all("td")
        if not cols:
            continue

        # Guard: skip rows that don't have enough columns
        if len(cols) <= file_col_index:
            if month_idx < 12:
                print(f"⚠️ {year} {MONTHS[month_idx]} → missing (row too short)")
                month_idx += 1
            continue

        # Find link in the target column
        link_tag = cols[file_col_index].find("a")
        if not link_tag or "href" not in link_tag.attrs:
            if month_idx < 12:
                print(f"⚠️ {year} {MONTHS[month_idx]} → no file link")
                month_idx += 1
            continue

        file_url = urljoin(BASE_URL, link_tag["href"])
        month_name = MONTHS[month_idx]
        file_ext = os.path.splitext(file_url.split("?")[0])[1] or ".xls"
        out_path = os.path.join(year_folder, f"{month_name}{file_ext}")

        try:
            print(f"⬇️ Downloading {year} {month_name} …")
            file_resp = requests.get(file_url, timeout=15)
            file_resp.raise_for_status()
            with open(out_path, "wb") as f:
                f.write(file_resp.content)
        except Exception as e:
            print(f"❌ Failed {year} {month_name}: {e}")
        finally:
            month_idx += 1

    # If fewer than 12 months, pad missing months
    while month_idx < 12:
        print(f"⚠️ {year} {MONTHS[month_idx]} → missing (not listed)")
        month_idx += 1
