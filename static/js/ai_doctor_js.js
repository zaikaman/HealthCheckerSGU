// Global variables
let isRecording = false;
let mediaRecorder;
let audioChunks = [];

// Start or stop recording
async function toggleRecording() {
    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/mp4' });
            mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                audioChunks = [];
                await analyzeAudioWithGemini(audioBlob);
            };
            mediaRecorder.start();
            isRecording = true;
            document.getElementById("microphoneImg").style.border = "3px solid red";
            document.getElementById("statusMessage").innerText = "Đang ghi âm... Nhấn lại để dừng.";
        } catch (error) {
            console.error('Trình duyệt không có quyền truy cập microphone:', error);
            document.getElementById("statusMessage").innerText = "Lỗi: Không thể truy cập microphone.";
        }
    } else {
        mediaRecorder.stop();
        isRecording = false;
        document.getElementById("microphoneImg").style.border = "";
        document.getElementById("statusMessage").innerText = "Đang phân tích...";
    }
}

// Send audio to server for analysis
async function analyzeAudioWithGemini(audioBlob) {
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.webm");

    try {
        const response = await fetch("/analyze_audio", {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            console.log("Gemini response:", data);

            const cleanedResult = data.result.replace(/\*/g, "");
            document.getElementById("statusMessage").innerText = "";

            typeText("analysisResult", "Phân tích hoàn tất: " + cleanedResult);

            if (data.stream_url) {
                const audioPlayer = document.getElementById("audioPlayer");
                audioPlayer.src = data.stream_url;
                audioPlayer.play().catch((error) => {
                    console.log("Autoplay was prevented:", error);
                });
            }
        } else {
            console.error("Lỗi khi gửi audio đến server:", response.statusText);
            document.getElementById("statusMessage").innerText = "Lỗi: Không thể phân tích âm thanh.";
            document.getElementById("analysisResult").innerHTML = "";
        }
    } catch (error) {
        console.error("Error:", error);
        document.getElementById("statusMessage").innerText = "Lỗi: Không thể kết nối đến server.";
        document.getElementById("analysisResult").innerHTML = "";
    }
}

// Create typing effect
function typeText(elementId, text) {
    const element = document.getElementById(elementId);
    element.innerHTML = "";
    let index = 0;
    
    function type() {
        if (index < text.length) {
            element.innerHTML += text.charAt(index);
            index++;
            setTimeout(type, 50);
        }
    }
    
    type();
}

// Toggle media display
function toggleMediaDisplay(type) {
    const mediaDisplay = document.getElementById("mediaDisplay");
    const existingMedia = mediaDisplay.querySelector(".media-content.active");
    
    if (existingMedia) {
        existingMedia.classList.remove("active");
        setTimeout(() => {
            mediaDisplay.innerHTML = getMediaContent(type);
            const newMedia = mediaDisplay.querySelector(".media-content");
            if (newMedia) {
                newMedia.classList.add("active");
            }
        }, 500);
    } else {
        mediaDisplay.innerHTML = getMediaContent(type);
        const newMedia = mediaDisplay.querySelector(".media-content");
        if (newMedia) {
            newMedia.classList.add("active");
        }
    }
}

// Get media content based on type
function getMediaContent(type) {
    if (type === "video") {
        return `
            <div style="position: relative; width: 100%; height: 100%; overflow: hidden;">
                <iframe class="media-content active" allow="fullscreen; autoplay" allowfullscreen 
                    src="https://streamable.com/e/5iv02h?autoplay=1&muted=1&nocontrols=1" 
                    style="width: 100%; height: 100%; object-fit: cover;">
                </iframe>
            </div>`;
    } else {
        return `
            <img id="staticImage" src="https://i.ibb.co/qnzGV3N/image.png" alt="image" border="0" 
                class="media-content active" style="width: 100%; height: 100%; object-fit: cover;">`;
    }
}
