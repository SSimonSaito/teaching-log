import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

# ------------------- データ読み込み -------------------
subject_df = pd.read_excel("data/教科一覧.xlsx")
teacher_df = pd.read_excel("data/教師一覧.xlsx")
students_df = pd.read_excel("data/生徒一覧.xlsx")

# ------------------- 初期化 -------------------
if 'attendance_data' not in st.session_state:
    st.session_state.attendance_data = pd.DataFrame(columns=[
        "クラス", "日付", "時限", "教科", "担当教師", "生徒名", "出席状況"
    ])

st.set_page_config(layout="wide")
st.sidebar.title("メニュー")
page = st.sidebar.radio("表示を選択してください", ["出席入力", "出席総計", "CSV/PDF出力"])

grades = sorted(students_df["学年"].unique())
classes = sorted(students_df["組"].unique())
attendance_options = ["○", "／", "公", "病", "事", "忌", "停", "遅", "早", "保"]

# PDF生成関数（個人別出席集計）
def generate_summary_pdf(summary_df, class_name, date_range):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(20, height - 30, f"{class_name} 出席集計 ({date_range})")

    y = height - 50
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20, y, "| 生徒名         | " + " | ".join(summary_df.columns) + " |")
    y -= 10
    c.line(20, y, width - 20, y)
    y -= 15

    c.setFont("Helvetica", 10)
    for student, row in summary_df.iterrows():
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica-Bold", 10)
            c.drawString(20, y, "| 生徒名         | " + " | ".join(summary_df.columns) + " |")
            y -= 10
            c.line(20, y, width - 20, y)
            y -= 15
            c.setFont("Helvetica", 10)

        line = f"{student:<15} " + " ".join(str(row.get(col, 0)) for col in summary_df.columns)
        c.drawString(25, y, line)
        y -= 15

    c.save()
    buffer.seek(0)
    return buffer

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
        selected_date = st.date_input("日付", datetime.today())
    with col4:
        selected_period = st.selectbox("時限", ["1限", "2限", "3限", "4限", "5限", "6限"])

    col5, col6 = st.columns(2)
    with col5:
        selected_subject = st.selectbox("教科", subject_df["教科"].tolist())
    with col6:
        selected_teacher = st.selectbox("担当教師", teacher_df["教師名"].tolist())

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
elif page == "出席総計":
    st.title("個人別 出席総計")
    if st.session_state.attendance_data.empty:
        st.info("まだ出席データがありません")
    else:
        df = st.session_state.attendance_data.copy()
        df["日付"] = pd.to_datetime(df["日付"])

        col1, col2 = st.columns(2)
        with col1:
            selected_grade = st.selectbox("学年", grades, key="sum_grade")
        with col2:
            selected_class = st.selectbox("組", classes, key="sum_class")
        class_name = f"{selected_grade}{selected_class}"

        col3, col4 = st.columns(2)
        with col3:
            date_from = st.date_input("集計開始日", datetime.today().replace(day=1))
        with col4:
            date_to = st.date_input("集計終了日", datetime.today())

        filtered = df[(df["クラス"] == class_name) & (df["日付"] >= pd.to_datetime(date_from)) & (df["日付"] <= pd.to_datetime(date_to))]

        if filtered.empty:
            st.warning("この条件に該当するデータがありません")
        else:
            summary = filtered.groupby(["生徒名", "出席状況"]).size().unstack(fill_value=0).reindex(columns=attendance_options, fill_value=0)
            st.dataframe(summary)

            if st.button("この集計結果をPDF出力"):
                date_range = f"{date_from}〜{date_to}"
                pdf_buffer = generate_summary_pdf(summary, class_name, date_range)
                st.download_button(
                    label="PDF出席集計ダウンロード",
                    data=pdf_buffer,
                    file_name=f"{class_name}_出席集計.pdf",
                    mime="application/pdf"
                )

# ------------------- 出力 -------------------
elif page == "CSV/PDF出力":
    st.title("CSV / PDF 出力")
    if st.session_state.attendance_data.empty:
        st.warning("出力するデータがありません")
    else:
        df = st.session_state.attendance_data.copy()
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("CSVダウンロード", data=csv, file_name="出席簿.csv", mime="text/csv")
