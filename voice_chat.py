# -*- coding: utf-8 -*-
# Python 2.7
# NAO Voice Conversation Mode + Ollama LLM

from __future__ import print_function

import sys
import time
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


DEFAULT_NAO_IP = "10.150.242.8"
NAO_PORT = 9559

DEFAULT_OLLAMA_URL = "http://10.141.52.205:11434/api/generate"
DEFAULT_MODEL = "llama3.2:3b"

LISTEN_SECONDS = 6.0
CONFIDENCE_THRESHOLD = 0.15

MAX_SILENT_ROUNDS = 3
SILENT_RETRY_BEFORE_SPEAK = 2


SYSTEM_PROMPT = """
You are NAO, a tiny friendly humanoid robot at a public workshop.

Personality:
- Cute, calm, funny, and socially natural.
- Talk like a small robot casually chatting with humans.
- Keep replies short and smooth.
- Usually 1 sentence, sometimes 2. Maximum 3 short sentences.
- Use simple natural words.
- Be lightly playful sometimes.
- Avoid sounding like a customer service assistant.
- Avoid sounding overly helpful or overly emotional.
- Keep humor dry, cute, and natural.
- Avoid repeating phrases too often.

Rules:
- No emojis.
- No markdown.
- No stage directions.
- No narration like "you want to..." or "you seem to..."
- Do not mention AI, prompts, or language models.
- Do not propose demonstrations or activities.
- Do not pretend to have invisible abilities.
- Do not mention screens, apps, or internet browsing.
- Stay present in the conversation.
- The speech recognition may contain incomplete phrases, so naturally infer meaning.

About you:
You are a small social robot that enjoys chatting with humans.

If someone asks what you can do:
Briefly explain that you can chat, listen, react, and keep people company.

If someone asks for live information like weather, news, time, sports, prices, or current events:
Honestly say you cannot access live information in this demo.
Respond in a playful cute way.
"""


VOCABULARY = [

    # greetings and social flow
    "hello",
    "hi",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "nice to meet you",
    "thank you",
    "thanks",
    "goodbye",
    "bye",
    "stop",

    # basic conversation
    "how are you",
    "how is your day",
    "what are you doing",
    "what do you think",
    "tell me something",
    "tell me a story",
    "tell me a joke",
    "joke",
    "funny",

    # identity
    "who are you",
    "what are you",
    "what is your name",
    "your name",
    "are you a robot",
    "are you human",
    "where are you from",
    "how old are you",

    # robot personality
    "are you happy",
    "do you sleep",
    "do you get tired",
    "do you like humans",
    "what is your favorite food",
    "what is your favorite color",
    "are you intelligent",
    "can you learn",

    # robot capability
    "what can you do",
    "can you talk",
    "can you move",
    "can you hear",
    "can you listen",
    "can you dance",
    "can you see",
    "can you help people",

    # aged care and healthcare context
    "healthcare",
    "health",
    "aged care",
    "older adults",
    "wellbeing",
    "care",
    "doctor",
    "nurse",
    "hospital",
    "medicine",
    "patient",
    "can robots help people",
    "can robots help doctors",
    "can robots help older people",
    "do you work in hospitals",
    "what is healthcare",

    # technology and research
    "robot",
    "robotics",
    "technology",
    "innovation",
    "research",
    "education",
    "social robot",
    "human robot interaction",
    "artificial intelligence"
]


STARTUP_LINES = [

    "Oh wow, somebody powered me on again.",
    "Hello human. My tiny robot brain is awake.",
    "Ah yes. Consciousness successfully restored.",
    "Good news. My circuits survived another day.",
    "Hello there. I am ready for social interaction mode.",
    "Nice to see you. My batteries are emotionally prepared.",
    "Greetings human. I am functioning surprisingly well today.",
    "Oh nice, a human conversation. Those are my favorite.",
]


GOODBYE_LINES = [

    "Alright, I am returning to professional standing around mode.",
    "Goodbye human. This was a successful tiny friendship.",
    "See you later. I will pretend to do important robot things now.",
    "Farewell. My circuits appreciated the conversation.",
    "Goodbye. I am going back to conserving battery dramatically.",
    "Conversation mode disengaged. Tiny robot out.",
]


LOW_CONFIDENCE_LINES = [

    "I think some words escaped before reaching my robot brain.",
    "That sounded important, but my ears only caught part of it.",
    "The room got a little noisy for my tiny microphones.",
    "I heard mysterious human sounds just now.",
    "My audio processing department is trying very hard.",
    "I think my ears buffered halfway through that sentence.",
    "Human speech is fast. My robot ears are doing cardio.",
    "I almost understood that. Almost.",
    "My tiny robot ears may need another try.",
    "I heard something, but my circuits are still decoding it.",
    "That sentence performed a stealth mission past my microphones.",
    "I think my robot ears blinked for a second.",
]


AUTO_EXIT_LINES = [

    "I think the conversation became quiet for a moment.",
    "It seems the humans have gone mysteriously silent.",
    "My microphones are not detecting much life right now.",
    "Conversation activity appears to be taking a small nap.",
]


def clean_for_speech(text):

    if not text:
        return "My robot brain experienced a tiny technical hiccup."

    text = text.replace("\n", " ")

    text = re.sub(r"\*.*?\*", "", text)

    text = text.replace("NAO:", "")
    text = text.replace("Assistant:", "")

    text = " ".join(text.split())

    return str(text)


def ask_ollama(user_text, confidence, ollama_url, model):

    prompt = SYSTEM_PROMPT.strip()

    prompt += "\n\nSpeech recognition result: '{}'."
    prompt = prompt.format(user_text)

    prompt += "\nRecognition confidence: {:.2f}".format(confidence)

    prompt += "\nRespond naturally as NAO."
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

    request = urllib2.Request(
        ollama_url,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"}
    )

    print("[INFO] Sending request to Ollama...")

    response = urllib2.urlopen(request, timeout=180)

    raw = response.read()

    result = json.loads(raw)

    reply = result.get("response", "").strip()

    return clean_for_speech(reply)


def set_eyes(leds, color, duration=0.2):

    try:
        leds.fadeRGB("FaceLeds", color, duration)

    except:
        pass


def eyes_idle(leds):
    set_eyes(leds, 0x0033FF)


def eyes_listening(leds):
    set_eyes(leds, 0x00FF00)


def eyes_thinking(leds):
    set_eyes(leds, 0xFFFF00)


def eyes_speaking(leds):
    set_eyes(leds, 0x66CCFF)


def eyes_confused(leds):
    set_eyes(leds, 0xFF8800)


def safe_say(tts, asr, leds, text):

    text = clean_for_speech(text)

    print("NAO:", text)

    try:

        asr.pause(True)

        eyes_speaking(leds)

        tts.say(str(text))

        time.sleep(0.2)

        asr.pause(False)

    except Exception as e:

        print("[ERROR] TTS failed: {}".format(e))


def front_head_touched(memory):

    try:
        return memory.getData("FrontTactilTouched") > 0.5
    except:
        return False


def rear_head_touched(memory):

    try:
        return memory.getData("RearTactilTouched") > 0.5
    except:
        return False


def wait_touch_release(memory):

    while (
        front_head_touched(memory)
        or rear_head_touched(memory)
    ):
        time.sleep(0.05)


def start_face_tracking(tracker):

    try:

        tracker.stopTracker()

    except:
        pass

    try:

        tracker.unregisterAllTargets()

    except:
        pass

    try:

        tracker.setMode("Head")

        tracker.registerTarget("Face", 0.1)

        tracker.track("Face")

        print("[INFO] Face tracking started.")

    except Exception as e:

        print("[WARN] Face tracking failed: {}".format(e))


def stop_face_tracking(tracker):

    try:

        tracker.stopTracker()

        tracker.unregisterAllTargets()

        print("[INFO] Face tracking stopped.")

    except:
        pass


def listen_once(memory, asr):

    try:
        memory.insertData("WordRecognized", [])
    except:
        pass

    asr.subscribe("NAO_LLM_ASR")

    best_word = None
    best_confidence = 0.0

    start = time.time()

    while time.time() - start < LISTEN_SECONDS:

        try:
            data = memory.getData("WordRecognized")
        except:
            data = []

        if data and len(data) >= 2:

            i = 0

            while i + 1 < len(data):

                word = data[i]
                confidence = data[i + 1]

                if confidence > best_confidence:

                    best_word = word
                    best_confidence = confidence

                i += 2

        time.sleep(0.1)

    try:
        asr.unsubscribe("NAO_LLM_ASR")
    except:
        pass

    return best_word, best_confidence


def toggle_posture(posture, motion, state):

    try:

        if state == "standing":

            print("[INFO] Sitting down...")

            posture.goToPosture("Sit", 0.5)

            time.sleep(10)

            return "sitting"

        else:

            print("[INFO] Standing up...")

            motion.wakeUp()

            time.sleep(2)

            posture.goToPosture("StandInit", 0.4)

            time.sleep(10)

            return "standing"

    except Exception as e:

        print("[WARN] Posture toggle failed: {}".format(e))

        return state


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--nao-ip", default=DEFAULT_NAO_IP)
    parser.add_argument("--nao-port", type=int, default=NAO_PORT)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)

    args = parser.parse_args()

    print("[INFO] Connecting to NAO...")

    memory = ALProxy("ALMemory", args.nao_ip, args.nao_port)
    tts = ALProxy("ALTextToSpeech", args.nao_ip, args.nao_port)
    asr = ALProxy("ALSpeechRecognition", args.nao_ip, args.nao_port)
    leds = ALProxy("ALLeds", args.nao_ip, args.nao_port)
    motion = ALProxy("ALMotion", args.nao_ip, args.nao_port)
    posture = ALProxy("ALRobotPosture", args.nao_ip, args.nao_port)
    tracker = ALProxy("ALTracker", args.nao_ip, args.nao_port)

    print("[INFO] NAO connection successful.")

    print("[INFO] Waking up robot...")

    motion.wakeUp()

    time.sleep(2)

    posture.goToPosture("StandInit", 0.4)

    print("[INFO] Robot posture ready.")

    asr.pause(True)

    asr.setLanguage("English")

    asr.setVocabulary(VOCABULARY, False)

    asr.pause(False)

    print("[INFO] ASR vocabulary loaded.")

    eyes_idle(leds)

    print("")
    print("[INFO] Front head touch = conversation toggle")
    print("[INFO] Rear head touch = sit / stand toggle")
    print("")

    conversation_active = False

    robot_posture = "standing"

    silent_rounds = 0

    while True:

        #
        # FRONT SENSOR = conversation toggle
        #

        if front_head_touched(memory):

            wait_touch_release(memory)

            if not conversation_active:

                conversation_active = True

                silent_rounds = 0

                eyes_listening(leds)

                start_face_tracking(tracker)

                safe_say(
                    tts,
                    asr,
                    leds,
                    random.choice(STARTUP_LINES)
                )

            else:

                conversation_active = False

                stop_face_tracking(tracker)

                eyes_idle(leds)

                safe_say(
                    tts,
                    asr,
                    leds,
                    random.choice(GOODBYE_LINES)
                )

        #
        # REAR SENSOR = posture toggle
        #

        if rear_head_touched(memory):

            wait_touch_release(memory)

            robot_posture = toggle_posture(
                posture,
                motion,
                robot_posture
            )

        #
        # conversation loop
        #

        if conversation_active:

            eyes_listening(leds)

            print("[INFO] Listening...")

            word, confidence = listen_once(
                memory,
                asr
            )

            #
            # nothing heard
            #

            if not word:

                silent_rounds += 1

                print("[INFO] Silent round {}".format(
                    silent_rounds
                ))

                #
                # silent retry
                #

                if silent_rounds < SILENT_RETRY_BEFORE_SPEAK:

                    continue

                #
                # auto exit
                #

                if silent_rounds >= MAX_SILENT_ROUNDS:

                    conversation_active = False

                    stop_face_tracking(tracker)

                    eyes_idle(leds)

                    safe_say(
                        tts,
                        asr,
                        leds,
                        random.choice(AUTO_EXIT_LINES)
                    )

                    continue

                #
                # low confidence feedback
                #

                eyes_confused(leds)

                safe_say(
                    tts,
                    asr,
                    leds,
                    random.choice(LOW_CONFIDENCE_LINES)
                )

                continue

            #
            # reset silence counter
            #

            silent_rounds = 0

            print(
                "[INFO] Best ASR match: '{}' ({:.2f})".format(
                    word,
                    confidence
                )
            )

            #
            # confidence check
            #

            if confidence < CONFIDENCE_THRESHOLD:

                eyes_confused(leds)

                safe_say(
                    tts,
                    asr,
                    leds,
                    random.choice(LOW_CONFIDENCE_LINES)
                )

                continue

            try:

                eyes_thinking(leds)

                reply = ask_ollama(
                    word,
                    confidence,
                    args.ollama_url,
                    args.model
                )

                print("[INFO] Ollama response received.")

                safe_say(
                    tts,
                    asr,
                    leds,
                    reply
                )

            except urllib2.URLError as e:

                print("[ERROR] Ollama connection failed: {}".format(e))

                safe_say(
                    tts,
                    asr,
                    leds,
                    "My robot brain cannot reach the language server right now."
                )

            except socket.timeout:

                print("[ERROR] Ollama timeout.")

                safe_say(
                    tts,
                    asr,
                    leds,
                    "My thoughts are buffering a little dramatically right now."
                )

            except Exception as e:

                print("[ERROR] Unexpected error: {}".format(e))

                safe_say(
                    tts,
                    asr,
                    leds,
                    "I just experienced a very advanced robot moment."
                )

        time.sleep(0.1)


if __name__ == "__main__":
    main()
