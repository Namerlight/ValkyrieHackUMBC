# Valkyrie
### Voice Activated LLM Keypress Engine

We decided to build a Voice Activated LLM-based Keypresser for people who struggle to press keys on time in fast paced scenarios like work or games. While a lot of voice activated controls exist, most of them require you to say the exact key you want to activate, or require manual mapping. In this case, we use an LLM (GPT-4o) to automate the mapping process, simplifying things for the end user.

Voice commands are provided to the LLM, along with a frame grab of the current application. The LLM processes this information, then provides the exact keypresses that are required to execute the action in the game.

We have two modes for this: direct control, which converts simple commands like "dodge", "move" and "roll" to keypresses, based on the control mapping of the application, and LLM control, which takes in more broad stroke instructions and tries to generate controls for them using the LLM before generating commands to execute.

![Alt text](images/ValkyrieFlow.png?raw=true "Valkyrie Process")

## Setup

First, set up a python environment (3.9 is recommended). Then run
`pip install -r reqirements.txt`
to install all requirements.

## Running this

To run the direct control mode, execute `stt_input.py` in administrator mode.

To run LLM control mode, execute `stt_input_llmguided.py` in administrator mode.

If you do not run this in administrator mode, commands may not register in many games.

## Credits

Shadab Choudhury
Naren Sivakumar

