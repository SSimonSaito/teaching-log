import streamlit as st
import pandas as pd
from datetime import datetime

# クラス・教科・教師リスト
class_roster = {
    "1年A組": ["佐藤 太郎", "鈴木 花子"],
    "2年B組": ["田中 一郎", "高橋 美咲"],
    "3年A組": ["伊藤 健", "山田 美優"]
}

subject_list = ["国語", "数学", "英語", "理科", "社会", "体育", "音楽", "美術"]
teacher_list = ["山田 先生", "佐藤 先生", "高橋 先生", "中村 先生"]

# 初期データ
if 'class_data' not in st.session_state:
    st.session_state.class_data = pd.DataFrame(columns=[
        "クラス", "日付", "時限", "教科", "担当教師", "授業内容", "所感"
    ])

if 'attendance_data' not in st.session_state:
    st.session_state.attendance_data = pd.DataFrame(columns=[
        "クラス", "日付", "時限", "生徒名", "出席状況", "教科", "担当教師"
    ])

st.title("📘 高校教務手帳 + 出席簿 + クラス / 教科 / 教師対応")

# クラス・日付・時限・教科・教師
selected_class = st.selectbox("🏫 クラスを選択", list(class_roster.keys()))
selected_date = st.date_input("📅 日付を選択", datetime.today())
selected_period = st.selectbox("🕐 時限を選択", ["1限", "2限", "3限", "4限", "5限", "6限"])
selected_subject = st.selectbox("📘 教科を選択", subject_list)
selected_teacher = st.selectbox("👨‍🏫 担当教師を選択", teacher_list)

# 授業内容・所感
content = st.text_area("📖 授業内容・メモ")
impression = st.text_area("💭 所感・気づき")

# 授業記録 登録
if st.button("💾 授業記録を保存"):
    new_class_record = {
        "クラス": selected_class,
        "日付": selected_date.strftime("%Y-%m-%d"),
        "時限": selected_period,
        "教科": selected_subject,
        "担当教師": selected_teacher,
        "授業内容": content,
        "所感": impression
    }
    st.session_state.class_data = pd.concat(
        [st.session_state.class_data, pd.DataFrame([new_class_record])],
        ignore_index=True
    )
    st.success("授業記録を保存しました ✅")

# 出席簿入力
st.subheader("🧑‍🎓 出席簿")
attendance_records = []

for student in class_roster[selected_class]:
    status = st.selectbox(
        f"{student} の出席状況",
        ["出席", "欠席", "遅刻", "早退"],
        key=f"{selected_class}_{student}_{selected_date}_{selected_period}"
    )
    attendance_records.append({
        "クラス": selected_class,
        "日付": selected_date.strftime("%Y-%m-%d"),
        "時限": selected_period,
        "生徒名": student,
        "出席状況": status,
        "教科": selected_subject,
        "担当教師": selected_teacher
    })

if st.button("📝 出席状況を保存"):
    st.session_state.attendance_data = pd.concat(
        [st.session_state.attendance_data, pd.DataFrame(attendance_records)],
        ignore_index=True
    )
    st.success("出席データを保存しました ✅")

# 授業記録 表示
st.subheader("📂 授業記録一覧")
st.dataframe(st.session_state.class_data)

# 出席簿 表示
st.subheader("📋 出席簿一覧")
st.dataframe(st.session_state.attendance_data)

# CSV出力
st.download_button(
    label="📥 授業記録 CSV出力",
    data=st.session_state.class_data.to_csv(index=False).encode('utf-8'),
    file_name='授業記録.csv',
    mime='text/csv'
)

st.download_button(
    label="📥 出席簿 CSV出力",
    data=st.session_state.attendance_data.to_csv(index=False).encode('utf-8'),
    file_name='出席簿.csv',
    mime='text/csv'
)
