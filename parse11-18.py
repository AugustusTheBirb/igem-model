import os
import pdfplumber
import re
import pandas as pd

BASE_FOLDER = "nvsc_reports"
OUT_FOLDER = "parsed_csv"
os.makedirs(OUT_FOLDER, exist_ok=True)

def parse_pdf_file(path, year, month):
    rows = []
    capture = False
    end = 0
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            # Look for start and stop markers
            if "27. Laimo liga" in text:
                capture = True
                end = 1

            if capture:
                end += 1
                if end == 4:  # stop after ~2 pages of this table
                    capture = False

            if capture:
                table = page.extract_table()
                if table:
                    for row in table:
                        if not row or len(row) < 23:
                            continue
                        name, infections1, infections2 = row[0], row[-11], row[-22]

                        if not name or "Lietuvoje" in str(name):
                            continue
                        if not infections1 or not infections2:
                            continue
                        try:
                            infections1 = int(re.sub(r"\D", "", str(infections1)))
                            infections2 = int(re.sub(r"\D", "", str(infections2)))
                        except:
                            continue
                        infections = infections1 + infections2

                        rows.append([name.strip(), year, month, infections])
    return rows

# --- Batch process 2011–2018 ---
for year in [2018]:
    year_folder = os.path.join(BASE_FOLDER, str(year))
    if not os.path.exists(year_folder):
        print(f"⚠️ No folder for {year}, skipping")
        continue

    all_rows = []
    for month in range(1,13):
        month_name = pd.Timestamp(year=2000, month=month, day=1).strftime("%B")
        filename = f"{month:02d}_{month_name}.pdf"
        file_path = os.path.join(year_folder, filename)
        if not os.path.exists(file_path):
            print(f"⚠️ Missing {year}-{month:02d}")
            continue

        print(f"📄 Parsing {file_path} ...")
        rows = parse_pdf_file(file_path, year, month)
        if rows:
            all_rows.extend(rows)
        else:
            print(f"⚠️ No rows extracted from {file_path}")

    if all_rows:
        out_csv = os.path.join(OUT_FOLDER, f"{year}.csv")
        df_out = pd.DataFrame(all_rows, columns=["name","year","month","infections"])
        df_out.to_csv(out_csv, index=False, encoding="utf-8")
        print(f"✅ Wrote {out_csv} ({len(all_rows)} rows)")
    else:
        print(f"⚠️ Nothing extracted for {year}")
