let currentInstrument = "piano";

function initializePage() {
    const defaultColor = "red"; // piano 的顏色
    document.body.style.background = `linear-gradient(45deg, ${defaultColor}, black)`;
    document.querySelector(".instrument").textContent = currentInstrument;
}


// 更新背景和樂器
document.querySelectorAll(".color-picker div").forEach(colorDiv => {
    colorDiv.addEventListener("click", () => {
        const color = colorDiv.getAttribute("data-color");
        document.body.style.background = `linear-gradient(45deg, ${color}, black)`;

        currentInstrument = colorDiv.getAttribute("data-instrument");
        document.querySelector(".instrument").textContent = currentInstrument;
    });
});

// 處理音符按下事件
document.querySelectorAll(".circle div[data-note]").forEach(noteDiv => {
    noteDiv.addEventListener("click", () => {
        const note = noteDiv.getAttribute("data-note");
        
        // 播放對應的音效
        const audio = new Audio(`/static/audio/${note}.mp3`);
        audio.play();

        fetch("/update_instrument", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ instrument: currentInstrument, note })
        })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);

                // 更新記錄到左側
                const recordList = document.getElementById("record-list");
                const newRecord = document.createElement("li");
                newRecord.innerHTML = `<span>${currentInstrument}</span>: ${note}`;
                recordList.appendChild(newRecord);
            })
            .catch(err => console.error(err));
    });
});

// 生成音樂按鈕
document.querySelector(".generate-btn").addEventListener("click", () => {
    fetch("/generate_music", { method: "POST" })
        .then(response => {
            if (response.ok) {
                return response.blob(); // 將返回的數據轉為 Blob
            } else {
                throw new Error("Failed to generate music");
            }
        })
        .then(blob => {
            // 創建臨時下載鏈接
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.style.display = "none";
            a.href = url;
            a.download = "generated_music.mid"; // 指定下載的文件名
            document.body.appendChild(a);
            a.click(); // 自動觸發點擊
            window.URL.revokeObjectURL(url); // 釋放 URL 資源

            // 清空儲存的音符
            fetch("/reset_instrument_data", { method: "POST" }) // 向伺服器請求重置
                .then(() => {
                    console.log("Instrument data cleared.");
                })
                .catch(err => console.error("Failed to reset instrument data", err));

            // 清除左側記錄
            const recordList = document.getElementById("record-list");
            recordList.innerHTML = "";
        })
        .catch(err => console.error(err));
});

document.addEventListener("DOMContentLoaded", () => {
    const randomButton = document.getElementById("random-button");
    const randomStatus = document.getElementById("random-status");
    let isRandomOn = false; // 初始狀態為 OFF

    // 檢查按紐點擊事件
    randomButton.addEventListener("click", () => {
        isRandomOn = !isRandomOn; // 切换狀態
        const randomText = isRandomOn ? "ON" : "OFF";

        // 更新狀態文本
        randomStatus.textContent = randomText;

        // 將狀態發送到後端
        fetch("/toggle_random", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ random: randomText.toLowerCase() }),
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("Random Mode Updated:", data);
            })
            .catch((error) => {
                console.error("Error updating random mode:", error);
            });
    });
});





// 在頁面載入時初始化
window.onload = initializePage;