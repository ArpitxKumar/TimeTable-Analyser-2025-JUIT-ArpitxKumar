import re
from datetime import datetime
import pandas as pd

def load_timetable(path):
    xl = pd.ExcelFile(path)
    print("Available sheets:")
    for i, name in enumerate(xl.sheet_names):
        if i:
            print(f"{i}: {name}")
    
    idx = int(input("Enter sheet index to use: "))
    return pd.read_excel(path, sheet_name=xl.sheet_names[idx], header=None)

def parse_cell(cell_str):
    tokens = cell_str.split()
    subject = tokens[0] if tokens else ""
    room = tokens[-1] if tokens else ""
    m = re.search(r"\(([A-Za-z0-9]+)\)", cell_str)
    faculty = m.group(1) if m else ""
    batch_tokens = [t for t in tokens if "24" in t]
    batch_info = " ".join(batch_tokens)
    return subject, batch_info, faculty, room

def format_time_range(time_str):
    if not isinstance(time_str, str):
        return time_str
    parts = time_str.split("-")
    if len(parts) != 2:
        return time_str.strip()
    
    def norm(t):
        t_clean = t.strip().replace(" ", "")
        for fmt in ("%I:%M%p", "%I:%M %p"):
            try:
                return datetime.strptime(t_clean, fmt.replace(" ", "")).strftime("%I:%M %p")
            except ValueError:
                continue
        return t.strip()
    
    return f"{norm(parts[0])} - {norm(parts[1])}"

def parse_start_time(time_str):
    if not isinstance(time_str, str):
        return None
    start = time_str.split("-")[0].strip()
    try:
        start_clean = start.replace(" ", "")
        return datetime.strptime(start_clean, "%I:%M%p").time()
    except ValueError:
        try:
            return datetime.strptime(start, "%I:%M %p").time()
        except ValueError:
            return None

def filter_matrix_by_batch(df, batch_code):
    batch_code = str(batch_code).strip()
    time_labels = df.iloc[1].fillna("").astype(str).tolist()
    records = []
    current_day = None
    
    for r in range(2, len(df)):
        row = df.iloc[r]
        val0 = str(row.iloc[0]).strip()
        if val0 and val0.upper() not in ["NAN"]:
            current_day = val0
        
        if not current_day:
            continue
            
        for c in range(1, len(row)):
            cell = row.iloc[c]
            if pd.isna(cell) or batch_code not in str(cell):
                continue
            
            time_label = format_time_range(time_labels[c] if c < len(time_labels) else f"Col {c}")
            subject, batch_info, faculty, room = parse_cell(str(cell))
            
            records.append({
                "Day": current_day,
                "Time": time_label,
                "Subject": subject,
                "BatchInfo": batch_info,
                "Faculty": faculty,
                "Room": room,
            })
    
    return pd.DataFrame(records)

def show_table(df):
    if df.empty:
        print("No entries found for this batch.")
        return
    
    df = df.copy()
    df["StartTime"] = df["Time"].apply(parse_start_time)
    day_order = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4, "SAT": 5, "SUN": 6}
    df["DayOrder"] = df["Day"].str.upper().map(day_order)
    df = df.sort_values(["DayOrder", "StartTime", "Time"]).drop(columns=["StartTime", "DayOrder"])
    
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 180)
    pd.set_option("display.colheader_justify", "center")
    
    print("\nYour timetable:\n")
    for day, day_df in df.groupby("Day", sort=False):
        print(day_df.to_string(index=False))
        print()

if __name__ == "__main__":
    path = input("Enter the name of timetable file: ")
    timetable_df = load_timetable(path)
    batch = input("Enter your batch code: ")
    batch_df = filter_matrix_by_batch(timetable_df, batch)
    show_table(batch_df)
