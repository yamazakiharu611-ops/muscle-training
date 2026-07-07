from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# 部位ごとの種目データ
EXERCISE_DATA = {
    '胸': ['ベンチプレス', 'インクラインダンベルプレス', 'ダンベルフライ', 'プッシュアップ'],
    '腕': ['バーベルカール', 'インクラインダンベルカール', 'スカルクラッシャー'],
    '肩': ['ショルダープレス', 'サイドレイズ', 'フロントレイズ'],
    '背中': ['デッドリフト', 'ラットプルダウン', '懸垂（チンニング）'],
    '足': ['スクワット', 'レッグプレス', 'レッグエクステンション']
}

records = []

# 1RM（最大挙上重量）計算
def calculate_1rm(weight, reps):
    if reps == 1: return weight
    return round(weight * (1 + reps / 30), 1)

# BMI計算
def calculate_bmi(height_cm, weight_kg):
    if height_cm <= 0: return 0
    height_m = height_cm / 100
    return round(weight_kg / (height_m * height_m), 1)

# 身長・体重・性別をベースにした目標重量計算（体重比ロジック）
def calculate_target_weights(gender, body_weight, exercise):
    # 種目ごとの体重倍率 [初級, 中級, 上級]
    if exercise == 'ベンチプレス':
        factors = [0.7, 1.0, 1.5] if gender == 'male' else [0.35, 0.5, 0.75]
    elif exercise == 'スクワット':
        factors = [1.0, 1.5, 2.0] if gender == 'male' else [0.6, 1.0, 1.4]
    elif exercise == 'デッドリフト':
        factors = [1.2, 1.8, 2.3] if gender == 'male' else [0.7, 1.2, 1.7]
    else:
        # その他の種目（ダンベルやマシンなど）の標準目安
        factors = [0.4, 0.6, 0.9] if gender == 'male' else [0.2, 0.35, 0.5]
        
    return {
        '初級者': round(body_weight * factors[0], 1),
        '中級者': round(body_weight * factors[1], 1),
        '上級者': round(body_weight * factors[2], 1)
    }

@app.route('/')
def index():
    return render_template('index.html', records=records)

@app.route('/record', methods=['GET', 'POST'])
def record():
    if request.method == 'POST':
        if 'add_exercise' in request.form:
            new_part = request.form.get('new_part')
            new_exercise = request.form.get('new_exercise').strip()
            if new_exercise and new_exercise not in EXERCISE_DATA[new_part]:
                EXERCISE_DATA[new_part].append(new_exercise)
            return redirect(url_for('record'))

        date = request.form.get('date')
        part = request.form.get('part')
        exercise = request.form.get('exercise')
        weight = float(request.form.get('weight'))
        reps = int(request.form.get('reps'))
        height = float(request.form.get('height'))
        
        rm = calculate_1rm(weight, reps)
        bmi = calculate_bmi(height, weight)
        
        records.append({
            'date': date, 'part': part, 'exercise': exercise, 
            'weight': weight, 'reps': reps, 'height': height, 
            'rm': rm, 'bmi': bmi
        })
        return redirect(url_for('index'))
        
    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('record.html', today=today, exercise_data=EXERCISE_DATA)

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    target_weights = None
    selected_level = None
    calculated_target = None
    bmi_result = None
    bmi_status = None
    
    all_exercises = []
    for exercises in EXERCISE_DATA.values(): all_exercises.extend(exercises)
    all_exercises = sorted(list(set(all_exercises)))

    if request.method == 'POST':
        gender = request.form.get('gender')
        body_weight = float(request.form.get('body_weight'))
        height = float(request.form.get('height'))
        exercise = request.form.get('exercise')
        selected_level = request.form.get('level')
        
        # 各種計算の実行
        target_weights = calculate_target_weights(gender, body_weight, exercise)
        calculated_target = target_weights.get(selected_level)
        bmi_result = calculate_bmi(height, body_weight)
        
        # BMI判定
        if bmi_result < 18.5: bmi_status = "低体重（やせ型）"
        elif bmi_result < 25.0: bmi_status = "普通体重（標準）"
        else: bmi_status = "肥満（筋肉量が多い可能性もあります）"

    return render_template('calculate.html', 
                           all_exercises=all_exercises, 
                           target_weights=target_weights,
                           selected_level=selected_level,
                           calculated_target=calculated_target,
                           bmi_result=bmi_result,
                           bmi_status=bmi_status)

if __name__ == '__main__':
    app.run(debug=True)