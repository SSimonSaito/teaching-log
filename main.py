import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

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

# PDF生成関数（日本語フォント対応）
def generate_summary_pdf(summary_df, class_name, date_range):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
    c.setFont('HeiseiMin-W3', 14)
    width, height = A4

    c.drawString(20, height - 30, f"{class_name} 出席集計 ({date_range})")

    y = height - 50
    c.setFont('HeiseiMin-W3', 10)
    c.drawString(20, y, "| 生徒名         | " + " | ".join(summary_df.columns) + " |")
    y -= 10
    c.line(20, y, width - 20, y)
    y -= 15

    for student, row in summary_df.iterrows():
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont('HeiseiMin-W3', 10)
            c.drawString(20, y, "| 生徒名         | " + " | ".join(summary_df.columns) + " |")
            y -= 10
            c.line(20, y, width - 20, y)
            y -= 15

        line = f"{student:<15} " + " ".join(str(row.get(col, 0)) for col in summary_df.columns)
        c.drawString(25, y, line)
        y -= 15

    c.save()
    buffer.seek(0)
    return buffer
