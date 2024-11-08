// Global variables
let isRecording = false;
let mediaRecorder;
let audioChunks = [];

// Start or stop recording with improved UI feedback
async function toggleRecording() {
    const microphoneImg = document.getElementById("microphoneImg");
    const statusMessage = document.getElementById("statusMessage");
    
    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = event => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };
            
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                audioChunks = [];
                await analyzeAudioWithGemini(audioBlob);
            };
            
            // Start recording with UI updates
            mediaRecorder.start();
            isRecording = true;
            microphoneImg.classList.add('recording');
            statusMessage.innerHTML = '<i class="fas fa-circle text-danger me-2"></i>Đang ghi âm... Nhấn lại để dừng.';
            
        } catch (error) {
            console.error('Microphone access error:', error);
            showError('Không thể truy cập microphone. Vui lòng kiểm tra quyền truy cập.');
        }
    } else {
        // Stop recording with UI updates
        mediaRecorder.stop();
        isRecording = false;
        microphoneImg.classList.remove('recording');
        statusMessage.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Đang phân tích...';
    }
}

// Enhanced audio analysis function
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
            handleAnalysisSuccess(data);
        } else {
            throw new Error(response.statusText);
        }
    } catch (error) {
        handleAnalysisError(error);
    }
}

// Handle successful analysis
function handleAnalysisSuccess(data) {
    const cleanedResult = data.result.replace(/\*/g, "");
    document.getElementById("statusMessage").innerHTML = 
        '<i class="fas fa-check-circle text-success me-2"></i>Phân tích hoàn tất';

    typeText("analysisResult", cleanedResult);

    if (data.stream_url) {
        const audioPlayer = document.getElementById("audioPlayer");
        audioPlayer.src = data.stream_url;
        audioPlayer.play().catch(console.error);
    }
}

// Handle analysis error
function handleAnalysisError(error) {
    console.error("Analysis error:", error);
    showError('Không thể phân tích âm thanh. Vui lòng thử lại.');
}

// Show error message
function showError(message) {
    const statusMessage = document.getElementById("statusMessage");
    statusMessage.innerHTML = `<i class="fas fa-exclamation-circle text-danger me-2"></i>${message}`;
    document.getElementById("analysisResult").innerHTML = "";
}

// Enhanced typing effect
function typeText(elementId, text) {
    const element = document.getElementById(elementId);
    element.innerHTML = "";
    let index = 0;
    
    function type() {
        if (index < text.length) {
            element.innerHTML += text.charAt(index);
            index++;
            setTimeout(type, 30);
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
