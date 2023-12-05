# Virtual Imouto Misaka Chan

![Misaka Chan](example_gui.png)

## Table of Contents

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Installation](#installation)
- [Others](#others)

## Introduction

Virtual Imouto Misaka Chan is simple ChatBot project that simulates the role of a little sister, also known as "imouto" in Japanese. This designed to respond to user input using natural language processing techniques. It's a basic implementation of NLP powered by PyTorch. 

## Requirements

- Python 3.11
- PyTorch (2.0.1+cu117) 
- Docker for Voicevox 
- [VoiceVox](https://voicevox.hiroshiba.jp/)

## Installation

Follow these steps to install Virtual Imouto Misaka Chan:

1. Clone the repository
2. Navigate to the project directory: `cd virtual-ai-misaka-chan`
3. Install the required dependencies: 


    ```
    pip install -r requirements.txt
    ```
4. Run the main script: `Chat APP.py`
5. Run VoiceVox Docker image if you wanna Misaka Chan response with Voice (Please Enable VoiceVox Check Box on GUI APP). The commannd Below (choose the one that suits your device):


    CPU : 


    ```
    docker run --rm -it -p 50021:50021 voicevox voicevox_engine:CPU-ubuntu20.04-latest
    ```


    GPU : 

    
    ```
    docker run --rm --gpus all -p 50021:50021 voicevox/voicevox_engine:nvidia-ubuntu20.04-latest
    ```

## Others
This program implements a simple RNN model with limited data intents, so there are many limitations in the response (example chat to get answers can be seen in "pattern" in intents.json). hopefully, in the future, I will improve this program.

Please note that this program uses Torch with version 2.0.1 CUDA 11.7 support.  However, this program only implements basic Torch so it may work well on other version, but there is no guarantee that it will work.

to customize the data for training can be changed in intents.json, don't forget to retrain in train.py

I am very lazy to design a gui app, so for now this is a rough look. I will focus more on exploring the NPL method later.

misaka.png image used was created using AI Stable Diffusion. contact me if you have any objections, of course I will delete it.