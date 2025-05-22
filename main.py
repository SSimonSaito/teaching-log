import streamlit as st
import pandas as pd
from datetime import datetime

# データファイルの読み込み
subject_df = pd.read_excel("data/教科一覧.xlsx")
teacher_df = pd.read_excel("data/教師一覧.xlsx")
students_df = pd.read_excel("data/生徒一覧.xlsx")

# 初期化
if 'attendance_data' not in st.session_state:
    st.session_state.attendance_data = pd.DataFrame(columns=[
        "クラス", "日付", "時限", "教科", "担当教師", "生徒名", "出席状況"
    ])

# ページ構成
st.set_page_config(layout="wide")
st.sidebar.title("📋 メニュー")
page = st.sidebar.radio("表示を選択してください", ["📥 出席入力", "📊 出席履歴"])

grades = sorted(students_df["学年"].unique())
classes = sorted(students_df["組"].unique())

# --- 出席入力ページ ---
if page == "📥 出席入力":
    st.title("📥 出席入力")

    # クラス選択
    col1, col2 = st.columns(2)
    with col1:
        selected_grade = st.selectbox("📚 学年を選択", grades, key="input_grade")
    with col2:
        selected_class = st.selectbox("🏫 組を選択", classes, key="input_class")
    class_name = f"{selected_grade}{selected_class}"

    # 日付・時限・教科・教師
    col3, col4 = st.columns(2)
    with col3:
        selected_date = st.date_input("📅 日付を選択", datetime.today())
    with col4:
        selected_period = st.selectbox("🕐 時限を選択", ["1限", "2限", "3限", "4限", "5限", "6限"])

    col5, col6 = st.columns(2)
    with col5:
        selected_subject = st.selectbox("📘 教科を選択", subject_df["教科"].tolist())
    with col6:
        selected_teacher = st.selectbox("👨‍🏫 担当教師を選択", teacher_df["教師名"].tolist())

    # 該当クラスの生徒抽出
    filtered_students = students_df[
        (students_df["学年"] == selected_grade) &
        (students_df["組"] == selected_class)
    ].sort_values("番号")

    # 出席入力欄
    st.subheader("🧑‍🎓 出席簿入力")
    attendance_records = []
    for _, row in filtered_students.iterrows():
        student_name = row["氏名"]
        status = st.selectbox(
            f"{student_name} の出席状況",
            ["出席", "欠席", "遅刻", "早退"],
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

    if st.button("📝 出席簿を保存"):
        df = pd.DataFrame(attendance_records)
        st.session_state.attendance_data = pd.concat(
            [st.session_state.attendance_data, df], ignore_index=True
        )
        st.success("✅ 出席データを保存しました")

# --- 出席履歴ページ ---
elif page == "📊 出席履歴":
    st.title("📊 出席履歴（集計表示）")

    if st.session_state.attendance_data.empty:
        st.info("まだ出席データが登録されていません。")
    else:
        col1, col2 = st.columns(2)
        with col1:
            selected_grade = st.selectbox("📚 学年を選択", grades, key="hist_grade")
        with col2:
            selected_class = st.selectbox("🏫 組を選択", classes, key="hist_class")
        class_name = f"{selected_grade}{selected_class}"

        col3, col4 = st.columns(2)
        with col3:
            date_from = st.date_input("📆 期間開始日", datetime.today().replace(day=1))
        with col4:
            date_to = st.date_input("📆 期間終了日", datetime.today())

        # フィルタリング
        df = st.session_state.attendance_data.copy()
        df["日付"] = pd.to_datetime(df["日付"])
        df_filtered = df[
            (df["クラス"] == class_name) &
            (df["日付"] >= pd.to_datetime(date_from)) &
            (df["日付"] <= pd.to_datetime(date_to))
        ]

        if df_filtered.empty:
            st.warning("この期間・クラスには出席データがありません。")
        else:
            summary = df_filtered.groupby(["生徒名", "出席状況"]).size().unstack(fill_value=0)
            summary = summary.reindex(columns=["出席", "欠席", "遅刻", "早退"], fill_value=0)
            st.dataframe(summary)
