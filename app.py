import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 保存先CSVファイルのパス
CSV_FILE = 'workout_records.csv'

# アプリ起動時にCSVファイルが存在しない場合は、ヘッダーのみ作成
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=['日付', '種目名', '重量(kg)', '回数'])
    df_init.to_csv(CSV_FILE, index=False)

st.title("🏋️ 筋トレ記録＆目標管理アプリ")

# --- 1. 体型データ入力と目標重量計算 ---
st.header("1. 体型データと目標重量")
col1, col2 = st.columns(2)
with col1:
    height = st.number_input("身長 (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.1)
with col2:
    weight = st.number_input("体重 (kg)", min_value=30.0, max_value=200.0, value=65.0, step=0.1)

# 目標重量の算出ロジック（体重をベースにした目安）
target_bench = weight * 0.8
target_squat = weight * 1.2
target_deadlift = weight * 1.2

st.subheader("💡 あなたへのおすすめ目標重量")
st.markdown(f"""
- **ベンチプレス**: `{target_bench:.1f} kg`
- **スクワット**: `{target_squat:.1f} kg`
- **デッドリフト**: `{target_deadlift:.1f} kg`
""")
st.caption("※目標重量は一般的な初心者の目安（体重比）として算出しています。")

st.divider() # 区切り線

# --- 2. 筋トレ実績の入力と保存 ---
st.header("2. 実績の記録")
with st.form("record_form"):
    date = st.date_input("日付", value=datetime.today())
    exercise = st.selectbox("種目名", ["ベンチプレス", "スクワット", "デッドリフト", "その他"])
    weight_val = st.number_input("重量 (kg)", min_value=0.0, max_value=500.0, value=20.0, step=2.5)
    reps = st.number_input("回数 (レップ数)", min_value=1, max_value=100, value=10, step=1)
    
    submit_button = st.form_submit_button("保存する")

if submit_button:
    # フォームが送信されたら、データをDataFrameにしてCSVに追記
    new_data = pd.DataFrame({
        '日付': [date],
        '種目名': [exercise],
        '重量(kg)': [weight_val],
        '回数': [reps]
    })
    new_data.to_csv(CSV_FILE, mode='a', header=False, index=False)
    st.success("✨ 記録を保存しました！")

st.divider()

# --- 3. 過去の記録一覧表示 ---
st.header("3. 過去の記録一覧")
try:
    # CSVからデータを読み込んで表示
    df_records = pd.read_csv(CSV_FILE)
    if not df_records.empty:
        # 最新の記録が上に来るように逆順で表示
        st.dataframe(df_records.iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("まだ記録がありません。最初の記録を追加してみましょう！")
except Exception as e:
    st.error("データの読み込みにエラーが発生しました。")