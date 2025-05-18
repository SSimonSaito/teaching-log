import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Googleスプレッドシートの認証とデータ取得
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
gc = gspread.authorize(credentials)
worksheet = gc.open_by_key('1RA_Y4PENX_b4DqxYR4qKZhd73j4vczIw6A2DrtFPGaI').sheet1
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Streamlitアプリの構築
st.title("📘 高校教務手帳（iPad対応）")

# クラス選択
grades = ["1年", "2年", "3年"]
classes = ["A組", "B組", "C組", "D組"]
col1, col2 = st.columns(2)
with col1:
    selected_grade = st.selectbox("学年を選択", grades)
with col2:
    selected_class = st.selectbox("組を選択", classes)
class_name = f"{selected_grade}{selected_class}"

# 日付と時限の選択
col3, col4 = st.columns(2)
with col3:
    selected_date = st.date_input("日付を選択", datetime.today())
with col4:
    selected_period = st.selectbox("時限を選択", ["1限", "2限", "3限", "4限", "5限", "6限"])

# 教科と教師の選択
subjects = ["国語", "数学", "英語", "理科", "社会", "音楽", "体育", "美術"]
teachers = ["山田 先生", "佐藤 先生", "高橋 先生", "中村 先生"]
col5, col6 = st.columns(2)
with col5:
    selected_subject = st.selectbox("教科を選択", subjects)
with col6:
    selected_teacher = st.selectbox("担当教師を選択", teachers)

# 授業内容と所感の入力
content = st.text_area("授業内容・メモ")
impression = st.text_area("所感・気づき")

# 保存ボタン
if st.button("授業記録を保存"):
    new_record = {
        "クラス": class_name,
        "日付": selected_date.strftime("%Y-%m-%d"),
        "時限": selected_period,
        "教科": selected_subject,
        "教師": selected_teacher,
        "授業内容": content,
        "所感": impression
    }
    df = df.append(new_record, ignore_index=True)
    st.success("授業記録を保存しました ✅")
