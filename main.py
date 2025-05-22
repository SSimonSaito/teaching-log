import streamlit as st
import pandas as pd
from datetime import datetime
import io

# ------------------- データ読み込み -------------------
subject_df = pd.read_excel("data/教科一覧.xlsx")
teacher_df = pd.read_excel("data/教師一覧.xlsx")
students_df = pd.read_excel("data/生徒一覧.xlsx")
timetable_df = pd.read_excel("data/時間割マスタ.xlsx")

# ------------------- 初期化 -------------------
if 'attendance_data' not in st.session_state:
    st.session_state.attendance_data = pd.DataFrame(columns=[
        "クラス", "日付", "時限", "教科", "担当教師", "生徒名", "出席状況"
    ])

st.set_page_config(layout="wide")
st.sidebar.title("メニュー")
page = st.sidebar.radio("表示を選択してください", ["出席入力", "出席入力（教師固定）", "出席総計"])

grades = sorted(students_df["学年"].unique())
classes = sorted(students_df["組"].unique())
attendance_options = ["○", "／", "公", "病", "事", "忌", "停", "遅", "早", "保"]

# ------------------- 出席入力（教師固定） -------------------
if page == "出席入力（教師固定）":
    st.title("出席入力（教師固定）")
    selected_date = st.date_input("日付", datetime.today(), key="teacher_fixed_date")
    selected_teacher = st.selectbox("教師名を選択", teacher_df["教師名"].tolist(), key="teacher_fixed_name")

    weekday_str = ["月", "火", "水", "木", "金", "土", "日"][selected_date.weekday()]
    teacher_classes = timetable_df[
        (timetable_df["曜日"] == weekday_str) &
        (timetable_df["教師"] == selected_teacher)
    ].sort_values("時限")

    st.subheader(f"{selected_teacher} の担当一覧（{selected_date.strftime('%Y-%m-%d')} {weekday_str}曜日）")
    for _, row in teacher_classes.iterrows():
        label = f"{row['時限']}：{row['学年']}{row['組']}（{row['教科']}）"
        if st.button(label):
            selected_period = row['時限']
            selected_grade = row['学年']
            selected_class = row['組']
            selected_subject = row['教科']

            class_name = f"{selected_grade}{selected_class}"
            filtered_students = students_df[(students_df["学年"] == selected_grade) & (students_df["組"] == selected_class)].sort_values("番号")

            st.subheader(f"{class_name} - {selected_period} 出席簿入力")
            attendance_records = []
            for _, stu in filtered_students.iterrows():
                student_name = stu["氏名"]
                status = st.selectbox(
                    f"{student_name} の出席状況",
                    attendance_options,
                    index=0,
                    key=f"{class_name}_{student_name}_{selected_date}_{selected_period}_teacher"
                )
                attendance_records.append({
                    "クラス": class_name,
                    "日付": selected_date.strftime("%Y-%m-%d"),
                    "時限": selected_period,
                    "教科": selected_subject,
                    "担当教師": selected_teacher,
                    "生徒名": student_name,
                    "出席状況": status
                })

            if st.button(f"{class_name} {selected_period} 保存"):
                df = pd.DataFrame(attendance_records)
                st.session_state.attendance_data = pd.concat([st.session_state.attendance_data, df], ignore_index=True)
                st.success(f"{class_name} {selected_period} を保存しました！")

# （出席入力および出席総計の既存コードはそのまま維持）
