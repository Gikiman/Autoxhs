# Autoxsh

<div align="center">
    <img src="assets/Autoxhs.png" width="80%">
</div>

> Autoxsh is an open-source tool for generating and publishing content on Xiaohongshu (Little Red Book), leveraging OpenAI's API for automatic title, content, and tag creation.

## Features

- **Automated Content Creation**: Utilizes OpenAI's API to generate engaging titles, content, and tags.
- **LangGPT Prompt Generation**: Employs the LangGPT project methodology for creating structured and high-quality ChatGPT prompts.
- **Customizable**: Offers configuration options for prompt customization and model selection.
- **Easy to Use**: Streamlit-based interface for a user-friendly experience.

## Table of Contents

- [Autoxsh](#autoxsh)
  - [Features](#features)
  - [Table of Contents](#table-of-contents)
  - [Demo](#demo)
  - [Installation](#installation)
  - [Get Started](#get-started)
  - [Configuration](#configuration)
  
## Demo
A quick demonstration of Autoxsh in action (video accelerated for brevity):

<div align="center">
    <img src="assets/demo.gif">
</div>

## Installation
To install Autoxsh, follow these steps:
```bash
# Create a new conda environment with Python 3.9
conda create -n Autoxsh python=3.9

# Activate the conda environment
conda activate Autoxsh

# Clone the Autoxsh repository to your local machine
git clone https://github.com/Gikiman/Autoxhs.git

# Navigate to the Autoxsh project directory
cd Autoxhs

# Install dependencies from requirements.txt
pip install -r requirements.txt
```

## Get Started

After installing, you can start using Autoxsh by:
1. Enter your OpenAI API key in the .env file:
```bash
OPENAI_API_KEY=your_api_key_here
```
2. Launch the application with the following command:
```bash
streamlit run streamlit.py
```
> Note: A high-speed internet connection is required, and users in China should use a proxy.

## Configuration
- Prompt Customization: Modify generation prompts in the `data\prompt` folder using the LangGPT methodology.
- Model Selection: Default models are `gpt-4-0125-preview` for text and `dall-e-3` for images. These can be changed in `config\setting.py`.