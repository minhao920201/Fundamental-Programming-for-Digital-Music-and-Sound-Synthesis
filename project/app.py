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
    "trumpet": [],
    "violoncello": []
}

# 音符對應的音高
notes_mapping = {
    "A": "A4",  # La
    "B": "B4",  # Si
    "C": "C5",  # Do
    "D": "D5",  # Re
    "E": "E5",  # Mi
    "F": "F5",  # Fa
    "G": "G5"   # Sol
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/update_instrument", methods=["POST"])
def update_instrument():
    """
    接收前端按下的音符和樂器，記錄音符到對應樂器。
    """
    data = request.get_json()
    instrument = data.get("instrument")
    note = data.get("note")

    if instrument and note and instrument in instrument_data:
        instrument_data[instrument].append(notes_mapping[note])
        return jsonify({"message": f"Note '{notes_mapping[note]}' added to {instrument}"}), 200
    return jsonify({"message": "Invalid data"}), 400

@app.route("/generate_music", methods=["POST"])
def generate_music():
    """
    根據記錄的音符為每個樂器生成音樂，並保存為 MIDI 檔案。
    """

    piano_notes = set(instrument_data["piano"])
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
                elif instrument == "trumpet":
                    part.append(m21.instrument.Trumpet())
                elif instrument == "violoncello":
                    part.append(m21.instrument.Violoncello())

                # 將記錄的音符加入聲部
                for note in notes:
                    part.append(m21.note.Note(note))

                # 加入聲部到總譜
                score.append(part)

        # 保存為 MIDI 檔案
        output_file = "static/generated_music.mid"
        score.write("midi", fp=output_file)


    return send_file(output_file, as_attachment=True, download_name="generated_music.mid")

@app.route("/reset_instrument_data", methods=["POST"])
def reset_instrument_data():
    """
    清空儲存的樂器和音符資料。
    """
    for instrument in instrument_data:
        instrument_data[instrument] = []
    return jsonify({"message": "Instrument data reset"}), 200

if __name__ == "__main__":
    app.run(debug=True)
