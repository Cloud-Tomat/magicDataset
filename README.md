# Image Dataset Generator for Deep Learning

This tool automates the generation of image datasets for deep learning purposes by crawling images from Yandex image search. It is designed to streamline the process of preparing datasets optimized for deep learning models through various features including downloading, duplicate filtering, cropping, resizing, and more.

## Installation Guide

This guide provides step-by-step instructions for setting up the project on a Windows machine. Follow these steps to clone the repository, set up a Python virtual environment, and install the necessary dependencies.

### Prerequisites

Ensure you have the following installed:
- Git ([Download Git](https://git-scm.com/download/win))
- Python 3 ([Download Python](https://www.python.org/downloads/))
- NVIDIA GPU compatible with CUDA
- Chrome browser 

### Clone the Repository

First, clone the repository using Git. Open your command prompt (CMD) or PowerShell, navigate to the directory where you want to clone the repository, and run:

```cmd
git clone https://github.com/Cloud-Tomat/magicDataset
cd magicDataset
```

### Set Up a Virtual Environment

Next, create a Python virtual environment in the repository directory. This environment will be used to install and isolate the project's Python dependencies.

```cmd
python -m venv magicDataset
```

Activate the virtual environment:

```cmd
.\magicDataset\Scripts\activate
```

You should now see `(magicDataset)` at the beginning of your command prompt line, indicating that the virtual environment is activated.

### Install Dependencies

Install torch with CUDA support

```cmd
pip install torch==2.2.1+cu121 -f https://download.pytorch.org/whl/torch_stable.html
```

Then, install the rest of the dependencies from your `requirement.txt` file:

```cmd
pip install -r requirement.txt
```

## Running the Application

copy exampleConf.yaml to a new file
adapt the content to you need, the yaml is heavily commented

Activate the virtual environment if not already done

```cmd
.\magicDataset\Scripts\activate
```

run the script
```cmd
python magicDataset.py your_configuration_file.yaml
```

## Features

### Image Crawling
- **Engine**: Utilizes Yandex for image search with plans to support more engines in the future.
- **Searches**: Perform specified searches with queries and desired number of images.
- **Minimum Resolution**: Only downloads images above a certain resolution threshold.

### Duplicate Image Filtering
- Filters out duplicate images based on hash distance to ensure dataset uniqueness.

### Crop and Resize
- **Resize**: Automatically resizes images larger than specified dimensions.
- **Face Crop**: Crops images to focus on faces, adjustable by the percentage of the biggest face.
- **Crop Borders**: Refines image focus by cropping borders by a specified percentage.

### LAVIS Filter and Captioning
- Filters images and generates captions using LAVIS based on question-and-answer pairs and predefined templates.

### Watermark Filter
- Removes watermarked images to clean the dataset, focusing on a central crop for effective watermark detection.

## Configuration

The tool is configurable through a YAML file, allowing for detailed customization of its operation, including:
- CUDA device selection for processing.
- Target directory for saving downloaded images.
- Debug mode for browser action visibility.
- Configurations for search parameters, duplicate filtering, image cropping, resizing, and more.

## Usage

Define your configuration in a YAML file as shown in the example provided. Each section corresponds to a configurable feature module of the tool, including `search`, `duplicateFilter`, `cropAndResize`, `lavisFilterAndCaption`, and `watermarkFilter`.

Ensure all dependencies are installed and run the tool with your YAML configuration file as the input.

## Contributing

Contributions are welcome to enhance the tool's capabilities, such as adding support for more image search engines or improving image processing features. Feel free to submit issues and pull requests.

