📺 ASCII Video Art on Android with Termux

Turn ordinary videos into animated ASCII art directly from an Android phone using the "Termux" (https://termux.dev/) terminal, Python, and FFmpeg.

No PC is required.

The project converts video frames into grayscale ASCII characters and continuously renders them in the Termux terminal to create a moving ASCII-art version of the original video.

«🚧 This project is experimental and currently focused on learning, experimentation, and creating interesting terminal-based visuals.»

---

✨ What This Project Does

        🎥 Video
           │
           ▼
        FFmpeg
           │
           ▼
   Extract video frames
           │
           ▼
     Grayscale image
           │
           ▼
      ASCII mapping
           │
           ▼
   Smooth frame rendering
           │
           ▼
     🖥️ Termux Terminal
           │
           ▼
     🎬 ASCII Video Art

Dark areas of an image are represented by lighter ASCII characters, while brighter areas use denser characters.

Example:

        .:-=+*#%@
      .:-=+*##%%@
    .:=+*##%%%%%%
   :-+*##%%%%%%%%
   =*##%%%%@@@@%%
   *##%%%@@@@@@%%

---

📱 Requirements

You need:

- Android phone
- Termux
- Python
- FFmpeg
- A video file
- Basic knowledge of using the terminal

A computer is not required.

---

🛠️ Installation

1. Install Termux

Install Termux from a trusted source such as F-Droid or the official Termux project.

After opening Termux, update the package repository:

pkg update
pkg upgrade

---

2. Install Required Packages

Install Python, FFmpeg, and Git:

pkg install python ffmpeg git

Check that they were installed:

python --version
ffmpeg -version
git --version

---

📂 3. Give Termux Storage Access

Run:

termux-setup-storage

Android will ask for storage permission.

Select Allow.

Termux will create convenient storage shortcuts inside:

~/storage/

Your shared Android storage can normally be accessed through:

~/storage/shared/

which points to:

/storage/emulated/0/

---

📁 4. Create the Project

Create a project directory:

mkdir ascii-video

Enter it:

cd ascii-video

Create the Python renderer:

nano ascii_video.py

Paste the Python renderer from this repository into the file.

Save it with:

CTRL + O
Enter
CTRL + X

Your project should now look approximately like:

ascii-video/
└── ascii_video.py

---

🎥 5. Find a Video on Your Android Phone

Videos can be stored in locations such as:

/storage/emulated/0/DCIM/
/storage/emulated/0/Download/
/storage/emulated/0/Movies/

You can search for videos using:

find /storage/emulated/0 -type f \
\( -iname "*.mp4" -o -iname "*.mov" -o -iname "*.gif" \) \
2>/dev/null | head -50

For example:

/storage/emulated/0/Download/example.mp4

---

▶️ 6. Run the ASCII Renderer

From inside the project directory:

cd ~/ascii-video

Run:

python ascii_video.py "/storage/emulated/0/Download/example.mp4"

If the path contains spaces, keep the entire path inside quotation marks:

python ascii_video.py "/storage/emulated/0/My Videos/example video.mp4"

The video will be converted into ASCII frames and displayed directly inside the Termux terminal.

---

🧠 How It Works

The renderer uses FFmpeg to decode the input video.

Each frame goes through roughly this process:

Video
  ↓
FFmpeg
  ↓
Individual frames
  ↓
Resize
  ↓
Grayscale
  ↓
Brightness values
  ↓
ASCII character mapping
  ↓
Terminal rendering

The brightness of each pixel determines which ASCII character is used.

The renderer uses a character gradient such as:

" .:-=+*#%@"

Conceptually:

Dark ─────────────────────── Bright

  .   :   -   =   +   *   #   %   @
  ↑                               ↑
Less dense                    More dense

This allows an image to be represented using only text characters.

---

🎞️ Smooth Animation

The renderer doesn't simply print one frame after another.

It maintains a brightness matrix and interpolates between consecutive frames.

This creates a smoother transition:

Frame A
   ███
   ███

      ↓

   ███
  ████

      ↓

  ████
 █████

Instead of:

Frame A
██████

Frame B
     ████

Frame C
          ███

The goal is to make the ASCII representation visually follow the movement of the original video.

---

⚙️ Customization

The renderer contains several settings near the top of the Python file.

ASCII character set

CHARS = " .:-=+*#%@"

You can experiment with different character sets.

For example:

CHARS = " .·:*#@"

or:

CHARS = " .░▒▓█"

---

Resolution

The renderer uses:

WIDTH = min(shutil.get_terminal_size().columns - 2, 80)
HEIGHT = 32

Increasing the resolution can produce more detailed ASCII art, but it also increases the amount of text the phone has to render.

For slower devices, try:

HEIGHT = 25

---

Frame Rate

The current renderer uses:

FPS = 15

You can experiment with:

FPS = 10

or:

FPS = 20

Higher FPS generally produces smoother motion but requires more processing.

---

Smoothness

The interpolation strength is controlled by:

SMOOTHING = 0.45

Lower values produce slower transitions.

Higher values make the ASCII image respond more quickly to the original video.

Try experimenting with:

SMOOTHING = 0.30

SMOOTHING = 0.45

SMOOTHING = 0.70

---

⏹️ Stop the Renderer

While the animation is running, press:

CTRL + C

This stops the Python program.

---

📱 Why Termux?

Termux provides a Linux-like environment directly on Android.

That makes it possible to use familiar developer tools such as:

Python
FFmpeg
Git
Shell
SSH
GCC
Node.js

without requiring a traditional computer.

This project is an experiment in seeing how far an Android phone can be pushed as a small development and content-creation environment.

---

🚀 Development Roadmap

The project is being developed incrementally.

V1 — Basic ASCII Video ✅

Video
 ↓
FFmpeg
 ↓
ASCII frames
 ↓
Terminal

V2 — Cascade Experiment 🧪

Experimented with falling/cascading ASCII characters.

This version demonstrated a digital-rain style reveal but was intentionally removed from the main rendering approach because the goal is smooth video animation rather than vertical sliding effects.

V3 — Smooth ASCII Video ✅

Current direction:

Video
 ↓
Grayscale
 ↓
Brightness interpolation
 ↓
ASCII conversion
 ↓
Smooth terminal animation

Future Ideas 🚀

Possible future improvements:

- [ ] ANSI terminal colors
- [ ] Green/cyberpunk mode
- [ ] Better character aspect-ratio correction
- [ ] Automatic terminal-size detection
- [ ] Video duration controls
- [ ] Image-to-ASCII mode
- [ ] Audio support
- [ ] Glitch effects
- [ ] Digital-rain effects
- [ ] Export ASCII animation directly to a video file
- [ ] Preset visual styles
- [ ] Command-line arguments for customization

---

🎬 Content Creation

This project can also be used as a small experimental content-creation tool.

For example:

Original video
      ↓
ASCII conversion
      ↓
Terminal animation
      ↓
Screen recording
      ↓
Short-form video

Possible content ideas:

- Cyberpunk ASCII animations
- Sci-fi terminal visuals
- Programming-themed Shorts
- Linux/Termux experiments
- “I made this using only my Android phone”
- ASCII versions of original footage
- Terminal visualizers

---

🧪 Project Philosophy

This project started as a simple question:

«How much can I create with just an Android phone and a terminal?»

Rather than immediately building a complicated application, the project is developed step-by-step:

Experiment
   ↓
Understand
   ↓
Build
   ↓
Improve
   ↓
Document

The goal is not just to create ASCII videos, but to learn about:

- Python
- FFmpeg
- Image processing
- Video frames
- Terminal rendering
- Animation
- Git/GitHub
- Android/Linux environments

---

🤝 Contributing

Suggestions, improvements, optimizations, and new visual effects are welcome.

If you experiment with the renderer and create a better algorithm, feel free to contribute.

---

⚠️ Limitations

Terminal rendering is not designed to be a high-performance video renderer.

Performance depends heavily on:

- Android device
- Terminal emulator
- Video resolution
- ASCII resolution
- FPS
- Terminal rendering speed

For longer or high-resolution videos, performance may decrease significantly.

Short clips are recommended for experimentation.

---

📜 License

Choose a license appropriate for your project before publishing.

If you want others to freely use, modify, and distribute the code, an MIT License is a common choice.

---

⭐ If You Try It

If you create something interesting with this project, consider sharing it and documenting what you changed.

Made on Android. Built with Termux. Powered by Python + FFmpeg. 📱🐍🎬
