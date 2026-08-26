# ASCII Art & Terminal Renderer

A collection of real-time ASCII rendering experiments built with **Python, mathematics, and terminal graphics**.

What started as a simple terminal ASCII renderer gradually evolved into experiments involving **3D objects, lighting, perspective projection, RGB video rendering, animation, and synchronized audio playback**.

The goal of this project is simple:

> **Explore how far graphics can be pushed using mathematics, characters, ANSI escape sequences, and a terminal — without relying on a conventional graphics engine.**

Everything is designed to run directly inside a terminal.

---

## ✨ Features

### 🎨 ASCII Rendering

* Brightness-based ASCII rendering
* Customizable ASCII character gradients
* Real-time terminal rendering
* Configurable rendering resolution
* Automatic terminal-size detection
* ANSI color rendering

### 🧊 3D ASCII Objects

The project contains several mathematical 3D rendering experiments:

* Rotating solid cube
* Shaded sphere
* Donut / torus
* Planet
* Black hole
* Other procedural 3D experiments

These objects are rendered directly in the terminal without a traditional graphics engine.

### 🎬 ASCII Video

The project can convert video frames into ASCII art in real time.

Features include:

* Video → RGB frame conversion
* Brightness-based ASCII mapping
* ANSI true-color rendering
* Configurable FPS
* Automatic terminal resolution
* Configurable maximum width
* RGB color smoothing
* Real-time terminal playback

### 🔊 Audio Playback

Video audio can be played simultaneously using **FFplay**.

The video and audio pipelines are handled separately:

```text
                 ┌──→ FFmpeg ──→ RGB Frames ──→ Python ──→ ASCII Terminal
Video ───────────┤
                 └──→ FFplay ──→ Audio
```

---

# 🛠️ Technologies

* **Python**
* **FFmpeg**
* **FFplay**
* **ANSI escape sequences**
* **Terminal rendering**
* **3D mathematics**
* **Vector mathematics**
* **Lighting calculations**
* **Perspective projection**
* **Depth buffering**
* **RGB color processing**

The core project uses Python's standard library and does not require external Python packages.

---

# 📋 Requirements

## Python

**Python 3.10+** is recommended.

Check your installation:

```bash
py --version
```

Example:

```text
Python 3.13.15
```

## FFmpeg

FFmpeg is required for video processing.

Check:

```bash
ffmpeg -version
```

FFplay is required for audio playback:

```bash
ffplay -version
```

Both commands should work directly from your terminal.

> **Windows:** If the commands are not recognized, make sure FFmpeg has been added to your system `PATH`.


---

# 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ASCII-Art.git
```

### 2. Enter the project directory

```bash
cd ASCII-Art
```

### 3. Create a virtual environment

```bash
py -m venv .venv
```

### 4. Activate the virtual environment

Windows:

```bash
.venv\Scripts\activate
```

### 5. Install requirements

```bash
py -m pip install -r requirements.txt
```

The project currently relies on Python's standard library, so no additional Python packages are required for the core renderers.

---

# 🧊 3D ASCII Renderers

All 3D renderers are located inside:

```text
ascii/
```

## Cube

Run:

```bash
py ascii\cube.py
```

The cube renderer demonstrates:

* Perspective projection
* Face filling
* Depth buffering
* Surface normals
* Lighting
* ASCII shading
* Real-time rotation

## Sphere

Run:

```bash
py ascii\sphere.py
```

The sphere is generated mathematically and uses lighting calculations to create a shaded 3D appearance.

## Donut

Run:

```bash
py ascii\donut.py
```

The donut is generated parametrically using two angular coordinates to construct a 3D torus.

## Planet

Run:

```bash
py ascii\planet.py
```

The planet renderer explores procedural spherical rendering and terminal-based shading.

## Black Hole

Run:

```bash
py ascii\blackhole.py
```

The black-hole renderer is another procedural experiment designed to explore visual effects using terminal characters and mathematical transformations.

---

# 🎬 ASCII Video Renderer

Place a video inside:

```text
assets/videos/
```

For example:

```text
assets/
└── videos/
    └── test.mp4
```

Run the basic ASCII video renderer:

```bash
py ascii\ascii_video.py assets\videos\test.mp4
```

The renderer processes video frames and converts them into ASCII characters for real-time terminal playback.

---

# 🌈 RGB ASCII Video

The RGB renderer extends the basic renderer by preserving the original video's colors.

Run:

```bash
py ascii\ascii_video_v3.py assets\videos\test.mp4
```

The rendering pipeline is approximately:

```text
Video Frame
     ↓
RGB Pixel Data
     ↓
Brightness Calculation
     ↓
ASCII Character Selection
     ↓
ANSI True-Color
     ↓
Terminal Output
```

This allows the ASCII characters to retain the approximate colors of the source video.

---

# ⚙️ Configuration

Most renderers contain configuration values near the beginning of the source file.

A typical configuration may look like:

```python
CHARS = " .:-=+*#%@"

FPS = 30

MAX_WIDTH = 120

COLOR_SMOOTHING = 0.20
```

The exact available settings depend on the renderer.

---

## ASCII Character Gradient

The character set determines how brightness is represented.

```python
CHARS = " .:-=+*#%@"
```

Characters near the beginning represent darker areas, while characters near the end represent brighter areas.

You can experiment with different character sets:

```python
CHARS = " .·:+=#%@"
```

---

# 📐 Resolution

For the RGB video renderer, the maximum width can be configured using:

```python
MAX_WIDTH = 120
```

For more detail:

```python
MAX_WIDTH = 160
```

or:

```python
MAX_WIDTH = 200
```

Higher resolutions require more processing because more characters have to be generated and rendered for every frame.

A reasonable starting point is:

```python
MAX_WIDTH = 120
```

---

# 🎞️ FPS

The target rendering FPS can be changed:

```python
FPS = 30
```

For slower systems:

```python
FPS = 15
```

or:

```python
FPS = 20
```

Higher FPS increases the amount of processing required.

If the renderer cannot keep up with the requested FPS, frames may be skipped.

---

# 🔊 Audio Delay

The RGB video renderer provides an adjustable audio delay:

```python
AUDIO_DELAY = 1.0
```

For example:

```python
AUDIO_DELAY = 2.0
```

can delay the audio to compensate for additional video-rendering latency.

The optimal value depends on the system and rendering workload.

---

# 🖥️ Recommended Terminals

For the best results, use a modern terminal emulator such as:

* **Windows Terminal**
* **PowerShell**
* **VS Code integrated terminal**

For high-resolution rendering, maximize or enlarge the terminal window.

---

# 🧠 How It Works

## 1. Video Decoding

FFmpeg reads the source video and converts it into raw RGB frames:

```text
video.mp4
    ↓
  FFmpeg
    ↓
RGB Frames
```

Python then processes these frames.

---

## 2. Brightness Calculation

Each RGB pixel is converted into an approximate perceived brightness using:

```text
Brightness =
0.299R +
0.587G +
0.114B
```

The result is approximately mapped to:

```text
0 → Dark
255 → Bright
```

The weighting gives green more influence because human vision is more sensitive to green than red or blue.

---

## 3. ASCII Mapping

The calculated brightness is mapped to a character from the configured character gradient:

```text
Dark
 ↓
" "
"."
":"
"="
"+"
"*"
"#"
"%"
"@"
 ↓
Bright
```

This creates the visual structure of the image using only terminal characters.

---

## 4. RGB Rendering

The original RGB information can be preserved using ANSI true-color escape sequences:

```text
ESC[38;2;R;G;Bm
```

This allows individual ASCII characters to be displayed using colors derived from the original video frame.

---

# 🧮 3D Rendering Pipeline

The 3D experiments use mathematical transformations instead of a conventional graphics engine.

A simplified pipeline looks like:

```text
3D Coordinates
      ↓
Rotation
      ↓
Lighting
      ↓
Perspective Projection
      ↓
Depth Calculation
      ↓
ASCII Shading
      ↓
Terminal
```

Depending on the renderer, the calculations can involve:

* Coordinate systems
* Rotation matrices
* Vector mathematics
* Surface normals
* Perspective projection
* Lighting
* Depth buffering
* Parametric surfaces

This makes the project a useful playground for understanding the fundamentals behind computer graphics.

---

# 🎯 Learning Goals

This project is primarily an experiment in understanding how graphical information can be represented without relying on a conventional graphics API.

It explores:

* Python programming
* Computer graphics
* 3D mathematics
* Vector mathematics
* Coordinate transformations
* Rendering pipelines
* Image processing
* Video processing
* ANSI terminal control
* Real-time rendering
* Performance optimization

The emphasis is on **learning by building and experimenting** rather than creating a production graphics engine.

---

# 🚧 Known Limitations

Terminal rendering is significantly slower than GPU-accelerated graphics.

RGB ASCII video can become CPU-intensive at higher resolutions.

A rough workload progression is:

```text
80 columns
    ↓
Low workload

120 columns
    ↓
Moderate workload

160 columns
    ↓
High workload

200+ columns
    ↓
Very high workload
```

Actual performance depends on:

* CPU
* Terminal emulator
* Video resolution
* ASCII resolution
* Target FPS
* ANSI color rendering
* Video complexity

---

# 🔮 Future Improvements

Possible future experiments include:

* Better audio/video synchronization
* Frame-timestamp synchronization
* Automatic FPS detection
* Adaptive resolution
* ANSI color optimization
* Neon/cyberpunk rendering
* Color trails
* Motion trails
* Particle effects
* ASCII webcam renderer
* ASCII image renderer
* Cascading ASCII effects
* Additional 3D objects
* 3D planetary systems
* Ray-marched ASCII scenes
* Interactive camera controls
* Mouse-controlled 3D camera
* Keyboard-controlled camera
* Terminal-based mini games

---

# 📸 Screenshots & Demos

Add screenshots and animated demonstrations here as the project develops.

Example:

```markdown
![ASCII Cube](screenshots/cube.png)
```

For an animated demo:

```markdown
![ASCII Video](screenshots/ascii-video.gif)
```

A good GitHub README can eventually showcase:

* 🧊 Rotating cube
* 🌐 Shaded sphere
* 🍩 Donut
* 🪐 Planet
* 🕳️ Black hole
* 🎬 RGB ASCII video

---

# 🤝 Contributing

Contributions, ideas, and rendering experiments are welcome.

Potential contributions include:

* New ASCII rendering techniques
* New mathematical 3D objects
* Performance improvements
* Rendering effects
* Terminal compatibility improvements
* Documentation improvements

---

# 👨‍💻 Author

**Niladri**

Electronics & Communication Engineering student interested in:

* 🔌 Embedded Systems
* 🤖 Robotics
* 🧠 Artificial Intelligence
* 🎨 Computer Graphics
* 🚀 Space Technology
* 💻 Software Development

---

# ⭐ Project Philosophy

> **What happens if we remove the graphics engine and try to build the visuals using mathematics, characters, and a terminal?**

That's the idea behind this project.

From a single ASCII character:

```text
@
```

to a rotating 3D object:

```text
      @@@@@
   @@@@@@@@@@@
  @@@@     @@@@
  @@@       @@@
  @@@@     @@@@
   @@@@@@@@@@@
      @@@@@
```

and eventually to real-time RGB video rendering.

The project is a collection of experiments exploring the boundary between **mathematics, programming, graphics, and the humble terminal.**

---

**Built with Python + Mathematics + Terminal Magic. 🐍⚡**
