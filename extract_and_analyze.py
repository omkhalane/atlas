import cv2
import base64
import requests

# Extract frame
vidcap = cv2.VideoCapture('Screencast from 2026-08-01 23-15-24.webm')
success, image = vidcap.read()
if success:
    cv2.imwrite("frame.jpg", image)
    
    with open("frame.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
    api_key = "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"
    headers = {
      "Authorization": f"Bearer {api_key}",
      "Content-Type": "application/json"
    }
    
    payload = {
      "model": "google/gemini-2.0-flash-lite-preview-02-05:free",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "Please act as an expert UI/UX developer. Describe the UI in this screenshot in extremely precise detail so I can build a 100% clone of it using React. What are the specific layout panels? What are the exact CSS colors (backgrounds, borders, text, accents)? How does the 'Agent Running' indicator look? How are the message bubbles (thoughts, actions, etc.) styled? What do the tabs look like? BE VERY SPECIFIC."
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{encoded_string}"
              }
            }
          ]
        }
      ]
    }
    
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    if 'choices' in response.json():
        print(response.json()['choices'][0]['message']['content'])
    else:
        print(response.json())
else:
    print("Failed to read video")
