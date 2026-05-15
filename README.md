<div align="center">

```
███╗   ██╗██╗     ██████╗ ██████╗ ███████╗██╗  ██╗███████╗██╗     ██╗
████╗  ██║██║     ██╔══██╗╚════██╗██╔════╝██║  ██║██╔════╝██║     ██║
██╔██╗ ██║██║     ██████╔╝ █████╔╝███████╗███████║█████╗  ██║     ██║
██║╚██╗██║██║     ██╔═══╝ ██╔═══╝ ╚════██║██╔══██║██╔══╝  ██║     ██║
██║ ╚████║███████╗██║     ███████╗███████║██║  ██║███████╗███████╗███████╗
╚═╝  ╚═══╝╚══════╝╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
```

**Speak naturally. Execute instantly.**

*Natural language → shell command, right in your terminal.*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Model](https://img.shields.io/badge/Model-Qwen2.5--0.5B-FF6B35?style=flat-square)](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)
[![Fine--tuned on](https://img.shields.io/badge/Dataset-NL2Bash-brightgreen?style=flat-square)](https://huggingface.co/datasets/AnishJoshi/nl2bash-custom)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active%20Development-blue?style=flat-square)]()

</div>

---

## What Is NLP2Shell?

NLP2Shell is a local desktop tool that sits in your terminal and converts natural language — typed or spoken — into executable shell commands using a fine-tuned language model. Everything runs **on your machine**. No cloud. No subscription. No copy-pasting from Stack Overflow.

```
$ nlp2shell

🎤  Listening...

You said  ──  "move all PDFs from Downloads to Documents"

┌─ Predicted Command ──────────────────────────────────────┐
│   mv ~/Downloads/*.pdf ~/Documents/                      │
└──────────────────────────────────────────────────────────┘

Run this? [y/n]: y
✓  Done.
```

---

## Why This Exists

Some tasks are genuinely annoying to type out:

```bash
# You want to do this:
"set 6 alarms between 7am and 9am"

# Instead of googling and hand-crafting:
for i in $(seq 0 5); do at 07:$(printf '%02d' $((i * 20))) <<< "notify-send Alarm"; done
```

NLP2Shell bridges that gap. You describe what you want. It figures out the command. You confirm and run it.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        NLP2Shell                            │
│                                                             │
│   Voice Input ──► Whisper STT ──► Natural Language Text     │
│   Text Input  ──────────────────────────────────────────►  │
│                                                             │
│                    Fine-tuned Qwen2.5-0.5B                  │
│                    (LoRA adapter, CPU inference)             │
│                              │                              │
│                              ▼                              │
│                    Predicted Bash Command                    │
│                              │                              │
│                    ┌─────────▼─────────┐                    │
│                    │   Safety Layer    │                    │
│                    │  blocklist check  │                    │
│                    │  path validation  │                    │
│                    └─────────┬─────────┘                    │
│                              │                              │
│                    Confirm [y/n] → Execute                  │
└─────────────────────────────────────────────────────────────┘
```

### Core Modules

| Module | File | Purpose |
|---|---|---|
| Speech-to-Text | `src/stt.py` | Whisper tiny, mic input, silence detection |
| Inference | `src/predictor.py` | Loads LoRA adapter, runs prediction |
| Safety | `src/safety.py` | Blocklist, path validation, allowlist |
| Executor | `src/executor.py` | Confirm + subprocess, logs history |
| Pipeline | `src/pipeline.py` | Connects all modules |
| CLI | `cli/main.py` | Rich terminal UI, argument parsing |

---

## Tech Stack

### Inference (Local)
- **[Whisper](https://github.com/openai/whisper)** — speech to text, tiny model, CPU only
- **[Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)** — base LLM
- **[PEFT](https://github.com/huggingface/peft)** — LoRA adapter loading
- **[Rich](https://github.com/Textualize/rich)** — terminal UI

### Training (Kaggle T4 GPU)
- **[TRL SFTTrainer](https://huggingface.co/docs/trl)** — supervised fine-tuning
- **[BitsAndBytes](https://github.com/TimDettmers/bitsandbytes)** — 4-bit quantization (NF4)
- **[NL2Bash dataset](https://huggingface.co/datasets/AnishJoshi/nl2bash-custom)** — 26k NL→Bash pairs

---

## Hardware Requirements

| Component | Minimum | Recommended |
|---|---|---|
| RAM | 4 GB | 8 GB |
| Storage | 2 GB free | 5 GB free |
| GPU | Not required | Any CUDA GPU |
| CPU | Any x86-64 | i5 6th gen+ |

> Runs fully on CPU. Tested on Intel HD 520 with 8GB RAM.

---

## Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/nlp2shell.git
cd nlp2shell

# Install dependencies
pip install -e .

# Download model (first run only, ~300MB)
python -c "from src.predictor import load_model; load_model('models/nlp2shell-qwen-lora')"
```

### PyAudio (for voice mode)

```bash
# Linux
sudo apt-get install portaudio19-dev && pip install pyaudio

# macOS
brew install portaudio && pip install pyaudio

# Windows
pip install pipwin && pipwin install pyaudio
```

---

## Usage

```bash
# Voice mode (default)
python cli/main.py

# Text mode — type instead of speak
python cli/main.py --text

# Dry run — see predicted commands, never execute
python cli/main.py --safe

# Text + dry run — safest for exploring
python cli/main.py --text --safe
```

### Example Interactions

```bash
# File operations
"move all logs older than 7 days to archive"
→ find . -name "*.log" -mtime +7 -exec mv {} ./archive/ \;

# Search
"find all python files containing the word 'import torch'"
→ grep -rl "import torch" --include="*.py" .

# Directory management
"create folder structure for a new python project"
→ mkdir -p src tests docs && touch README.md requirements.txt

# System info
"show me how much disk space each folder in home is using"
→ du -sh ~/*/
```

---

## Safety

NLP2Shell will **never silently execute** a command. Every prediction goes through:

1. **Blocklist check** — `rm -rf`, `dd if=`, fork bombs, and 15+ other dangerous patterns are hard-blocked
2. **Path validation** — commands targeting `/etc`, `/sys`, `/boot`, `/dev` are rejected
3. **Mandatory confirmation** — every command requires explicit `y` before execution
4. **Execution log** — every run is logged to `~/.nlp2shell_history.log`

```bash
You said: "delete everything"

┌─ Predicted Command ──────────────────────────┐
│   rm -rf ~/*                                 │
└──────────────────────────────────────────────┘

⚠  BLOCKED — matches unsafe pattern: rm -rf
```

---

## Model Details

| Property | Value |
|---|---|
| Base model | Qwen2.5-0.5B-Instruct |
| Fine-tuning method | LoRA (r=16, α=32) |
| Training data | NL2Bash — 26,436 pairs |
| Training hardware | Kaggle T4 GPU (free tier) |
| Quantization | 4-bit NF4 (BitsAndBytes) |
| Inference device | CPU |
| Prompt format | Qwen chat template |
| Parameters trained | ~0.66% (LoRA only) |

---

## Project Structure

```
nlp2shell/
├── src/
│   ├── stt.py          # Whisper speech-to-text
│   ├── predictor.py    # Model inference
│   ├── safety.py       # Command safety checks
│   ├── executor.py     # Confirm + execute
│   └── pipeline.py     # Main loop
├── cli/
│   └── main.py         # Rich terminal UI
├── training/
│   └── finetune.ipynb  # Kaggle training notebook
├── models/             # LoRA adapter weights (gitignored)
├── data/               # Training datasets (gitignored)
├── config.yaml         # User settings
└── GEMINI.md           # AI agent context file
```

---

## Roadmap

- [x] Dataset preparation and cleaning
- [x] LoRA fine-tuning on NL2Bash (Qwen2.5-0.5B)
- [ ] Local inference pipeline (`src/`)
- [ ] Rich CLI interface
- [ ] Voice input via Whisper
- [ ] Evaluation metrics (exact match, BLEU, execution success)
- [ ] Upgrade to Phi-3.5-mini (background training)
- [ ] Shell history learning — fine-tune on user's own commands
- [ ] Multi-command pipeline support

---

## Limitations

- Complex chained commands (`cmd1 | cmd2 | sort | uniq`) may be less accurate
- Model does not have internet access or knowledge of your filesystem
- Whisper tiny model may struggle with heavy accents or noisy environments
- First inference after cold start takes ~30-60 seconds on CPU (model loading)

---

## Built By

**Hassan Nawaz** — 4th semester BS Data Science student  
Built as a portfolio project exploring NLP + systems intersection.

> *"I wanted a faster way to do everyday terminal tasks without memorizing every flag and syntax. This is that."*

---

## Acknowledgements

- [TellinaTool/nl2bash](https://github.com/TellinaTool/nl2bash) — original NL2Bash research
- [Qwen Team @ Alibaba](https://github.com/QwenLM/Qwen2.5) — base model
- [Hugging Face](https://huggingface.co) — training infrastructure and model hub
- [Kaggle](https://kaggle.com) — free GPU compute

---

<div align="center">

**NLP2Shell** — because life is too short to remember every bash flag.

*MIT License · Made with terminal love*

</div>
