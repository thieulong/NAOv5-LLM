# NAO v5 + Local LLM Conversation System

A lightweight Python 2.7 project that connects a NAO v5 robot to a locally hosted Ollama language model. The robot can listen for predefined speech-recognition phrases, send the recognized text to the local LLM, speak the generated reply, track faces, change eye LED colours, and respond to head-touch controls.

## Project Files

| File | Purpose |
|---|---|
| `voice_chat.py` | **Main program.** Full NAO + local LLM conversation mode. Handles NAO speech recognition, Ollama requests, text-to-speech, face tracking, LED states, front-head conversation toggle, rear-head sit/stand toggle, silence handling, and error handling. |
| `llm_chat.py` | Simpler typed-chat bridge for testing. Type a message in the terminal, send it to Ollama, and have NAO speak the response. Also supports `--mock` mode without a robot. |
| `tts_test.py` | Minimal NAO text-to-speech test. Use this first to confirm that the computer can connect to the robot. |
| `battery_check.py` | Reads and prints the NAO battery percentage. |
| `.gitignore` | Excludes the large NAOqi SDK folder and archive from Git. |

## System Flow

```text
Person speaks
    ↓
NAO speech recognition
    ↓
voice_chat.py
    ↓
Ollama API
    ↓
Local model: llama3.2:3b
    ↓
Generated response
    ↓
NAO text-to-speech
```

`voice_chat.py` is the main file to run for the complete robot interaction.

## Requirements

- NAO v5 robot running NAOqi
- NAOqi Python SDK compatible with the robot; this project was developed with NAOqi/Python SDK `2.1.4.13`
- Python 2.7 environment
- A computer or VM that can reach the NAO robot over the network
- Ollama running on the local laptop or another reachable computer
- Ollama model `llama3.2:3b`

> The NAOqi SDK is intentionally not stored in this repository because it is large and must be installed separately.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/thieulong/NAOv5-LLM.git
cd NAOv5-LLM
```

### 2. Set up Python 2.7 and the NAOqi Python SDK

Use a Python 2.7 environment that is compatible with the NAOqi `2.1.4.13` Python SDK.

Extract the NAOqi Python SDK somewhere on the machine or inside the VM, then add the extracted SDK directory to `PYTHONPATH`.

Example:

```bash
export PYTHONPATH="$PYTHONPATH:/path/to/python-sdk"
```

Test the SDK:

```bash
python2.7 -c "import naoqi; print('NAOqi import OK')"
```

If `import naoqi` works, the Python side is ready.

### 3. Put the NAO and computer on a reachable network

The machine running the Python scripts must be able to reach the NAO robot.

Find the robot's IP address. On NAO, pressing the chest button can make the robot announce its IP address.

Test connectivity from the VM/computer:

```bash
ping <NAO_IP>
```

NAOqi normally uses port `9559` in this project.

### 4. Test the NAO connection

Open `tts_test.py` and replace:

```python
NAO_IP = "PUT_NAO_IP_HERE"
```

with the current robot IP, for example:

```python
NAO_IP = "192.168.1.50"
```

Run:

```bash
python2.7 tts_test.py
```

NAO should say:

```text
Hello. I'm running a test script.
```

You can also update `NAO_IP` in `battery_check.py` and run:

```bash
python2.7 battery_check.py
```

### 5. Install and start Ollama

Install Ollama on the laptop that will host the local LLM.

Pull the model used by this project:

```bash
ollama pull llama3.2:3b
```

Test it:

```bash
ollama run llama3.2:3b
```

The Python programs use Ollama's `/api/generate` endpoint on port `11434`.

### 6. Allow the VM to reach Ollama

If Ollama and the Python program run on the **same machine**, the Ollama URL can normally use:

```text
http://localhost:11434/api/generate
```

If the Python program runs inside a **VM** while Ollama runs on the host laptop, do not use `localhost`. Use the host laptop's IP address:

```text
http://<HOST_IP>:11434/api/generate
```

Ollama must also be configured to listen on an address reachable from the VM.

For example, on macOS:

```bash
launchctl setenv OLLAMA_HOST "0.0.0.0:11434"
```

Then restart the Ollama application.

From the VM, test:

```bash
curl http://<HOST_IP>:11434/api/tags
```

If JSON is returned, the VM can reach Ollama.

## Configure the Main Program

At the top of `voice_chat.py`, the current defaults are:

```python
DEFAULT_NAO_IP = "10.150.242.8"
NAO_PORT = 9559

DEFAULT_OLLAMA_URL = "http://10.141.52.205:11434/api/generate"
DEFAULT_MODEL = "llama3.2:3b"
```

For a new robot or laptop, change:

- `DEFAULT_NAO_IP` → the new NAO robot IP
- `DEFAULT_OLLAMA_URL` → the IP of the computer running Ollama
- `DEFAULT_MODEL` → only if using a different Ollama model

You can also leave the source code unchanged and override these values when starting the program:

```bash
python2.7 voice_chat.py \
  --nao-ip <NAO_IP> \
  --ollama-url http://<OLLAMA_HOST_IP>:11434/api/generate \
  --model llama3.2:3b
```

This is the recommended approach when moving between different robots or networks.

## Run the Full Conversation System

Start Ollama first, then run:

```bash
python2.7 voice_chat.py \
  --nao-ip <NAO_IP> \
  --ollama-url http://<OLLAMA_HOST_IP>:11434/api/generate
```

When the program starts, NAO wakes up and moves to `StandInit`.

Controls:

- **Front head sensor:** start or stop conversation mode
- **Rear head sensor:** toggle between sitting and standing
- **Blue eyes:** idle
- **Green eyes:** listening
- **Yellow eyes:** waiting for the LLM
- **Light blue eyes:** speaking
- **Orange eyes:** speech was not understood confidently

While conversation mode is active, NAO tracks the person's face, listens using its built-in speech recognition, sends the best recognized phrase to Ollama, and speaks the generated answer.

The current speech recognizer uses the predefined `VOCABULARY` list in `voice_chat.py`. Add or remove phrases there if the demo needs to recognise different topics.

## Optional: Test the LLM Bridge Before Voice Mode

`llm_chat.py` is useful for testing the LLM and NAO speech without using NAO's microphone.

Run with the robot:

```bash
python2.7 llm_chat.py \
  --nao-ip <NAO_IP> \
  --ollama-url http://<OLLAMA_HOST_IP>:11434/api/generate
```

Then type messages into the terminal. NAO should speak the LLM response.

To test the Ollama connection without a robot:

```bash
python2.7 llm_chat.py \
  --mock \
  --ollama-url http://<OLLAMA_HOST_IP>:11434/api/generate
```

## Recommended Setup Order

```text
1. Connect NAO and the computer/VM to the network
2. Confirm the NAO IP
3. Confirm Python 2.7 + NAOqi SDK imports correctly
4. Run tts_test.py
5. Install/start Ollama
6. Pull llama3.2:3b
7. Confirm the VM can reach port 11434
8. Test llm_chat.py
9. Run voice_chat.py
```

If `tts_test.py` fails, fix the NAO/Python/network connection first. If `llm_chat.py --mock` cannot reach Ollama, fix the Ollama/network configuration first. Only move to `voice_chat.py` after both sides work independently.
