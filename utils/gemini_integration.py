import requests
import json
import re

def analyze_text_with_gemini(text):
    api_key = "AIzaSyBCCCvVlI3FyQKLYmI2SdASxPiZvh8VvHY"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    prompt_text = "Hãy phân tích tình trạng bệnh của bệnh nhân này dựa trên văn bản này, nếu là đơn thuốc thì hãy tự suy nghĩ bệnh nhân có thể bị bệnh gì dựa trên đơn thuốc và phân tích bệnh nhân nên làm gì và không nên làm gì để tình trạng bệnh tốt hơn: " + text
    
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
