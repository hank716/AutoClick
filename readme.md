# PrayForTrump

A lightweight desktop auto key sequence runner with randomized timing, built with Python and Tkinter.

> **PrayForTrump** is a personal-use automation tool that allows you to record keyboard sequences and replay them in a loop with configurable randomness, simulating more human-like input behavior.

---

## Features

- Record custom keyboard sequences in real time
- Replay key sequences in a loop
- Independent randomization for:
  - Delay between individual key presses
  - Rest time between each full loop
- Live preview of randomized timing ranges
- Simple GUI (Tkinter-based)
- Always-on-top window option
- Start / Stop execution at any time

---

## Screenshot

*(Optional – you can add a screenshot here later)*

```text
[ GUI Screenshot ]
````

---

## Requirements

* Python **3.9 – 3.11**
* Windows OS (recommended)

### Python Dependencies

```txt
keyboard>=0.13.5
pydirectinput>=1.0.4
```

> `tkinter`, `threading`, `time`, and `random` are part of the Python standard library.

---

## Installation

### Option 1: Using `venv` (Recommended)

```bash
python -m venv venv
```

Activate the virtual environment:

* **Windows (PowerShell)**

```powershell
.\venv\Scripts\Activate.ps1
```

* **Windows (cmd)**

```cmd
venv\Scripts\activate
```

* **Linux / macOS**

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

### Option 2: Using Conda

```bash
conda create -n prayfortrump python=3.10 -y
conda activate prayfortrump
pip install -r requirements.txt
```

---

## Usage

Run the application:

```bash
python PrayForTrump.py
```

### Basic Workflow

1. Click **開始錄製** to start recording key presses
2. Press the keys you want to automate
3. Click **開始錄製** again to stop recording
4. Adjust:

   * Base key delay
   * Key delay randomization
   * Loop rest time
   * Loop randomization
5. Click **啟動循環**
6. Click **停止** to stop execution

---

## Randomization Logic

* **Key delay**

  * Randomized independently for each key press
* **Loop delay**

  * Randomized independently after each full sequence
* Random ranges are displayed in real time for transparency

This design reduces detection risk in systems that monitor fixed-interval automation.

---

## Important Notes

### Keyboard Permission

* **Windows**

  * Must be run as **Administrator**
* **Linux**

  * Requires root privileges or udev configuration
* **Wayland**

  * Not supported (use X11 instead)

### Platform Compatibility

* Fully supported on **Windows**
* Limited or unreliable behavior on **Linux / macOS**
* `pydirectinput` is Windows-focused

---

## Safety & Disclaimer

This project is intended for **personal learning and private automation use only**.

* Do not use in online games, competitive platforms, or services that prohibit automation
* The author is not responsible for any account bans or violations caused by misuse

---

## Project Structure

```text
PrayForTrump/
├── PrayForTrump.py
├── requirements.txt
├── README.md
└── venv/        # or conda environment
```

---

## Author

**Hank**

---

## License

This project is provided as-is for educational purposes.
No warranty is implied or provided.