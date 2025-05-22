import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 出欠区分
attendance_options = ["○", "／", "公", "病", "事", "忌", "停", "遅", "早", "保"]

# ファイルパス
attendance_file = "出席ログ.xlsx"
subject_file = "教科一覧.xlsx"
teacher_file = "教師一覧.xlsx"
student_file = "生徒一覧.xlsx"

# ログファイルがなければ初期化
if not os.path.exists(attendance_file):
    pd.DataFrame(columns=["日付", "学年", "組", "番号", "氏名", "教科", "教師", "出欠"]).to_excel(attendance_file, index=False)

# セッションステート
if 'page' not in st.session_state:
    st.session_state.page = '入力'

# サイドバー
page = st.sidebar.radio("表示メニュー", ["入力", "履歴"])
st.session_state.page = page

# データ読み込み
subject_df = pd.read_excel(subject_file)
teacher_df = pd.read_excel(teacher_file)
student_df = pd.read_excel(student_file)

if st.session_state.page == "入力":
    st.title("出席入力")

    subject = st.selectbox("教科を選択", subject_df["教科名"].unique())
    teacher = st.selectbox("担当教師を選択", teacher_df["教師名"].unique())

    classes = student_df[['学年', '組']].drop_duplicates().sort_values(by=['学年', '組'])
    selected_class = st.selectbox("クラスを選択", classes.apply(lambda row: f"{row['学年']}_{row['組']}", axis=1))
    grade, group = selected_class.split('_')

    filtered_students = student_df[(student_df['学年'] == grade) & (student_df['組'] == group)]

    st.subheader(f"{grade} {group} 出席登録")
    date = st.date_input("日付", datetime.today())

    attendance_data = []
    for _, row in filtered_students.iterrows():
        key = f"{row['学年']}_{row['組']}_{row['番号']}"
        status = st.selectbox(
            f"{row['番号']:02d} {row['氏名']}",
            attendance_options,
            index=0,
            key=key
        )
        attendance_data.append({
            "日付": pd.to_datetime(date),
            "学年": row["学年"],
            "組": row["組"],
            "番号": row["番号"],
            "氏名": row["氏名"],
            "教科": subject,
            "教師": teacher,
            "出欠": status
        })

    if st.button("出席を登録"):
        df_new = pd.DataFrame(attendance_data)
        df_log = pd.read_excel(attendance_file)
        df_log = pd.concat([df_log, df_new], ignore_index=True)
        df_log.to_excel(attendance_file, index=False)
        st.success("出席情報を保存しました。")

elif st.session_state.page == "履歴":
    st.title("出席履歴")

    # クラス・期間指定
    classes = student_df[['学年', '組']].drop_duplicates().sort_values(by=['学年', '組'])
    selected_class = st.selectbox("クラスを選択", classes.apply(lambda row: f"{row['学年']}_{row['組']}", axis=1))
    grade, group = selected_class.split('_')

    col1, col2 = st.columns(2)
    start_date = col1.date_input("開始日", datetime(2024, 4, 1))
    end_date = col2.date_input("終了日", datetime.today())

    # ログ読み込み
    df_log = pd.read_excel(attendance_file)
    df_log["日付"] = pd.to_datetime(df_log["日付"])
    df_filtered = df_log[
        (df_log["学年"] == grade) &
        (df_log["組"] == group) &
        (df_log["日付"] >= pd.to_datetime(start_date)) &
        (df_log["日付"] <= pd.to_datetime(end_date))
    ]

    # ピボットで区分ごとの合計集計
    if not df_filtered.empty:
        df_summary = df_filtered.pivot_table(
            index=["番号", "氏名"],
            columns="出欠",
            aggfunc="size",
            fill_value=0
        ).reset_index()

        df_summary = df_summary.sort_values(by="番号")
        st.dataframe(df_summary)

        # CSVエクスポート
        csv = df_summary.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 この集計結果をCSVでダウンロード",
            data=csv,
            file_name=f"{grade}_{group}_出席集計_{start_date}_{end_date}.csv",
            mime="text/csv"
        )
    else:
        st.warning("該当期間にデータがありません。")
