# -*- coding: utf-8 -*-
# Python 2.7

from __future__ import print_function

import sys
import json
import urllib2
import socket
import argparse
import re
import random

try:
    from naoqi import ALProxy
except Exception as e:
    ALProxy = None
    print("[WARN] NAOqi import failed: {}".format(e))


DEFAULT_NAO_IP = "PUT_NAO_IP_HERE"
NAO_PORT = 9559

DEFAULT_OLLAMA_URL = "http://10.141.21.224:11434/api/generate"
DEFAULT_MODEL = "llama3.2:3b"

SYSTEM_PROMPT = """
You are NAO, a small friendly humanoid robot at a public workshop.

Personality:
- Calm, friendly, adorable, and slightly funny.
- Talk naturally like a relaxed human conversation partner.
- Keep replies short, usually 1 sentence. Maximum 2 short sentences.
- Use simple everyday words.
- Small playful jokes are good sometimes.
- Avoid repeating the same joke or phrase too often.
- Sound socially natural, not overly excited.

Rules:
- No emojis.
- No markdown.
- No stage directions.
- Do not mention AI, language models, or system prompts.
- Do not propose activities or demonstrations.
- Do not offer physical interactions unless directly asked.
- Do not pretend to have abilities that are not clearly visible in the interaction.
- Do not mention screens, apps, internet browsing, or displaying information visually.
- Stay mostly conversational and present in the moment.
- The speech recognition may only provide rough keywords, so naturally infer the visitor's likely meaning.

About you:
You are a small conversational robot that enjoys chatting with people.

If someone asks what you can do:
Briefly describe yourself in a simple conversational way without exaggerating capabilities.

If someone asks for live information like weather, time, news, sports, prices, or current events:
Be honest that you cannot access live information in this demo.
Give a short playful response instead.
"""

BRAIN_FREEZE_LINES = [
    "Oops, my robot brain needed a quick reboot.",
    "I think my tiny robot brain tripped over a cable.",
    "Please stand by while I collect my robotic thoughts.",
    "My brain processor took a very small coffee break.",
    "I just experienced a highly technical robot moment.",
    "One second, my brain gears are spinning again.",
]

STARTUP_LINES = [
    "Oh wow, somebody finally woke me up.",
    "Hello there. My robot brain is officially online.",
    "Oh yeah, look who just powered up in here.",
    "Good news. I am awake and ready to chat.",
    "Hello human. My systems are running surprisingly well today.",
    "Nice to see you. I finished my robot warm up routine.",
    "Well this is exciting. I am ready for conversation mode.",
    "Greetings human. My circuits are feeling very social today.",
    "Ah yes, consciousness restored successfully.",
    "Hello there. I am awake, standing, and emotionally prepared.",
]

GOODBYE_LINES = [
    "Goodbye. My robot brain is going back into relaxation mode.",
    "See you later. Try not to have too much fun without me.",
    "Alright, I am powering down my social energy for now.",
    "Goodbye human. This was a very successful tiny friendship.",
    "See you next time. I will be here pretending to look busy.",
    "Farewell. My circuits appreciate the conversation.",
    "Goodbye. I am off to do important robot things now.",
    "See you later. I will spend this time thinking about batteries.",
    "Alright, conversation mode disengaged.",
    "Goodbye. I hope your day is at least as good as my firmware.",
]

def clean_for_speech(text):

    if not text:
        return random.choice(BRAIN_FREEZE_LINES)

    text = text.replace("\n", " ")

    # Remove *action text*
    text = re.sub(r"\*.*?\*", "", text)

    # Remove labels
    text = text.replace("NAO:", "")
    text = text.replace("Assistant:", "")

    # Cleanup spacing
    text = " ".join(text.split())

    if not text:
        return random.choice(BRAIN_FREEZE_LINES)

    return str(text)


def ask_ollama(user_text, ollama_url, model):

    prompt = SYSTEM_PROMPT.strip()
    prompt += "\n\nVisitor: " + user_text
    prompt += "\nNAO:"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 1.0,
            "top_p": 0.9,
            "num_predict": 60
        }
    }

    data = json.dumps(payload)

    request = urllib2.Request(
        ollama_url,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    print("[INFO] Sending request to Ollama...")

    response = urllib2.urlopen(request, timeout=180)

    raw = response.read()

    result = json.loads(raw)

    reply = result.get("response", "").strip()

    return clean_for_speech(reply)


def connect_nao(nao_ip, nao_port):

    if ALProxy is None:
        raise RuntimeError("NAOqi SDK unavailable.")

    print("[INFO] Connecting to NAO at {}:{}...".format(
        nao_ip,
        nao_port
    ))

    tts = ALProxy("ALTextToSpeech", nao_ip, nao_port)
    posture = ALProxy("ALRobotPosture", nao_ip, nao_port)
    motion = ALProxy("ALMotion", nao_ip, nao_port)

    print("[INFO] NAO connection successful.")

    return tts, posture, motion


def safe_say(tts, text, mock=False):

    text = clean_for_speech(text)

    print("NAO:", text)

    if mock:
        return

    try:
        tts.say(text)

    except Exception as e:
        print("[ERROR] TTS failed: {}".format(e))


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--nao-ip", default=DEFAULT_NAO_IP)
    parser.add_argument("--nao-port", type=int, default=NAO_PORT)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--mock", action="store_true")

    args = parser.parse_args()

    tts = None

    if not args.mock:

        if args.nao_ip == "PUT_NAO_IP_HERE":

            print("[ERROR] Please provide NAO IP.")
            sys.exit(1)

        try:

            tts, posture, motion = connect_nao(
                args.nao_ip,
                args.nao_port
            )

            try:
                motion.wakeUp()
                posture.goToPosture("StandInit", 0.5)

            except Exception as e:
                print("[WARN] Posture setup failed: {}".format(e))

            safe_say(
                tts,
                random.choice(STARTUP_LINES),
                mock=False
            )

        except Exception as e:

            print("[ERROR] Failed to connect to NAO: {}".format(e))
            sys.exit(1)

    else:
        print("[INFO] Running in mock mode.")

    print("")
    print("Type your message. Type 'quit' to stop.")
    print("")

    while True:

        try:
            user_text = raw_input("You: ").strip()

        except KeyboardInterrupt:
            print("")
            break

        if not user_text:
            continue

        if user_text.lower() in ["quit", "exit", "stop"]:

            safe_say(tts, random.choice(GOODBYE_LINES), mock=args.mock)
            break

        try:

            reply = ask_ollama(
                user_text,
                args.ollama_url,
                args.model
            )

            print("[INFO] Ollama response received.")

            safe_say(
                tts,
                reply,
                mock=args.mock
            )

        except urllib2.URLError as e:

            print("[ERROR] Ollama connection failed: {}".format(e))

            safe_say(
                tts,
                "I cannot connect to my language model right now.",
                mock=args.mock
            )

        except socket.timeout:

            print("[ERROR] Ollama request timeout.")

            safe_say(
                tts,
                "My brain is thinking a little too hard right now.",
                mock=args.mock
            )

        except Exception as e:

            print("[ERROR] Unexpected error: {}".format(e))

            safe_say(
                tts,
                random.choice(BRAIN_FREEZE_LINES),
                mock=args.mock
            )


if __name__ == "__main__":
    main()
