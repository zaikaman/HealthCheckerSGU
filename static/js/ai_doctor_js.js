function handleAnalysisSuccess(data) {
    const cleanedResult = data.result.replace(/\*/g, "");
    document.getElementById("statusMessage").innerHTML = 
        '<i class="fas fa-check-circle text-success me-2"></i>Phân tích hoàn tất';

    typeText("analysisResult", cleanedResult);

    if (data.audio_url) {
        const audioPlayer = document.getElementById("audioPlayer");
        audioPlayer.src = data.audio_url;
        
        // Thử phát audio
        const playAudio = () => {
            const playPromise = audioPlayer.play();
            
            if (playPromise !== undefined) {
                playPromise.then(() => {
                    // Phát thành công
                    console.log('Audio playing automatically');
                }).catch(error => {
                    console.log('Autoplay prevented:', error);
                    
                    // Thêm nút play nếu không thể tự động phát
                    if (!document.getElementById('manualPlayButton')) {
                        const playButton = document.createElement('button');
                        playButton.id = 'manualPlayButton';
                        playButton.className = 'btn btn-primary mt-2';
                        playButton.innerHTML = '<i class="fas fa-play"></i> Phát audio';
                        playButton.onclick = () => {
                            audioPlayer.play().then(() => {
                                playButton.style.display = 'none';
                            }).catch(console.error);
                        };
                        audioPlayer.parentElement.insertBefore(playButton, audioPlayer.nextSibling);
                    }
                });
            }
        };

        // Xử lý khi audio đã load xong
        audioPlayer.onloadeddata = playAudio;
        
        // Backup: thử phát lại khi có tương tác người dùng
        document.body.addEventListener('touchstart', function playOnTouch() {
            if (audioPlayer.paused) {
                playAudio();
            }
            document.body.removeEventListener('touchstart', playOnTouch);
        }, { once: true });
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

// Thêm hàm mới để khởi tạo audio context
function initializeAudioContext() {
    // Tạo audio context khi có tương tác người dùng
    document.addEventListener('touchstart', function initAudio() {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        const audioContext = new AudioContext();
        document.removeEventListener('touchstart', initAudio);
    }, { once: true });
}

// Thêm khởi tạo audio context khi trang load
document.addEventListener('DOMContentLoaded', function() {
    initializeAudioContext();
    
    // Thêm xử lý cho nút microphone
    const microphoneButton = document.querySelector('.microphone');
    if (microphoneButton) {
        microphoneButton.addEventListener('touchstart', function() {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!window.audioContext) {
                window.audioContext = new AudioContext();
            }
        }, { once: true });
    }
});

