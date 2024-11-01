import requests
import json
import re
import os

def upload_image_to_gemini(image_path, api_key):
    api_key = "AIzaSyBCCCvVlI3FyQKLYmI2SdASxPiZvh8VvHY"
    url = f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={api_key}"
    
    mime_type = "image/jpeg" if image_path.lower().endswith(".jpg") or image_path.lower().endswith(".jpeg") else "image/png"
    num_bytes = os.path.getsize(image_path)
    
    headers = {
        "X-Goog-Upload-Protocol": "resumable",
        "X-Goog-Upload-Command": "start",
        "X-Goog-Upload-Header-Content-Length": str(num_bytes),
        "X-Goog-Upload-Header-Content-Type": mime_type,
        "Content-Type": "application/json"
    }
    
    # Step 1: Initiate the resumable upload
    response = requests.post(url, headers=headers, json={"file": {"display_name": "Health Analysis Image"}})
    if response.status_code != 200:
        print(f"Failed to initiate upload: {response.status_code}")
        return None
    upload_url = response.headers.get("X-Goog-Upload-URL")

    # Step 2: Upload the actual image bytes
    headers = {
        "Content-Length": str(num_bytes),
        "X-Goog-Upload-Offset": "0",
        "X-Goog-Upload-Command": "upload, finalize"
    }
    with open(image_path, "rb") as f:
        response = requests.post(upload_url, headers=headers, data=f)

    if response.status_code == 200:
        file_info = response.json()
        return file_info["file"]["uri"]
    else:
        print(f"Failed to upload image: {response.status_code}")
        return None

def analyze_text_with_gemini(text):
    api_key = "AIzaSyBCCCvVlI3FyQKLYmI2SdASxPiZvh8VvHY"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    prompt_text = "Hãy phân tích tình trạng sức khỏe của bệnh nhân dựa trên văn bản này. Nếu đây là đơn thuốc, hãy suy luận về các khả năng bệnh lý dựa trên các loại thuốc được kê và giải thích lý do có thể cho việc sử dụng từng loại thuốc. Đưa ra nhận xét về tình trạng sức khỏe của bệnh nhân cũng như các hành vi và thói quen nên hoặc không nên thực hiện để cải thiện tình trạng bệnh. Hãy cung cấp lời khuyên cụ thể và hữu ích, tập trung vào chế độ ăn uống, hoạt động thể chất và các thói quen lành mạnh: " + text
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt_text
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            response_data = response.json()
            
            if "candidates" in response_data and response_data["candidates"]:
                generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                
                # Loại bỏ ** và thay thế dấu gạch đầu dòng thành ngắt dòng HTML
                cleaned_text = re.sub(r"\*\*", "", generated_text)
                formatted_text = re.sub(r'\*\s+', '- ', cleaned_text).replace('\n', '<br>')
                
                return formatted_text.strip()
            else:
                return "Không tìm thấy ứng cử viên."
        else:
            print(f"Lỗi: Nhận mã trạng thái {response.status_code}")
            return f"Lỗi: Không thể xử lý văn bản. Mã trạng thái: {response.status_code}"
    
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        return "Lỗi: Không thể xử lý văn bản với Gemini AI."
    
def analyze_text_with_image(text, image_path):
    api_key = "AIzaSyBCCCvVlI3FyQKLYmI2SdASxPiZvh8VvHY"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Prepare the prompt
    prompt_text = text
    
    # Upload the image and retrieve the URI
    file_uri = upload_image_to_gemini(image_path, api_key)
    if not file_uri:
        return "Error: Unable to upload the image."
    
    # Prepare the request data with both text and image
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text},
                    {
                        "file_data": {
                            "mime_type": "image/jpeg" if image_path.lower().endswith(".jpg") else "image/png",
                            "file_uri": file_uri
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        # Send the request
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            response_data = response.json()
            
            if "candidates" in response_data and response_data["candidates"]:
                generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                
                # Clean and format the response text
                cleaned_text = re.sub(r"\*\*", "", generated_text)
                formatted_text = re.sub(r'\*\s+', '- ', cleaned_text).replace('\n', '<br>')
                
                return formatted_text.strip()
            else:
                return "No content generated."
        else:
            print(f"Error: Received status code {response.status_code}")
            return f"Error: Unable to process text. Status code: {response.status_code}"
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error: Unable to process text with Gemini AI."
    
def analyze_audio_with_gemini(audio_path, api_key):
    api_key = "AIzaSyBCCCvVlI3FyQKLYmI2SdASxPiZvh8VvHY"
    upload_url = f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={api_key}"

    mime_type = "audio/mpeg" if audio_path.lower().endswith(".mp3") else "audio/wav"
    num_bytes = os.path.getsize(audio_path)

    headers = {
        "X-Goog-Upload-Protocol": "resumable",
        "X-Goog-Upload-Command": "start",
        "X-Goog-Upload-Header-Content-Length": str(num_bytes),
        "X-Goog-Upload-Header-Content-Type": mime_type,
        "Content-Type": "application/json"
    }

    # Bước 1: Khởi tạo upload
    response = requests.post(upload_url, headers=headers, json={"file": {"display_name": "User Audio"}})
    if response.status_code != 200:
        print(f"Failed to initiate upload: {response.status_code}")
        return None

    upload_url = response.headers.get("X-Goog-Upload-URL")

    # Bước 2: Upload audio
    headers = {
        "Content-Length": str(num_bytes),
        "X-Goog-Upload-Offset": "0",
        "X-Goog-Upload-Command": "upload, finalize"
    }
    with open(audio_path, "rb") as f:
        response = requests.post(upload_url, headers=headers, data=f)

    if response.status_code != 200:
        print(f"Failed to upload audio: {response.status_code}")
        return None

    # Lấy URI audio đã upload
    audio_uri = response.json()["file"]["uri"]

    # Bước 3: Gửi yêu cầu phân tích đến Gemini
    analysis_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    headers = {
        'Content-Type': 'application/json'
    }

    # Chuẩn bị dữ liệu yêu cầu
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "file_data": {
                            "mime_type": mime_type,
                            "file_uri": audio_uri
                        }
                    }
                ]
            }
        ]
    }

    try:
        # Gửi yêu cầu phân tích
        response = requests.post(analysis_url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            response_data = response.json()
            
            if "candidates" in response_data and response_data["candidates"]:
                generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                return generated_text.strip()
            else:
                return "Không tìm thấy nội dung nào được tạo ra."
        else:
            print(f"Lỗi: Nhận mã trạng thái {response.status_code}")
            return f"Lỗi: Không thể xử lý âm thanh. Mã trạng thái: {response.status_code}"

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        return "Lỗi: Không thể xử lý âm thanh với Gemini AI."

