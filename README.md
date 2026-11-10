# CLI Image Processing Engine

A command-line image processing tool written in Python. This engine parses raw image files, manipulates RGB pixel data via 2D arrays, and outputs modified images based on user-defined CLI flags. 

This project demonstrates array manipulation, algorithmic constraint checking, and backend command-line routing.

## Features
*   **RGB Channel Manipulation:** Implements mathematical filters for sepia and grayscale by recalculating pixel weights.
*   **Spatial Transformations:** Mirrors and flips pixel matrices across X/Y axes.
*   **Chroma Keying (Green Screen):** Uses dynamic thresholding to isolate and replace specified color bounds with a secondary background image matrix.
*   **Image Compositing:** Combines multiple images into structured collages with dynamic border offsets.

## Architecture & Logic
The engine operates entirely through a CLI router. It validates input parameters and routes the data to the appropriate processing function. To prevent data corruption, operations like the sepia filter include strict bounding logic to prevent RGB values from overflowing the 255 8-bit color maximum.

*(Note: This logic relies on `byuimage`, a proprietary university abstraction library, and is hosted here as an architectural logic demonstration.)*

## Usage Documentation
The engine is executed via the command line using specific operational flags. 

**Basic Transformations**
*   `python main.py -s <input.png> <output.png>` (Sepia)
*   `python main.py -g <input.png> <output.png>` (Grayscale)
*   `python main.py -f <input.png> <output.png>` (Flip Vertically)
*   `python main.py -m <input.png> <output.png>` (Mirror Horizontally)

**Advanced Compositing**
*   **Darken:** `python main.py -k <input.png> <output.png> <percent>`
*   **Borders:** `python main.py -b <input.png> <output.png> <thickness> <R> <G> <B>`
*   **Collage:** `python main.py -c <img1> <img2> <img3> <img4> <output.png> <thickness>`
*   **Green Screen:** `python main.py -y <foreground> <background> <output.png> <threshold> <factor>`
