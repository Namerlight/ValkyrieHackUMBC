from whisper_mic import WhisperMic
import cv2
from openai import OpenAI
from configs import org, api_key
from pathlib import Path
import os
import time
import pydirectinput
import get_controls
import base64
import configs
import requests

from screen_grab import grab_screen


client = OpenAI(
    organization=org,
    api_key=api_key
)


def parse_command(command):
    command = [com.strip() for com in command.split(",")]
    if len(command) == 1:
        command[0] = command[0]
        command.append("0.25")
    key = command[0]
    time = command[1]
    return key.lower(), time


def keypress(key, press_time):
    if key in ["lmb", "rmb", "mmb"]:
        if key == "lmb":
            pydirectinput.click()
        if key == "rmb":
            pydirectinput.rightClick()
        if key == "mmb":
            pydirectinput.middleClick()
    pydirectinput.keyDown(key)
    if press_time == "continue":
        press_time = "0.25"
    time.sleep(float(press_time))
    pydirectinput.keyUp(key)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def generate_instructions(image_path, task):

    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {configs.api_key}"
    }

    prompt = f"""You are instructing a person on how to play a video game. You must be concise and accurate. The player's task is to {task}. 
    Give the player instructions on how to accomplish the task based on the image given above. Do not say anything else other than the instructions. 
    The instruction should be in the form of a sequence of action and duration, given in a very simple, short sentence such as "move forward" or "move left for three seconds and then go forwards for five seconds".
    """

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
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
        "max_tokens": 200
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return response.json()['choices'][0]['message']['content']


def convert(spoken_inp, control_scheme_file):

    control_scheme = Path(control_scheme_file).read_text()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
             "content": "Your goal is to assist the use by turning a short phrase into a set of combinations and sentences, based on the control scheme given to you."},
            {"role": "user", "content": f"Here is the control scheme: {control_scheme}"},
            {"role": "user",
             "content": f"Turn this sentence into a sequence of keys. For example, if the input is 'Move Forward', then the response should be 'W'. If the input is 'Dodge' and the control schema says 'Dodge' is mapped to 'Shift', then your response should be 'Shift'. Do not say anything else other than the key press to list. The left mouse button should be called LMB and the right mouse button should be called RMB. The middle mouse button should be called MMB."
                        f"If a specific time is given for the action, then list that next to the key without any units. For example 'Shift, 3'. If the input sentence is a continuous action but no time or duration is given, such as 'Keep moving forward', then add the word continue after the key instead of giving the duration. For example, 'A, continue'. If there are multiple keys, they must each be on a new line."
                        f""
                        f"The input sentence is: {spoken_inp}"}
        ],
        temperature=0.5
    )

    op = completion.choices[0].message.content
    return op

while True:
    k = cv2.waitKey(1) & 0xFF
    if k == ord('q'):
        break
    mic = WhisperMic(model="base.en", device="cpu", english=False, verbose=False, energy=300, pause=0.5,
                     dynamic_energy=False, save_file=False, model_root="~/.cache/whisper", mic_index=None,
                     implementation="whisper", hallucinate_threshold=400)
    result = mic.listen()
    print(result)


    if "controls" in result:
        grab_screen()
        path = os.path.join("temp_imgs", "current_image.jpeg")
        get_controls.generate_controls(image_path=path)
        print("Controls have been updated.")
        continue

    op = convert(result, os.path.join("temp_controls", "control_schema.txt"))
    print(op)

    grab_screen()

    llm_instructions = generate_instructions(task=result, image_path=os.path.join("temp_imgs", "current_image.jpeg"))
    print(llm_instructions)

    list_of_commands = [item.strip() for item in op.split("\n")]
    print(list_of_commands)

    for command in list_of_commands:
        parsed = parse_command(command)
        print(parsed)
        if parsed[1] == "continue":
            for i in range(20):
                keypress(parsed[0], parsed[1])
        else:
            keypress(parsed[0], parsed[1])






