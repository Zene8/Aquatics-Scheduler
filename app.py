# app.py

import streamlit as st
from auth import login_form
from scheduler import generate_am_schedule
from template_parser import parse_template
import pandas as pd
import io
import tempfile
from datetime import datetime
import os
from openpyxl import load_workbook, Workbook, styles
from shutil import copyfile

st.set_page_config(page_title="Swim Scheduler App", layout="wide")

# --- Login Section --- #
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_form()
    st.stop()

st.title("🏊 Swim Instructor Scheduler")

# --- Schedule Input Method --- #
method = st.radio("Choose Input Method", ["Upload Template", "Select Classes Manually"])
st.session_state['source_method'] = method

if method == "Upload Template":
    st.subheader("Upload AM Session Template")
    am_template_file = st.file_uploader("Upload AM Template Excel File", type=["xlsx"])

    if am_template_file:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        tmp.write(am_template_file.read())
        tmp.flush()
        tmp.close()
        st.session_state['am_template_file'] = tmp.name

        # Now parse the uploaded template
        st.session_state['am_template_df'] = parse_template(tmp.name)

        st.success("AM Template uploaded successfully!")
        st.dataframe(st.session_state['am_template_df'], height=300)

elif method == "Select Classes Manually":
    st.subheader("Manually Select Classes With Enrollments")

    blank_template_path = os.path.join("assets", "Blank_MTWT_Template1.xlsx")
    working_copy_path = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx").name
    copyfile(blank_template_path, working_copy_path)

    blank_df = pd.read_excel(working_copy_path, engine="openpyxl")

    time_slots = blank_df.iloc[:, 0].tolist()
    class_columns = blank_df.columns[1:]

    if 'manual_selection' not in st.session_state:
        st.session_state.manual_selection = {
            time: {cls: False for cls in class_columns} for time in time_slots
        }

    for time in time_slots:
        st.markdown(f"#### {time}")
        cols = st.columns(len(class_columns))
        for i, cls in enumerate(class_columns):
            current_val = st.session_state.manual_selection[time][cls]
            new_val = cols[i].checkbox(cls, value=current_val, key=f"{time}_{cls}")
            st.session_state.manual_selection[time][cls] = new_val

    if st.button("Submit Class Enrollment Grid"):
        selected_matrix = pd.DataFrame.from_dict(st.session_state.manual_selection, orient='index')
        selected_matrix.index.name = "Time"
        selected_matrix.reset_index(inplace=True)

        final_template = blank_df.copy()
        for i, time in enumerate(final_template.iloc[:, 0]):
            for cls in class_columns:
                if selected_matrix.loc[i, cls] == True:
                    final_template.loc[i, cls] = "1"

        formatted_wb = load_workbook(working_copy_path)
        formatted_ws = formatted_wb.active

        for r in range(2, len(final_template) + 2):
            for c, cls in enumerate(class_columns, start=2):
                if final_template.iloc[r - 2, c - 1] == "1":
                    formatted_ws.cell(row=r, column=c).value = "1"

        formatted_wb.save(working_copy_path)

        st.session_state['am_template_df'] = final_template
        st.session_state['am_template_file'] = working_copy_path
        st.session_state['manual_mode'] = True

        st.success("Class enrollment matrix created successfully!")
        st.dataframe(final_template, height=400)

# --- Manual Instructor Entry Form --- #
if 'am_template_df' in st.session_state:
    st.subheader("Create AM Schedule")

    num_instructors = st.number_input("How many instructors to add?", min_value=1, max_value=20, value=3)

    instructor_data = []
    for i in range(num_instructors):
        st.markdown(f"### Instructor {i+1}")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(f"Name #{i+1}", key=f"name_{i}")
            start_time = st.time_input(f"AM Start #{i+1}", key=f"start_{i}")
        with col2:
            end_time = st.time_input(f"AM End #{i+1}", key=f"end_{i}")
            cant_teach = st.text_input(f"Can't Teach Classes (comma-separated) #{i+1}", key=f"cant_{i}")

        role = st.selectbox(f"Role #{i+1}", ["Instructor", "Shadow"], key=f"role_{i}")

        instructor_data.append({
            "Name": name,
            "AM Start": start_time,
            "AM End": end_time,
            "Can't Teach": cant_teach,
            "Role": role
        })

    if st.button("Generate AM Schedule"):
        availability_df = pd.DataFrame(instructor_data)
        st.write("Availability Preview:")
        st.dataframe(availability_df)

        am_template_df = st.session_state.get('am_template_df')
        am_template_file = st.session_state.get('am_template_file')
        manual_mode = st.session_state.get('manual_mode', False)

        if am_template_df is None or am_template_file is None or not os.path.exists(am_template_file):
            st.error("No valid template file path available.")
            st.stop()

        output_stream, output_preview = generate_am_schedule(
            am_template_df,
            availability_df,
            am_template_file,
            manual_mode
        )

        st.subheader("Generated Schedule Preview")
        st.dataframe(pd.DataFrame(output_preview))

        st.download_button(
            label="📅 Download Schedule",
            data=output_stream,
            file_name="AM_Schedule_Output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

st.subheader("Create PM Schedule")
st.warning("🚧 PM scheduling is still in progress. Coming soon!")
