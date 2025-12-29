# TimeTable-Analyser-2025-JUIT-ArpitxKumar

A Python script that parses Excel-based college timetables and extracts personalized schedules by batch code.

## Features
- Loads Excel files with multiple sheets

- Automatically detects and filters classes by batch code

- Parses subjects, faculty, rooms from timetable cells

- Formats time ranges consistently (handles "09:00AM" and "09:00 AM")

- Displays sorted timetable by day and time

- Groups output by day for easy reading

## Requirements
```
pip install pandas openpyxl
```

## Usage
- Save your timetable Excel file (Prefer in same directory where your code is present)

- Run the script:

```
python code.py
```

- Enter the Excel filename when prompted

- Select sheet index from the list

- Enter your batch code

## How It Works
- Loads Excel: Reads selected sheet without headers

- Parses Cells: Extracts subject, batch, faculty, room

- Filters Batch: Only shows classes matching your batch code

- Sorts Smartly: Days (MON-SUN) then start times

- Formats Nicely: Clean time ranges and day-grouped display

## Limitations
- Faculty in format (PROF1)

- Days start from row 3, column A

- Time labels in row 2

- Troubleshooting
- No entries found: Check batch code spelling

- Sheet not found: Verify Excel file path

- Time parsing errors: Ensure time format is HH:MM AM/PM

## Credits

- ArpitxKumar

## Built for computer science students parsing college timetables. Contributions welcome!