from naoqi import ALProxy

NAO_IP = "PUT_NAO_IP_HERE"
PORT = 9559

tts = ALProxy("ALTextToSpeech", NAO_IP, PORT)
tts.say("Hello. I'm running a test script.")
