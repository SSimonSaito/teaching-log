import streamlit as st
import pandas as pd
from datetime import datetime

# 学年・組・教科・教師マスタ
grades = ["1年", "2年", "3年"]
classes = ["A組", "B組", "C組", "D組"]
subjects = ["国語", "数学", "英語", "理科", "社会", "音楽", "体育", "美術"]
teachers = ["山田 先生", "佐藤 先生", "高橋 先生", "中村 先生"]

# 生徒名マスタ生成（全クラス20名）
class_roster = {}
for grade in grades:
    for cls in classes:
        class_name = f"{grade}{cls}"
        students = [f"{class_name}{i+1}番" for i in range(20)]
        class_roster[class_name] = students

# セッション状態の初期化
if 'class_data' not in st.session_state:
    st.session_state.class_data = pd.DataFrame(columns=["クラス", "日付", "時限", "教科", "教師", "授業内容", "所感"])

if 'attendance_data' not in st.session_state:
    st.session_state.attendance_data = pd.DataFrame(columns=["クラス", "日付", "時限", "教科", "教師", "生徒名", "出席状況"])

# タイトル
st.title("📘 高校教務手帳 + 出席簿（教師・教科選択付き）")

# --- クラス選択（学年と組の分離） ---
selected_grade = st.selectbox("📚 学年を選択", grades)
selected_class_label = st.selectbox("🏫 組を選択", classes)
selected_class = f"{selected_grade}{selected_class_label}"

# --- 日付・時限の入力 ---
selected_date = st.date_input("📅 日付を選択", datetime.today())
selected_period = st.selectbox("🕐 時限を選択", ["1限", "2限", "3限", "4限", "5限", "6限"])

# --- 教科・教師の選択 ---
selected_subject = st.selectbox("📘 教科を選択", subjects)
selected_teacher = st.selectbox("👨‍🏫 担当教師を選択", teachers)

# --- 授業メモ入力 ---
content = st.text_area("📖 授業内容・メモ")
impression = st.text_area("💭 所感・気づき")

# --- 授業記録 登録ボタン ---
if st.button("💾 授業記録を保存"):
    new_class_record = {
        "クラス": selected_class,
        "日付": selected_date.strftime("%Y-%m-%d"),
        "時限": selected_period,
        "教科": selected_subject,
        "教師": selected_teacher,
        "授業内容": content,
        "所感": impression
    }
    st.session_state.class_data = pd.concat(
        [st.session_state.class_data, pd.DataFrame([new_class_record])],
        ignore_index=True
    )
    st.success("授業記録を保存しました ✅")

# --- 出席簿 入力 ---
st.subheader("🧑‍🎓 出席簿入力")

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
        "教科": selected_subject,
        "教師": selected_teacher,
        "生徒名": student,
        "出席状況": status
    })

if st.button("📝 出席状況を保存"):
    st.session_state.attendance_data = pd.concat(
        [st.session_state.attendance_data, pd.DataFrame(attendance_records)],
        ignore_index=True
    )
    st.success("出席データを保存しました ✅")

# --- 授業記録 表示 ---
st.subheader("📂 授業記録一覧")
filtered_classes = st.multiselect("📚 表示するクラスを選択", list(class_roster.keys()), default=[selected_class])
st.dataframe(st.session_state.class_data[st.session_state.class_data["クラス"].isin(filtered_classes)])

# --- 出席簿 表示 ---
st.subheader("📋 出席簿一覧")
st.dataframe(st.session_state.attendance_data[st.session_state.attendance_data["クラス"].isin(filtered_classes)])

# --- ダウンロードボタン ---
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
