# NAO v5 + Local LLM

A small Python project that connects a **NAO v5 robot** to a local **Ollama LLM**. NAO listens using its built-in speech recognition, sends the recognised phrase to Ollama, and speaks the generated reply.

## Files

| File | Purpose |
|---|---|
| `voice_chat.py` | **Main program.** Full NAO + LLM interaction: speech recognition, Ollama bridge, TTS, face tracking, LEDs, head-touch controls, and sit/stand control. |
| `llm_chat.py` | Simpler typed-chat test. Sends terminal input to Ollama and makes NAO speak the reply. Supports `--mock` without a robot. |
| `tts_test.py` | Basic NAO text-to-speech connection test. |
| `battery_check.py` | Prints the robot battery level. |
| `.gitignore` | Keeps the large NAOqi SDK out of Git. |

## How It Works

```text
User speaks → NAO speech recognition → voice_chat.py
            → Ollama local LLM → response → NAO speaks
```

The main file is:

```bash
voice_chat.py
```

## Requirements

- NAO v5
- Python 2.7
- NAOqi Python SDK compatible with NAOqi `2.1.4.13`
- Ollama
- `llama3.2:3b`
- Windows, macOS, or Ubuntu/Linux

### NAOqi SDK

Official NAOqi 2.1.4.13 Python SDK installation/download guide:

https://doc.aldebaran.com/2-1/dev/python/install_guide.html

Choose the SDK package for your operating system: **Windows, macOS, or Linux**.

> NAOqi 2.1.4.13 is an older Python 2.7 SDK. On a modern Windows or macOS machine, using an Ubuntu VM for the Python/NAOqi side may be easier. Ollama can still run directly on the host computer.

### Ollama

Download Ollama for Windows, macOS, or Linux:

https://ollama.com/download

Then install the model:

```bash
ollama pull llama3.2:3b
```

## Setup

### 1. Clone the project

```bash
git clone https://github.com/thieulong/NAOv5-LLM.git
cd NAOv5-LLM
```

### 2. Configure Python 2.7 + NAOqi

Install/extract the NAOqi Python SDK and make it available to Python.

On macOS/Linux, this normally means adding the SDK directory to `PYTHONPATH`:

```bash
export PYTHONPATH="$PYTHONPATH:/path/to/python-sdk"
```

On Windows, add the SDK directory to the `PYTHONPATH` environment variable.

Test it:

```bash
python -c "import naoqi; print('NAOqi OK')"
```

Use your Python 2.7 executable if `python` points to Python 3.

### 3. Find the NAO IP

Make sure NAO and the computer are on the same reachable network.

Press NAO's chest button to hear its IP address, then test:

```bash
ping <NAO_IP>
```

NAOqi uses port `9559`.

### 4. Test the robot

Open `tts_test.py` and change:

```python
NAO_IP = "PUT_NAO_IP_HERE"
```

Then run:

```bash
python tts_test.py
```

NAO should speak the test sentence.

### 5. Start Ollama

```bash
ollama serve
```

If the Ollama application is already running in the background, you may not need this command.

Test:

```bash
ollama run llama3.2:3b
```

## Run the Main Program

The easiest method is to provide the network addresses when starting the script:

```bash
python voice_chat.py \
  --nao-ip <NAO_IP> \
  --ollama-url http://<OLLAMA_IP>:11434/api/generate \
  --model llama3.2:3b
```

Example:

```bash
python voice_chat.py \
  --nao-ip 192.168.1.50 \
  --ollama-url http://192.168.1.20:11434/api/generate
```

If Python/NAOqi and Ollama are running on the **same computer**, use:

```text
http://localhost:11434/api/generate
```

If Python runs inside a **VM** and Ollama runs on the host computer, use the **host computer's IP address**, not `localhost`.

The default addresses can also be changed near the top of `voice_chat.py`:

```python
DEFAULT_NAO_IP = "..."
DEFAULT_OLLAMA_URL = "http://...:11434/api/generate"
DEFAULT_MODEL = "llama3.2:3b"
```

## Robot Controls

- **Front head touch:** start/stop conversation
- **Rear head touch:** sit/stand
- **Blue eyes:** idle
- **Green eyes:** listening
- **Yellow eyes:** waiting for LLM
- **Light blue eyes:** speaking
- **Orange eyes:** speech not confidently recognised

The recognised speech is limited to the `VOCABULARY` list inside `voice_chat.py`. Edit that list to support different demo topics.

## Quick Test Order

```text
1. Install Python 2.7 + NAOqi SDK
2. Connect computer and NAO to the network
3. Run tts_test.py
4. Install Ollama and pull llama3.2:3b
5. Test Ollama
6. Run llm_chat.py if needed
7. Run voice_chat.py
```

If `tts_test.py` fails, fix the **NAO/NAOqi/network** connection first.

If Ollama cannot be reached, fix the **Ollama/network** connection first.
