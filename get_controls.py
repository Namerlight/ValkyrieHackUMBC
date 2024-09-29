import base64
from openai import OpenAI
import configs
import requests
import os


client = OpenAI(
    organization=configs.org,
    api_key=configs.api_key
)

prompt = f"""The given image shows a list of controls or keybinds for a video game. Look at the image and generate a string containing all of these keybinds. Each possible action and the key required to carry it out should be listed on a separate line. Do not say anything other than this. Do not make up any controls not visinble on the screen."""

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_controls(image_path):

    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {configs.api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "In this task, you need to map a set of controls from a given image into a string."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "max_tokens": 500
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    save_path = os.path.join("temp_controls", "control_schema.txt")

    with open(save_path, 'w') as filetowrite:
        filetowrite.write(response.json()['choices'][0]['message']['content'])


path = os.path.join("temp_imgs", "current_image_1.jpeg")
generate_controls(image_path=path)


