# Automated Videos

Automated Videos is a project designed to automate the creation of video content by converting text to speech, handling audio, and managing video segments. This README provides an overview of the project, installation instructions, configuration setup, and usage guidelines.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Contributing](#contributing)
6. [License](#license)

## Overview

The Automated Videos project automates the process of creating video content by generating audio from text and combining it with video segments. It supports various video formats and offers customizable options for intro/outro durations and segment durations. The goal is to streamline video production and enhance efficiency.

## Installation

To get started with Automated Videos, follow these steps:

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/automated-videos.git
    ```

2. **Navigate to the project directory:**

    ```bash
    cd automated-videos
    ```

3. **Create a virtual environment:**

    ```bash
    python -m venv venv
    ```

4. **Activate the virtual environment:**

    ```bash
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

5. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

6. **Set up the configuration file:**

    - Copy the configuration template:

      ```bash
      cp config/config.template.json config/config.json
      ```

    - Edit `config/config.json` to specify the voice settings. An example configuration is:

      ```json
      {
        "voices": {
          "en": "en-US-GuyNeural",
          "pt": "pt-BR-FranciscaNeural"
        }
      }
      ```

## Configuration

1. **Configuration File:**

   The configuration file is located at `config/config.json`. This file contains the settings for different voice configurations. Modify it to fit your specific needs.

2. **Updating the Configuration Path:**

   If you place the configuration file in a different location, ensure that you update the path in your code to reflect the new location.

## Usage
