import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

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
st.sidebar.title("📋 メニュー")
page = st.sidebar.radio("表示を選択してください", ["\ud83d\udcc5 出席入力", "\ud83d\udcca 出席総計", "\ud83d\udcc4 CSV/PDF出力"])

grades = sorted(students_df["学年"].unique())
classes = sorted(students_df["組"].unique())
attendance_options = ["○", "／", "公", "病", "事", "忌", "停", "遅", "早", "保"]

# ------------------- 出席入力 -------------------
if page == "\ud83d\udcc5 出席入力":
    st.title("\ud83d\udcc5 出席入力")

    col1, col2 = st.columns(2)
    with col1:
        selected_grade = st.selectbox("\ud83d\udcda 学年", grades, key="input_grade")
    with col2:
        selected_class = st.selectbox("\ud83c\udfe7 組", classes, key="input_class")
    class_name = f"{selected_grade}{selected_class}"

    col3, col4 = st.columns(2)
    with col3:
        selected_date = st.date_input("\ud83d\uddd3️ 日付", datetime.today())
    with col4:
        selected_period = st.selectbox("\ud83d\udd52 時限", ["1限", "2限", "3限", "4限", "5限", "6限"])

    col5, col6 = st.columns(2)
    with col5:
        selected_subject = st.selectbox("\ud83d\udcd8 教科", subject_df["教科"].tolist())
    with col6:
        selected_teacher = st.selectbox("\ud83d\udc68‍\ud83c\udfeb 担当教師", teacher_df["教師名"].tolist())

    filtered_students = students_df[(students_df["学年"] == selected_grade) & (students_df["組"] == selected_class)].sort_values("番号")

    st.subheader("\ud83e\uddd3 出席管理")
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

    if st.button("\ud83d\udcdd 保存"):
        df = pd.DataFrame(attendance_records)
        st.session_state.attendance_data = pd.concat([st.session_state.attendance_data, df], ignore_index=True)
        st.success("保存しました！")

# ------------------- 出席統計 -------------------
elif page == "\ud83d\udcca 出席総計":
    st.title("\ud83d\udcca 週/月別 出席総計")
    if st.session_state.attendance_data.empty:
        st.info("まだ出席データがありません")
    else:
        df = st.session_state.attendance_data.copy()
        df["日付"] = pd.to_datetime(df["日付"])
        df["週"] = df["日付"].dt.to_period("W").astype(str)
        df["月"] = df["日付"].dt.to_period("M").astype(str)

        st.subheader("\ud83d\uddd3️ 週別")
        weekly = df.groupby(["週", "出席状況"]).size().unstack(fill_value=0)
        st.dataframe(weekly)

        st.subheader("\ud83d\udcc5 月別")
        monthly = df.groupby(["月", "出席状況"]).size().unstack(fill_value=0)
        st.dataframe(monthly)

# ------------------- 出力 -------------------
elif page == "\ud83d\udcc4 CSV/PDF出力":
    st.title("\ud83d\udcc4 出力")
    if st.session_state.attendance_data.empty:
        st.warning("CSVまたはPDFに出力するデータがありません")
    else:
        df = st.session_state.attendance_data.copy()
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("\ud83d\udcc2 CSVダウンロード", data=csv, file_name="出席簿.csv", mime="text/csv")

        # PDF生成
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, height - 30, "出席簿 PDF")

        y = height - 50
        c.setFont("Helvetica-Bold", 10)
        headers = ["日付", "生徒名", "出席状況"]
        for i, header in enumerate(headers):
            c.drawString(50 + i * 150, y, header)

        c.setFont("Helvetica", 10)
        for i, row in df.iterrows():
            y -= 15
            if y < 50:
                c.showPage()
                y = height - 50
            c.drawString(50, y, str(row["日付"]))
            c.drawString(200, y, row["生徒名"])
            c.drawString(350, y, row["出席状況"])

        c.save()
        pdf = buffer.getvalue()
        st.download_button("\ud83d\udcc4 PDFダウンロード", data=pdf, file_name="出席簿.pdf", mime="application/pdf")