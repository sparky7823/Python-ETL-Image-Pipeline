# Python Web Scraper & ETL Image Pipeline

A comprehensive Python data pipeline that scrapes data from the web, respects network governance, and transforms raw HTML and binary image data into structured files and filtered graphics.

This repository demonstrates network request handling, HTML DOM parsing, data visualization, and modular software architecture.

## System Architecture
The repository is structured into two decoupled modules that interface through the main CLI router.
*   **Web Crawler Module:** Handles the Extract (E) and Load (L) phases. It parses DOM structures via `BeautifulSoup`, extracts data arrays, and exports structured CSVs and MatPlotLib charts.
*   **Image Processing Module:** Handles the Transform (T) phase. An independent matrix manipulation engine that recalculates RGB values and spatial layouts. 

## Core Features
*   **Network Governance:** Implements a strict `RequestGuard` class that fetches and parses a target domain's `robots.txt` file, actively blocking disallowed paths via Regex prior to issuing GET requests.
*   **Automated Link Traversal:** Recursively crawls domains, normalizing relative URLs, stripping anchor tags, and aggregating link frequencies to generate analytical histograms.
*   **Table Data Extraction:** Parses targeted DOM tables, converts extracted strings into floating-point numeric arrays, and plots multi-line trend graphs.
*   **Real-time Image Filtering:** Scrapes binary image payloads, routes them into the decoupled image processing engine, and saves modified versions (sepia, grayscale, mirrored) locally.

## Modular Usage

**Module 1: The Scraper Pipeline (`main.py`)**
*   **Link Crawler:** `python main.py -c <url> <graph_output.png> <csv_output.csv>`
*   **Table Plotter:** `python main.py -p <url> <graph_output.png> <csv_output.csv>`
*   **Image Pipeline:** `python main.py -i <url> <output_prefix> <filter_flag>`

**Module 2: The Independent Image Processor (`image_processing/main.py`)**
The image engine can be run entirely independently on local files without utilizing the web crawler.
*   `python main.py -s <input.png> <output.png>` (Sepia)
*   `python main.py -c <img1> <img2> <img3> <img4> <output.png> <thickness>` (Collage)
*   *See the README inside `/image_processor` for full documentation.*
