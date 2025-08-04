# scheduler.py

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment
from io import BytesIO
from datetime import datetime
import re

def to_dt(time):
    if isinstance(time, str):
        time = time.strip().lower()
        for fmt in ("%I%p", "%I:%M%p", "%H:%M:%S", "%H:%M"):
            try:
                return datetime.combine(datetime.today(), datetime.strptime(time, fmt).time())
            except ValueError:
                continue
        raise ValueError(f"Unsupported time format: {time}")
    return datetime.combine(datetime.today(), time)

def is_available(row, time):
    return to_dt(row['AM Start']) <= to_dt(time) <= to_dt(row['AM End'])

def parse_cell_content(content):
    student_count = 0
    instructor_names = []
    tokens = [token.strip() for token in re.split(r'[\n,/]', str(content)) if token.strip()]
    for token in tokens:
        match = re.match(r"(.+?)\s*[\\/]?\s*(\d+)$", token)
        if match:
            name = match.group(1).strip()
            count = int(match.group(2))
            student_count = count
            instructor_names.append((name, count))
        elif token.isdigit():
            student_count = int(token)
        else:
            instructor_names.append((token, None))
    return instructor_names, student_count

def generate_am_schedule(template_df, availability_df, template_path=None, manual_mode=False):
    if hasattr(template_path, 'read'):
        template_bytes = template_path.read()
        template_path = BytesIO(template_bytes)

    wb = load_workbook(filename=template_path)
    ws = wb.active

    headers = [cell.value for cell in ws[1]]
    time_slots = [row[0].value for row in ws.iter_rows(min_row=2, max_col=1)]

    instructor_assignments = {name: [] for name in availability_df['Name']}
    instructor_roles = availability_df.set_index("Name")['Role'].to_dict()
    assignments_by_time = {str(t): [] for t in time_slots}
    total_breaks = {name: 0 for name in availability_df['Name']}
    last_class_by_instructor = {name: None for name in availability_df['Name']}

    # First pass: assign at least one instructor to each class
    for i, row in enumerate(ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=len(headers))):
        time_cell = row[0]
        time_str = str(time_cell.value)

        for j, cell in enumerate(row[1:], start=1):
            class_name = headers[j]
            if not class_name:
                continue
            class_name = class_name.strip()
            if class_name.lower() == "brk":
                continue

            content = str(cell.value) if cell.value else ""
            if not content.strip():
                continue

            parsed_entries, student_count = parse_cell_content(content)
            preferred = [name for name, _ in parsed_entries if name]
            assigned = []
            shadows = []

            def can_be_assigned(inst_name, inst_row):
                if not is_available(inst_row, time_cell.value):
                    return False
                if class_name in inst_row.get("Can't Teach", []):
                    return False
                if inst_name in assignments_by_time[time_str]:
                    return False
                return True

            is_psl = "PSL" in class_name.upper()
            needed = len(preferred) if is_psl else 1

            preferred = list(dict.fromkeys(preferred))

            for inst_name in preferred:
                match = availability_df[availability_df['Name'].str.lower() == inst_name.lower()]
                if match.empty:
                    continue
                inst_row = match.iloc[0]
                role = inst_row['Role']
                if not can_be_assigned(inst_name, inst_row):
                    continue
                if role == 'Shadow':
                    if assigned:
                        shadows.append(inst_name)
                        assignments_by_time[time_str].append(inst_name)
                        instructor_assignments[inst_name].append(time_str)
                    continue
                else:
                    assigned.append(inst_name)
                    last_class_by_instructor[inst_name] = class_name
                    assignments_by_time[time_str].append(inst_name)
                    instructor_assignments[inst_name].append(time_str)

            available_pool = availability_df.copy()
            available_pool['Assignments'] = available_pool['Name'].map(lambda name: len(instructor_assignments[name]))
            available_pool = available_pool.sort_values(by='Assignments')

            while len(assigned) < needed:
                filled = False
                for _, inst_row in available_pool.iterrows():
                    inst_name = inst_row['Name']
                    if inst_name in assigned:
                        continue
                    if not can_be_assigned(inst_name, inst_row):
                        continue
                    if inst_row['Role'] == 'Shadow':
                        continue
                    assigned.append(inst_name)
                    last_class_by_instructor[inst_name] = class_name
                    assignments_by_time[time_str].append(inst_name)
                    instructor_assignments[inst_name].append(time_str)
                    filled = True
                    break
                if not filled:
                    break

            for _, inst_row in availability_df.iterrows():
                inst_name = inst_row['Name']
                if inst_name in assigned or inst_name in shadows:
                    continue
                if not can_be_assigned(inst_name, inst_row):
                    continue
                if inst_row['Role'] == 'Shadow' and assigned:
                    shadows.append(inst_name)
                    assignments_by_time[time_str].append(inst_name)
                    instructor_assignments[inst_name].append(time_str)
                    break

            result_lines = []
            for a in assigned:
                line = f"{a} ({student_count})" if not is_psl else f"{a}"
                result_lines.append(line)
            for s in shadows:
                result_lines.append(s)

            formatted_text = "\n".join(result_lines) if result_lines else "unfilled"
            cell.value = formatted_text
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Double up logic and breaks only if not manual mode
    if not manual_mode:
        for i, row in enumerate(ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=len(headers))):
            time_str = str(row[0].value)
            for j, cell in enumerate(row[1:], start=1):
                class_name = headers[j]
                if not class_name:
                    continue
                class_name = class_name.strip()
                if class_name.lower() == "brk":
                    continue
                if not cell.value or cell.value == "unfilled":
                    continue

                current_names = [line.split(" (")[0] for line in str(cell.value).split("\n")]
                parsed_entries, student_count = parse_cell_content(cell.value)
                is_psl = "PSL" in class_name.upper()
                if is_psl or student_count < 5:
                    continue

                if len(current_names) < 2:
                    available_pool = availability_df.copy()
                    available_pool = available_pool.sort_values(by='Name')
                    for _, inst_row in available_pool.iterrows():
                        inst_name = inst_row['Name']
                        if inst_name in current_names:
                            continue
                        if not is_available(inst_row, time_str):
                            continue
                        if inst_row['Role'] == 'Shadow':
                            continue
                        if inst_name in assignments_by_time[time_str]:
                            continue
                        current_names.append(inst_name)
                        assignments_by_time[time_str].append(inst_name)
                        instructor_assignments[inst_name].append(time_str)
                        break

                    updated = "\n".join(current_names)
                    cell.value = updated
                    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        if any(h for h in headers if h and h.lower() == "brk"):
            brk_col = [h.lower() if h else "" for h in headers].index("brk") + 1
            for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                time_str = str(row[0].value)
                not_teaching = []
                for inst_name in instructor_assignments:
                    inst_row = availability_df[availability_df['Name'] == inst_name].iloc[0]
                    if time_str not in instructor_assignments[inst_name] and is_available(inst_row, time_str):
                        not_teaching.append(inst_name)

                required_breaks = [name for name in not_teaching if total_breaks[name] < 1 and len(instructor_assignments[name]) >= 4]
                for name in required_breaks:
                    total_breaks[name] += 1

                row[brk_col - 1].value = ", ".join(not_teaching)
                row[brk_col - 1].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    if manual_mode and any(h for h in headers if h and h.lower() == "brk"):
        brk_col = [h.lower() if h else "" for h in headers].index("brk") + 1
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            time_str = str(row[0].value)
            not_teaching = []
            for inst_name in instructor_assignments:
                inst_row = availability_df[availability_df['Name'] == inst_name].iloc[0]
                if time_str not in instructor_assignments[inst_name] and is_available(inst_row, time_str):
                    not_teaching.append(inst_name)

            row[brk_col - 1].value = ", ".join(not_teaching)
            row[brk_col - 1].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    preview_data = []
    for row in ws.iter_rows(min_row=2, max_col=ws.max_column, values_only=True):
        preview_data.append(row)

    return output, preview_data
