# LABOCR

A small project from AT87.02 Deep Learning for Computer Vision at Asian
Institute of Technology Thailand. This project uses Tauri + ReactJS + Python +
Opencv + YOLOv11, for GUI, to detect, and to recognize seven segment displays
from measurement instruments.

<u><b>Small disclaimer</b></u>: The onnx model needs some improvement and can be
swapped out with your own onnx model for seven segment display.

## Guide to build it in LINUX:

- [x] Download rust programming language from https://www.rust-lang.org/
- [x] Download all necessary prerequistes to run tauri from
      https://v2.tauri.app/start/prerequisites/
- [x] Download python from https://www.python.org/
- [x] Pip install from py folder using requirements.txt
- [x] Change extension `stream-x86_64-unknown-linux-gnu` like in
      https://v2.tauri.app/develop/sidecar/ from build_py in package.json if
      needed
- [x] Make sure your --add-data in package json has the same path as you
      py/ocr.onnx so it can be used by the binary later on.
- [x] Go to terminal and type-enter `npm run tauri build`

## GUIDE to build it in WINDOWS:

- [x] Download rust programming language from https://www.rust-lang.org/
- [x] Download all necessary prerequistes to run tauri from
      https://v2.tauri.app/start/prerequisites/
- [x] Download python from https://www.python.org/
- [x] Pip install from py folder using requirements.txt
- [x] Change extension `stream-x86_64-pc-windows-msvc` like in
      https://v2.tauri.app/develop/sidecar/ from build_py in package.json if
      needed
- [x] Make sure your --add-data in package json has the same path as you
      py/ocr.onnx so it can be used by the binary later on.
- [x] Go to terminal and type-enter `npm run tauri build`

# ENJOY!!
