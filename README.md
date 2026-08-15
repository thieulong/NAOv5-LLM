# NAO v5 + Local LLM

A Python 2.7 project that connects a **NAO v5 robot** to a locally hosted **Ollama LLM**.

The system allows NAO to listen using its built-in speech recognition, send the recognised phrase to a local language model, receive a generated response, and speak that response using NAO's text-to-speech system.

> **Important environment note:**  
> This project was developed and tested in an **Ubuntu 20.04 virtual machine** running the NAOqi Python 2.7 SDK. Ollama was hosted separately on the main laptop and accessed from the VM over the network.
>
> The code may also work on other operating systems, but **Windows and macOS have not been verified for the NAOqi/Python side of this project**. For the most reproducible setup, use **Ubuntu 20.04 in a VM**.

---

## Project Files

| File | Purpose |
|---|---|
| `voice_chat.py` | **Main program.** Runs the complete NAO + LLM interaction, including speech recognition, Ollama communication, text-to-speech, face tracking, LEDs, head-touch controls, and sit/stand behaviour. |
| `llm_chat.py` | Simpler typed-chat test. Sends terminal input to Ollama and makes NAO speak the reply. Also supports `--mock` mode without a robot. |
| `tts_test.py` | Minimal text-to-speech test used to confirm that Python can communicate with NAO. |
| `battery_check.py` | Reads and prints the NAO battery percentage. |
| `.gitignore` | Prevents the large NAOqi SDK folder and archive from being committed to Git. |

The main file for normal operation is:

```bash
voice_chat.py
```

---

## System Architecture

The tested setup is:

```text
Host laptop
│
├── Ollama
│   └── llama3.2:3b
│
└── Ubuntu 20.04 VM
    ├── Python 2.7
    ├── NAOqi Python SDK 2.1.4.13
    └── voice_chat.py
            │
            │ NAOqi / TCP port 9559
            ↓
         NAO v5
```

During a conversation:

```text
User speaks
    ↓
NAO speech recognition
    ↓
voice_chat.py
    ↓
Ollama API
    ↓
llama3.2:3b
    ↓
Generated response
    ↓
NAO text-to-speech
```

---

# Tested Environment

This repository was developed using:

- **NAO v5**
- **Ubuntu 20.04 LTS**
- Ubuntu running inside a **virtual machine**
- **Python 2.7**
- **NAOqi Python SDK 2.1.4.13**
- **Ollama** running on the host laptop
- Ollama model: **`llama3.2:3b`**
- NAOqi communication on port **9559**
- Ollama API communication on port **11434**

Other operating systems may work, but they have not been tested with this codebase.

Because NAOqi 2.1.4.13 depends on Python 2.7 and older libraries, using the same **Ubuntu 20.04 VM environment** is recommended if you want to reproduce the original setup.

---

# Requirements

You will need:

- A NAO v5 robot
- A computer capable of running an Ubuntu 20.04 VM
- Ubuntu 20.04 inside the VM
- Python 2.7 inside the VM
- NAOqi Python SDK 2.1.4.13
- Ollama on the host computer or another reachable machine
- The `llama3.2:3b` Ollama model
- Network connectivity between:
  - VM ↔ NAO
  - VM ↔ Ollama host

---

# 1. Download the NAOqi Python SDK

The project uses the NAOqi Python SDK compatible with **NAOqi 2.1.4.13**.

Official NAOqi Python installation guide:

https://doc.aldebaran.com/2-1/dev/python/install_guide.html

Download the Linux/Python 2.7 SDK for NAOqi 2.1.4.13.

The SDK archive may look similar to:

```text
naoqi-sdk-2.1.4.13-linux64.tar.gz
```

After extraction, you will have a directory similar to:

```text
naoqi-sdk-2.1.4.13-linux64/
```

The SDK is intentionally **not included in this GitHub repository** because it is large.

---

# 2. Set Up Ubuntu 20.04

Create an **Ubuntu 20.04 LTS virtual machine** using a VM platform such as:

- UTM
- VMware
- VirtualBox
- Parallels

The original project was developed using Ubuntu 20.04 in a VM.

Inside Ubuntu, confirm Python 2.7 is available:

```bash
python2.7 --version
```

You should see something similar to:

```text
Python 2.7.x
```

---

# 3. Configure the NAOqi SDK

Extract the NAOqi SDK inside Ubuntu.

For example:

```bash
tar -xzf naoqi-sdk-2.1.4.13-linux64.tar.gz
```

Then add the SDK to `PYTHONPATH`.

Example:

```bash
export PYTHONPATH="$PYTHONPATH:/path/to/naoqi-sdk-2.1.4.13-linux64/lib/python2.7/site-packages"
```

The exact path depends on where the SDK was extracted.

Test the installation:

```bash
python2.7 -c "import naoqi; print('NAOqi import OK')"
```

If this works, the NAOqi Python SDK is available.

You may want to add the `PYTHONPATH` export to:

```bash
~/.bashrc
```

so it is loaded automatically whenever a terminal is opened.

---

# 4. Clone This Repository

Inside the Ubuntu 20.04 VM:

```bash
git clone https://github.com/thieulong/NAOv5-LLM.git
cd NAOv5-LLM
```

---

# 5. Connect to the NAO Robot

Make sure the VM and NAO can communicate over the network.

Find the NAO IP address.

Pressing the robot's chest button can make NAO announce its current IP address.

For example:

```text
192.168.1.50
```

From Ubuntu, test connectivity:

```bash
ping 192.168.1.50
```

The scripts connect to NAOqi using:

```text
Port 9559
```

---

# 6. Test NAO Before Using the LLM

Before running the full system, test basic communication with NAO.

Open:

```text
tts_test.py
```

Change:

```python
NAO_IP = "PUT_NAO_IP_HERE"
```

to the current NAO IP:

```python
NAO_IP = "192.168.1.50"
```

Then run:

```bash
python2.7 tts_test.py
```

NAO should say:

```text
Hello. I'm running a test script.
```

If this does not work, fix the **NAO network connection or NAOqi SDK configuration** before continuing.

You can also update the IP inside:

```text
battery_check.py
```

and run:

```bash
python2.7 battery_check.py
```

to confirm that the robot battery can be read.

---

# 7. Install Ollama

Ollama can run on the **host laptop** rather than inside the Ubuntu VM.

Download Ollama:

https://ollama.com/download

Install the model used by this project:

```bash
ollama pull llama3.2:3b
```

Test it:

```bash
ollama run llama3.2:3b
```

The project uses the Ollama endpoint:

```text
/api/generate
```

on port:

```text
11434
```

---

# 8. Allow the Ubuntu VM to Reach Ollama

If Ollama runs on the host laptop while the Python scripts run inside Ubuntu, the VM must connect to the **host computer's IP address**.

Do not use:

```text
localhost
```

because inside the VM, `localhost` refers to the VM itself.

Instead use:

```text
http://<HOST_IP>:11434/api/generate
```

For example:

```text
http://192.168.1.20:11434/api/generate
```

From Ubuntu, test the connection:

```bash
curl http://<HOST_IP>:11434/api/tags
```

If JSON containing the installed Ollama models is returned, the connection is working.

If the VM cannot reach Ollama, make sure Ollama is listening on an address accessible from the VM and that the host firewall is not blocking port `11434`.

---

# 9. Configure the Main Program

The main program is:

```text
voice_chat.py
```

The current defaults near the top of the file are:

```python
DEFAULT_NAO_IP = "10.150.242.8"
NAO_PORT = 9559

DEFAULT_OLLAMA_URL = "http://10.141.52.205:11434/api/generate"
DEFAULT_MODEL = "llama3.2:3b"
```

For a new robot or network, you can either change these values directly or provide them when starting the program.

Using command-line arguments is recommended:

```bash
python2.7 voice_chat.py \
  --nao-ip <NAO_IP> \
  --ollama-url http://<HOST_IP>:11434/api/generate \
  --model llama3.2:3b
```

Example:

```bash
python2.7 voice_chat.py \
  --nao-ip 192.168.1.50 \
  --ollama-url http://192.168.1.20:11434/api/generate
```

---

# 10. Run the Full Conversation System

Make sure:

1. NAO is powered on.
2. Ubuntu can reach NAO.
3. The NAOqi SDK imports correctly.
4. Ollama is running.
5. The Ubuntu VM can reach Ollama.

Then run:

```bash
python2.7 voice_chat.py \
  --nao-ip <NAO_IP> \
  --ollama-url http://<HOST_IP>:11434/api/generate
```

When the program starts, NAO:

- connects through NAOqi
- wakes up
- moves to `StandInit`
- loads its speech-recognition vocabulary
- enters idle mode

---

# Robot Controls

### Front head sensor

Starts or stops conversation mode.

### Rear head sensor

Switches between sitting and standing.

### Eye colours

```text
Blue        = Idle
Green       = Listening
Yellow      = Waiting for Ollama
Light blue  = Speaking
Orange      = Speech not confidently recognised
```

When conversation mode is active, NAO also uses face tracking.

---

# Speech Recognition

The current version uses NAO's built-in speech recognition.

Recognition is limited to the predefined list:

```python
VOCABULARY = [
    ...
]
```

inside:

```text
voice_chat.py
```

The current vocabulary includes topics such as:

- greetings
- casual conversation
- robot identity
- robot capabilities
- healthcare
- aged care
- technology
- robotics
- research
- human-robot interaction

To support a different demonstration topic, edit the `VOCABULARY` list.

---

# Optional: Test the LLM Bridge Separately

Before using full voice mode, you can test the Ollama + NAO connection using:

```text
llm_chat.py
```

With NAO:

```bash
python2.7 llm_chat.py \
  --nao-ip <NAO_IP> \
  --ollama-url http://<HOST_IP>:11434/api/generate
```

Type a message into the terminal and NAO should speak the generated reply.

You can also test Ollama without a robot:

```bash
python2.7 llm_chat.py \
  --mock \
  --ollama-url http://<HOST_IP>:11434/api/generate
```

---

# Recommended Setup Order

```text
1. Create Ubuntu 20.04 VM
2. Install/confirm Python 2.7
3. Download and configure NAOqi SDK 2.1.4.13
4. Clone this repository
5. Connect the VM to NAO
6. Run tts_test.py
7. Install Ollama on the host computer
8. Pull llama3.2:3b
9. Confirm the VM can reach Ollama
10. Test llm_chat.py
11. Run voice_chat.py
```

Troubleshooting can be separated into two parts:

```text
tts_test.py fails
    ↓
Check NAO IP / network / Python 2.7 / NAOqi SDK


Ollama test fails
    ↓
Check Ollama / host IP / port 11434 / VM networking


Both work
    ↓
Run voice_chat.py
```

---

## Platform Compatibility

**Tested and recommended:**

```text
Ubuntu 20.04 VM + Python 2.7 + NAOqi SDK 2.1.4.13
```

**Not currently verified:**

```text
Native Windows
Native macOS
Other Linux distributions
Newer Python versions
```

The Python scripts themselves are relatively simple, but the main compatibility limitation is the older **NAOqi 2.1.4.13 / Python 2.7 SDK**.

For this reason, reproducing the original **Ubuntu 20.04 VM environment** is the safest setup.
