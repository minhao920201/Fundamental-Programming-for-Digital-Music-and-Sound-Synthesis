from flask import Flask, render_template, request, jsonify, send_file
import music21 as m21
import random
import copy

app = Flask(__name__)

# 儲存每個樂器對應的音符記錄
instrument_data = {
    "piano": [],
    "violin": [],
    "flute": [],
    "guitar": [],
    "bass": [],
    "altoSaxophone": []
}

# 音符對應的音高
notes_mapping = {
    "A": "A5",  # La
    "B": "B5",  # Si
    "C": "C5",  # Do
    "D": "D5",  # Re
    "E": "E5",  # Mi
    "F": "F5",  # Fa
    "G": "G5"   # Sol
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/favicon.ico')
def favicon():
    return '', 204  # 返回 204 No Content


# 接收前端按下的音符和樂器，記錄音符到對應樂器。
@app.route("/update_instrument", methods=["POST"])
def update_instrument():
    data = request.get_json()
    instrument = data.get("instrument")
    note = data.get("note")

    if instrument and note and instrument in instrument_data:
        instrument_data[instrument].append(notes_mapping[note])
        return jsonify({"message": f"Note '{notes_mapping[note]}' added to {instrument}"}), 200
    return jsonify({"message": "Invalid data"}), 400

# 定義一個global variable來儲存隨機狀態
random_mode = False

@app.route('/toggle_random', methods=['POST'])
def toggle_random():
    global random_mode
    data = request.get_json()
    if 'random' in data:
        random_mode = data['random'] == 'on'  # 更新隨機狀態
        return jsonify({"message": "Random mode updated", "status": random_mode})
    else:
        return jsonify({"error": "Invalid request"}), 400


# 根據記錄的音符為每個樂器生成音樂，並保存為 MIDI 檔案。
@app.route("/generate_music", methods=["POST"])
def generate_music():
    global random_mode
    # random: ON
    if random_mode:
        
        # 創建總譜
        score = m21.stream.Score()
        available_notes = [72, 74, 76, 77, 79, 81, 83]

        # 遍歷每個樂器的音符數據
        for instrument_name, notes in instrument_data.items():
            if notes:  # 如果該樂器有音符數據
                # 音階設定為該樂器儲存的音符 MIDI 編碼
                sc = [m21.note.Note(n).pitch.midi for n in notes]  # 將音符轉為 MIDI pitch
                idx = 2  # 起始音符索引
                measure_count = 48  # 總小節數

                # 創建樂器聲部
                part = m21.stream.Part()

                # 加入樂器類型
                if instrument_name == "piano":
                    part.append(m21.instrument.Piano())
                elif instrument_name == "violin":
                    part.append(m21.instrument.Violin())
                elif instrument_name == "flute":
                    part.append(m21.instrument.Flute())
                elif instrument_name == "guitar":
                    part.append(m21.instrument.Guitar())
                elif instrument_name == "bass":
                    part.append(m21.instrument.Bass())
                elif instrument_name == "altoSaxophone":
                    part.append(m21.instrument.AltoSaxophone())
                
                # 如果使用者輸入少於5個note隨機加note進去
                while len(sc) < 5:
                    note_to_add = random.choice(available_notes)
                    sc.append(note_to_add)


                # 和弦生成邏輯
                def generate_chord(idx, scale):
                    """根據當前索引生成三和弦（根音、三度音、五度音）。"""
                    root = scale[idx]
                    third = scale[(idx + 2) % len(scale)]  # 三度
                    fifth = scale[(idx + 4) % len(scale)]  # 五度
                    return m21.chord.Chord([root, third, fifth])

                # 主旋律生成迴圈
                total_notes = measure_count * 4  # 每小節 4 拍，總共的音符數
                for i in range(total_notes):
                    # 隨機生成和弦或單音
                    if random.randint(0, 4) > 0:  # 大部分生成和弦
                        current_chord = generate_chord(idx, sc)
                        current_chord.quarterLength = random.choice([0.5, 1, 2])  # 長度為 0.5, 1 或 2 拍
                        part.append(current_chord)
                    else:  # 偶爾生成單音
                        midi_pitch = sc[idx]
                        single_note = m21.note.Note(midi_pitch)
                        single_note.quarterLength = random.choice([0.5, 1, 2])  # 長度為 0.5, 1 或 2 拍
                        part.append(single_note)

                    # 隨機變化音高索引
                    dice = random.randint(-1, 1)
                    idx += dice
                    if idx < 0 or idx >= len(sc):
                        idx = random.randint(2, len(sc) - 3)  # 確保索引在有效範圍內

                    # 隨機插入休止符，模仿自然節奏
                    if random.randint(0, 3) == 0:  # 約 25% 機率加入休止符
                        rest = m21.note.Rest()
                        rest.quarterLength = random.choice([0.5, 1, 1.5, 2])  # 休止符長度多樣化
                        part.append(rest)

                # 將生成的樂器聲部加入總譜
                score.append(part)

        # 保存為 MIDI 檔案
        output_file = "static/generated_music.mid"
        score.write("midi", fp=output_file)

    # random: OFF
    else:
        piano_notes = set(instrument_data["piano"])
        violin_notes = instrument_data["violin"]

        # If the notes C, D, and E in piano list then use 小魔女doremi.mid sampling note and generate music
        if {"C5", "D5", "E5"}.issubset(piano_notes):
            # 使用指定 MIDI 文件生成特定音樂
            myFile1 = m21.converter.parse("小魔女doremi.midi")
            iter_times = 50
            consecutive_note_num = 4
            s = m21.stream.Stream()
            for _ in range(iter_times):
                idx = random.randint(0, len(myFile1.flat.notesAndRests) - consecutive_note_num)
                for j in range(consecutive_note_num):
                    n = myFile1.flat.notesAndRests[idx + j]
                    s.append(copy.deepcopy(n))
            
            # 保存為 MIDI 檔案
            output_file = "static/generated_music.mid"
            s.write("midi", fp=output_file)

        # If there are at least five note C in violin list then use 小魔女doremi.mid upside down to play and generate music
        elif violin_notes.count("C5") >= 5:
            # reverse處理
            myFile1 = m21.converter.parse("小魔女doremi.midi")
            reversed_stream = m21.stream.Stream()

            for part in myFile1.parts:
                # 取得所有音符和和弦，並reverse
                notes_and_chords = list(part.recurse().notes)
                reversed_notes_and_chords = notes_and_chords[::-1]
                reversed_part = m21.stream.Part()

                for element in reversed_notes_and_chords:
                    reversed_part.append(copy.deepcopy(element))
                reversed_stream.append(reversed_part)

            # 保存reverse後的 MIDI 檔案
            output_file = "static/generated_music.mid"
            reversed_stream.write("midi", fp=output_file)

        else:
            score = m21.stream.Score()

            for instrument, notes in instrument_data.items():
                if notes:
                    part = m21.stream.Part()
                    part.id = instrument

                    # 加入樂器到每個聲部
                    if instrument == "piano":
                        part.append(m21.instrument.Piano())
                    elif instrument == "violin":
                        part.append(m21.instrument.Violin())
                    elif instrument == "flute":
                        part.append(m21.instrument.Flute())
                    elif instrument == "guitar":
                        part.append(m21.instrument.Guitar())
                    elif instrument == "bass":
                        part.append(m21.instrument.Bass())
                    elif instrument == "altoSaxophone":
                        part.append(m21.instrument.AltoSaxophone())

                    # 將記錄的音符加入聲部
                    for note in notes:
                        part.append(m21.note.Note(note))

                    # 加入聲部到總譜
                    score.append(part)

            # 保存為 MIDI 檔案
            output_file = "static/generated_music.mid"
            score.write("midi", fp=output_file)


    return send_file(output_file, as_attachment=True, download_name="generated_music.mid")

# 清空儲存的樂器和音符資料。
@app.route("/reset_instrument_data", methods=["POST"])
def reset_instrument_data():
    for instrument in instrument_data:
        instrument_data[instrument] = []
    return jsonify({"message": "Instrument data reset"}), 200

if __name__ == "__main__":
    app.run(debug=True)
