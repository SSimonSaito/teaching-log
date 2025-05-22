import streamlit as st
import pandas as pd
from datetime import datetime

# セッションステートの初期化
if 'page' not in st.session_state:
    st.session_state.page = '入力'

# サイドバーのメニュー
page = st.sidebar.radio("表示メニュー", ["入力", "履歴"])
st.session_state.page = page

# データの読み込み
subject_df = pd.read_excel("教科一覧.xlsx")
teacher_df = pd.read_excel("教師一覧.xlsx")
student_df = pd.read_excel("生徒一覧.xlsx")

# メイン画面
if st.session_state.page == "入力":
    st.title("出席入力画面")

    # 教科と教師の選択
    subject = st.selectbox("教科を選択", subject_df["教科名"].unique())
    teacher = st.selectbox("担当教師を選択", teacher_df["教師名"].unique())

    # 学年・組の一覧取得
    classes = student_df[['学年', '組']].drop_duplicates().sort_values(by=['学年', '組'])

    selected_class = st.selectbox("クラスを選択", classes.apply(lambda row: f"{row['学年']}_{row['組']}", axis=1))

    # クラスでフィルタ
    grade, group = selected_class.split('_')
    filtered_students = student_df[(student_df['学年'] == grade) & (student_df['組'] == group)]

    st.subheader(f"{grade} {group} の生徒一覧")
    for _, row in filtered_students.iterrows():
        st.checkbox(f"{row['番号']:02d} {row['氏名']}")

    if st.button("出席を登録"):
        st.success("出席情報が登録されました（ダミー）")

elif st.session_state.page == "履歴":
    st.title("出席履歴")

    # クラスの選択
    selected_class = st.selectbox("クラスを選択（履歴）", student_df[['学年', '組']].drop_duplicates().apply(lambda row: f"{row['学年']}_{row['組']}", axis=1))
    grade, group = selected_class.split('_')
    filtered_students = student_df[(student_df['学年'] == grade) & (student_df['組'] == group)]

    # 期間指定（モック）
    col1, col2 = st.columns(2)
    start_date = col1.date_input("開始日", datetime(2024, 4, 1))
    end_date = col2.date_input("終了日", datetime.today())

    st.subheader(f"{grade} {group} の出席履歴（モック表示）")
    st.write(f"{start_date} から {end_date} までの出席データ")

    # ダミー履歴表示
    for _, row in filtered_students.iterrows():
        st.write(f"{row['番号']:02d} {row['氏名']}：出席日数（モック） = {27 + (_ % 4)} 日")

