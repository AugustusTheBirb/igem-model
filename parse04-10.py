import os
import pandas as pd

BASE_FOLDER = "nvsc_reports"
OUT_FOLDER = "parsed_csv"
os.makedirs(OUT_FOLDER, exist_ok=True)

def parse_excel_file(path, year, month):
    """Parse a single Excel file, return list of (name, year, month, infections)."""
    try:
        df = pd.read_excel(path, header=None)  # raw, no header
    except Exception as e:
        print(f"❌ Could not open {path}: {e}")
        return []

    df = df.dropna(how="all")  # drop fully empty rows
    rows = []

    started = False
    for _, row in df.iterrows():
        name = row.iloc[0]
        infections = row.iloc[3] if len(row) > 2 else None

        # Check: col1 = string, col3 = numeric and not NaN
        if isinstance(name, str) and pd.api.types.is_number(infections) and not pd.isna(infections):
            if not started:
                started = True  # begin parsing
            rows.append([name.strip(), year, month, int(infections)])
        else:
            if started:
                break  # stop when pattern breaks

    return rows


for year in range(2004, 2011):
    year_folder = os.path.join(BASE_FOLDER, str(year))
    if not os.path.exists(year_folder):
        print(f"⚠️ Skipping {year}, no folder found")
        continue

    all_rows = []
    for month in range(1, 13):
        # Files were saved as 01_January.xls etc
        possible_exts = [".xls", ".xlsx"]
        file_path = None
        for ext in possible_exts:
            test_path = os.path.join(year_folder, f"{month:02d}_{pd.Timestamp(month=month, day=1, year=2000).strftime('%B')}{ext}")
            if os.path.exists(test_path):
                file_path = test_path
                break

        if not file_path:
            print(f"⚠️ {year}-{month:02d} missing file")
            continue

        rows = parse_excel_file(file_path, year, month)
        if rows:
            all_rows.extend(rows)
        else:
            print(f"⚠️ {year}-{month:02d} no valid rows extracted")

    # Save CSV for the year
    if all_rows:
        out_csv = os.path.join(OUT_FOLDER, f"{year}.csv")
        df_out = pd.DataFrame(all_rows, columns=["name", "year", "month", "infections"])
        df_out.to_csv(out_csv, index=False, encoding="utf-8")
        print(f"✅ Wrote {out_csv} with {len(all_rows)} rows")
    else:
        print(f"⚠️ No data extracted for {year}")
