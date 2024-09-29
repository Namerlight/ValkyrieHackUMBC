from whisper_mic import WhisperMic
import cv2
from openai import OpenAI
from configs import org, api_key
from pathlib import Path
import os
import time
import pydirectinput
import re

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

# inp = ['A', 'W, continue']
# for i in inp:
#     parsed = parse_command(i)
#     print(parsed)
#     keypress(parsed[0], parsed[1])

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
        vllm = vllm_for_instruction_control()


    op = convert(result, os.path.join("temp_controls", "control_schema.txt"))
    print(op)

    list_of_commands = [item.strip() for item in op.split("\n")]
    print(list_of_commands)

    for command in list_of_commands:
        parsed = parse_command(command)
        print(parsed)
        if parsed[1] == "continue":
            for i in range(10):
                keypress(parsed[0], parsed[1])






