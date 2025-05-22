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

    if 'active_period' not in st.session_state:
        st.session_state.active_period = None
    if 'teacher_fixed_saved' not in st.session_state:
        st.session_state.teacher_fixed_saved = set()

    weekday_str = ["月", "火", "水", "木", "金", "土", "日"][selected_date.weekday()]
    teacher_classes = timetable_df[
        (timetable_df["曜日"] == weekday_str) &
        (timetable_df["教師"] == selected_teacher)
    ].sort_values("時限")

    st.subheader(f"{selected_teacher} の担当一覧（{selected_date.strftime('%Y-%m-%d')} {weekday_str}曜日）")
    for _, row in teacher_classes.iterrows():
        selected_period = row['時限']
        selected_grade = row['学年']
        selected_class = row['組']
        selected_subject = row['教科']
        class_name = f"{selected_grade}{selected_class}"

        key_id = f"{selected_date}_{selected_period}_{class_name}"
        saved = any(
            (st.session_state.attendance_data["クラス"] == class_name) &
            (st.session_state.attendance_data["日付"] == selected_date.strftime("%Y-%m-%d")) &
            (st.session_state.attendance_data["時限"] == selected_period)
        )
        label = f"{selected_period}：{class_name}（{selected_subject}）"
        if saved:
            label = f"✅ {label}"

                btn_color = "lightgreen" if saved else "white"
        with st.container():
            st.markdown(f"<div style='background-color:{btn_color}; padding:10px; border-radius:5px;'>", unsafe_allow_html=True)
            if st.button(label, key=f"button_{key_id}"):
                st.session_state.active_period = key_id
            st.markdown("</div>", unsafe_allow_html=True)
            st.session_state.active_period = key_id

        if st.session_state.active_period == key_id:
            st.markdown(f"### {class_name} - {selected_period} 出席簿入力")
            filtered_students = students_df[
                (students_df["学年"] == selected_grade) & (students_df["組"] == selected_class)
            ].sort_values("番号")

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

            if key_id not in st.session_state.teacher_fixed_saved:
                if st.button(f"{class_name} {selected_period} 保存", key=f"save_{key_id}"):
                    df = pd.DataFrame(attendance_records)
                    exists = ~st.session_state.attendance_data[
                        (st.session_state.attendance_data["クラス"] == class_name) &
                        (st.session_state.attendance_data["日付"] == selected_date.strftime("%Y-%m-%d")) &
                        (st.session_state.attendance_data["時限"] == selected_period)
                    ].index
                    if exists.any():
                        st.session_state.attendance_data = pd.concat([st.session_state.attendance_data, df], ignore_index=True)
                        st.success(f"{class_name} {selected_period} を保存しました！")
                        st.session_state.teacher_fixed_saved.add(key_id)
                    else:
                        st.warning("すでに保存済みです。")
            else:
                if st.button(f"このデータを削除（管理者用）", key=f"delete_{key_id}"):
                    before = len(st.session_state.attendance_data)
                    st.session_state.attendance_data = st.session_state.attendance_data[
                        ~(
                            (st.session_state.attendance_data["クラス"] == class_name) &
                            (st.session_state.attendance_data["日付"] == selected_date.strftime("%Y-%m-%d")) &
                            (st.session_state.attendance_data["時限"] == selected_period)
                        )
                    ]
                    after = len(st.session_state.attendance_data)
                    st.session_state.teacher_fixed_saved.discard(key_id)
                    st.success(f"削除しました（{before - after} 件）")
                else:
                    st.info("この授業はすでに保存されています。")

# ------------------- 出席入力 -------------------
if page == "出席入力":
    st.title("出席入力")

    col1, col2 = st.columns(2)
    with col1:
        selected_grade = st.selectbox("学年", grades, key="input_grade")
    with col2:
        selected_class = st.selectbox("組", classes, key="input_class")
    class_name = f"{selected_grade}{selected_class}"

    col3, col4 = st.columns(2)
    with col3:
        selected_date = st.date_input("日付", datetime.today(), key="input_date")
    with col4:
        selected_period = st.selectbox("時限", ["1限", "2限", "3限", "4限", "5限", "6限"], key="input_period")

    weekday_str_display = ["月", "火", "水", "木", "金", "土", "日"][selected_date.weekday()]
    st.markdown(f"**選択した日付の曜日：{weekday_str_display}曜日**")

    tt_row = timetable_df[
        (timetable_df["曜日"] == weekday_str_display) &
        (timetable_df["学年"] == selected_grade) &
        (timetable_df["組"] == selected_class) &
        (timetable_df["時限"] == selected_period)
    ]

    if not tt_row.empty:
        default_subject = tt_row.iloc[0]["教科"]
        default_teacher = tt_row.iloc[0]["教師"]
    else:
        default_subject = subject_df["教科"].iloc[0]
        default_teacher = teacher_df["教師名"].iloc[0]

    col5, col6 = st.columns(2)
    with col5:
        selected_subject = st.selectbox("教科", subject_df["教科"].tolist(), index=subject_df["教科"].tolist().index(default_subject) if default_subject in subject_df["教科"].tolist() else 0, key="input_subject")
    with col6:
        selected_teacher = st.selectbox("担当教師", teacher_df["教師名"].tolist(), index=teacher_df["教師名"].tolist().index(default_teacher) if default_teacher in teacher_df["教師名"].tolist() else 0, key="input_teacher")

    filtered_students = students_df[(students_df["学年"] == selected_grade) & (students_df["組"] == selected_class)].sort_values("番号")

    st.subheader("出席簿入力")
    attendance_records = []
    for _, row in filtered_students.iterrows():
        student_name = row["氏名"]
        status = st.selectbox(
            f"{student_name} の出席状況",
            attendance_options,
            index=0,
            key=f"{class_name}_{student_name}_{selected_date}_{selected_period}"
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

    if st.button("保存"):
        df = pd.DataFrame(attendance_records)
        st.session_state.attendance_data = pd.concat([st.session_state.attendance_data, df], ignore_index=True)
        st.success("保存しました！")

# ------------------- 出席総計 -------------------
if page == "出席総計":
    st.title("出席総計")

    col1, col2 = st.columns(2)
    with col1:
        selected_grade = st.selectbox("学年を選択", grades, key="summary_grade")
    with col2:
        selected_class = st.selectbox("組を選択", classes, key="summary_class")
    class_name = f"{selected_grade}{selected_class}"

    col3, col4 = st.columns(2)
    with col3:
        date_from = st.date_input("集計開始日", datetime.today().replace(day=1))
    with col4:
        date_to = st.date_input("集計終了日", datetime.today())

    df = st.session_state.attendance_data.copy()
    df["日付"] = pd.to_datetime(df["日付"])
    df_filtered = df[
        (df["クラス"] == class_name) &
        (df["日付"] >= pd.to_datetime(date_from)) &
        (df["日付"] <= pd.to_datetime(date_to))
    ]

    if df_filtered.empty:
        st.warning("指定された条件に該当する出席データがありません。")
    else:
        students = students_df[
            (students_df["学年"] == selected_grade) &
            (students_df["組"] == selected_class)
        ].sort_values("番号")["氏名"].tolist()

        day_summary = []
        for student in students:
            student_df = df_filtered[df_filtered["生徒名"] == student]
            per_day = student_df.groupby("日付")["出席状況"].apply(list)
            summary = {k: 0 for k in attendance_options}
            total_days = 0
            for statuses in per_day:
                total_days += 1
                if all(s == "○" for s in statuses):
                    summary["○"] += 1
                elif any(s == "遅" for s in statuses):
                    summary["遅"] += 1
                else:
                    for code in ["病", "忌", "停", "事", "保", "公", "／"]:
                        if code in statuses:
                            summary[code] += 1
                            break
                    else:
                        summary["／"] += 1
            summary["生徒名"] = student
            summary["登校日数"] = total_days
            summary["出席率(%)"] = round(100 * summary["○"] / total_days, 1) if total_days else 0
            day_summary.append(summary)

        summary_df = pd.DataFrame(day_summary).fillna(0)
        columns_order = ["生徒名", "登校日数", "出席率(%)"] + [k for k in attendance_options if k in summary_df.columns]
        summary_df = summary_df[columns_order]
        st.subheader("個人別出席統計")
        st.dataframe(summary_df)

        csv = summary_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 出席集計CSVダウンロード",
            data=csv,
            file_name=f"{class_name}_出席集計.csv",
            mime="text/csv"
        )

        st.subheader("教師別・教科別 集計")
        teacher_group = df_filtered.groupby("担当教師")["生徒名"].count().reset_index(name="記録数")
        subject_group = df_filtered.groupby("教科")["生徒名"].count().reset_index(name="記録数")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 教師別 授業記録数")
            st.dataframe(teacher_group)
        with col2:
            st.markdown("#### 教科別 授業記録数")
            st.dataframe(subject_group)
