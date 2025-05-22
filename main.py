import streamlit as st
import pandas as pd
from datetime import datetime

# Excelファイルの読み込み
EXCEL_PATH = "data/出席簿_再現.xlsx"
df_excel = pd.read_excel(EXCEL_PATH, sheet_name=0, header=None)

# 教科・教師情報の取得（行2: 教科, 行3: 教師）
subject_row = df_excel.iloc[2].dropna().tolist()[1:]  # 1列目は見出し除外
teacher_row = df_excel.iloc[3].dropna().tolist()[1:]

# UI構成
st.set_page_config(layout="wide")
st.title("📘 高校教務手帳（iPad対応 / Excel連携）")

# クラス選択
grades = ["1年", "2年", "3年"]
classes = ["A組", "B組", "C組", "D組"]
col1, col2 = st.columns(2)
with col1:
    selected_grade = st.selectbox("📚 学年を選択", grades)
with col2:
    selected_class = st.selectbox("🏫 組を選択", classes)
class_name = f"{selected_grade}{selected_class}"

# 日付・時限
col3, col4 = st.columns(2)
with col3:
    selected_date = st.date_input("📅 日付を選択", datetime.today())
with col4:
    selected_period = st.selectbox("🕐 時限を選択", ["1限", "2限", "3限", "4限", "5限", "6限"])

# 教科・教師情報の表示（読み取り専用）
col5, col6 = st.columns(2)
with col5:
    st.markdown("### 📘 教科一覧")
    st.write(subject_row)
with col6:
    st.markdown("### 👨‍🏫 担当教師一覧")
    st.write(teacher_row)

# 出席簿セクション
st.subheader("🧑‍🎓 出席簿入力")

# 仮の生徒名20人
students = [f"{class_name}{i+1}番" for i in range(20)]
attendance_records = []

for student in students:
    status = st.selectbox(
        f"{student} の出席状況",
        ["出席", "欠席", "遅刻", "早退"],
        key=f"{class_name}_{student}_{selected_date}_{selected_period}"
    )
    attendance_records.append({
        "クラス": class_name,
        "日付": selected_date.strftime("%Y-%m-%d"),
        "時限": selected_period,
        "生徒名": student,
        "出席状況": status
    })

# 保存ボタン
if st.button("📝 出席簿を保存してCSV出力"):
    df = pd.DataFrame(attendance_records)
    st.success("✅ 出席簿を保存しました")
    st.download_button(
        label="📥 出席簿CSVダウンロード",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f"{class_name}_出席簿_{selected_date}.csv",
        mime="text/csv"
    )
