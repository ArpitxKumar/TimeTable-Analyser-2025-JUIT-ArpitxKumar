import re
import os
import json
from datetime import datetime
import pandas as pd

def load_timetable(path):
    xl = pd.ExcelFile(path)
    print("Available sheets:")
    for i, name in enumerate(xl.sheet_names):
        if i:
            print(f"{i}: {name}")
    return pd.read_excel(
        path,
        sheet_name=xl.sheet_names[int(input("Enter sheet index to use: "))],
        header=None
    )

def is_valid_day(val):
    return isinstance(val, str) and val.strip() and val.upper() != "NAN"

def parse_start_time(time_str):
    if not isinstance(time_str, str):
        return None
    start = time_str.split("-")[0].strip().replace(" ", "")
    for fmt in ("%I:%M%p",):
        try:
            return datetime.strptime(start, fmt).time()
        except ValueError:
            pass
    return None

def format_time_range(time_str):
    if not isinstance(time_str, str) or "-" not in time_str:
        return time_str

    def norm(t):
        try:
            return datetime.strptime(t.strip().replace(" ", ""), "%I:%M%p").strftime("%I:%M %p")
        except ValueError:
            return t.strip()

    a, b = time_str.split("-", 1)
    return f"{norm(a)} - {norm(b)}"

def parse_cell(cell_str):
    tokens = cell_str.split()
    subject = tokens[0] if tokens else ""
    room = tokens[-1] if tokens else ""
    faculty = re.search(r"\(([^)]+)\)", cell_str)
    batch_info = " ".join(t for t in tokens if "24" in t)
    return subject, batch_info, faculty.group(1) if faculty else "", room

def load_additional_subjects():
    os.makedirs("Additional Subjects", exist_ok=True)

    if input("Do you have a saved additional subjects list? (y/n): ").strip().lower() == "y":
        path = os.path.join(
            "Additional Subjects",
            input("Enter saved file name: ").strip() + ".json"
        )
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        print("Saved file not found. Switching to manual entry.")

    subjects = input("Enter subject codes (space separated): ").split()

    if input("Do you want to save this list? (y/n): ").strip().lower() == "y":
        path = os.path.join(
            "Additional Subjects",
            input("Enter file name to save: ").strip() + ".json"
        )
        with open(path, "w") as f:
            json.dump(subjects, f, indent=2)
        print(f"Additional subjects saved to {path}")

    return subjects

def filter_matrix_by_batch_and_subjects(df, batch_code, subject_codes):
    time_labels = df.iloc[1].fillna("").astype(str).tolist()
    records, current_day = [], None

    for r in range(2, len(df)):
        row = df.iloc[r]
        if is_valid_day(row.iloc[0]):
            current_day = row.iloc[0]

        if not current_day:
            continue

        for c in range(1, len(row)):
            cell = row.iloc[c]
            if pd.isna(cell):
                continue

            cell_str = str(cell)
            subject_match = any(s in cell_str for s in subject_codes)
            batch_match = batch_code in cell_str

            if not (batch_match or subject_match):
                continue

            subject, batch_info, faculty, room = parse_cell(cell_str)

            records.append({
                "Day": current_day,
                "Time": format_time_range(time_labels[c]),
                "Subject": subject,
                "Batch Info": batch_info,
                "Faculty": faculty,
                "Room": room,
                "Additional": "√" if subject_match else ""
            })

    return pd.DataFrame(records)

def show_table(df):
    if df.empty:
        print("No entries found.")
        return

    df["StartTime"] = df["Time"].apply(parse_start_time)
    df["DayOrder"] = df["Day"].str.upper().map(
        {"MON":0,"TUE":1,"WED":2,"THU":3,"FRI":4,"SAT":5,"SUN":6}
    )

    df = df.sort_values(["DayOrder", "StartTime"]).drop(columns=["StartTime", "DayOrder"])

    widths = [max(len(str(x)) for x in df[col].astype(str).tolist() + [col]) + 2 for col in df]
    print("\nYour timetable:\n")
    print("".join(col.ljust(w) for col, w in zip(df.columns, widths)))

    last_day = None
    for _, row in df.iterrows():
        if last_day and row["Day"] != last_day:
            print()
        print("".join(str(v).ljust(w) for v, w in zip(row, widths)))
        last_day = row["Day"]

if __name__ == "__main__":
    df = load_timetable(input("Enter the name of timetable file: "))
    batch = input("Enter your batch code: ")

    subjects = []
    if input("Do you want to add additional subjects? (y/n): ").strip().lower() == "y":
        subjects = load_additional_subjects()

    show_table(filter_matrix_by_batch_and_subjects(df, batch, subjects))
