# Image Dataset Generator for Deep Learning

Deep Learning generative AI training requires a large image dataset; the quality of the dataset significantly influences the quality of the results. Many datasets are available for download, but most of them are synthetic (AI-generated). The goal here is to be able to generate a large image dataset from the real world.

The main problem we face is the difficulty of legally sharing large image datasets, as most images on the internet are copyrighted.

The tool we propose here automates the following processes:
* Download a large dataset of images based on automation of a set of searches on web image search engines.
* Exclude images not suitable for training:
  - Remove images too similar based on their perceptual hash distance.
  - Remove watermarked images.
  - Filter using lavis img2text question/expected answer, allowing to keep only the images representing what you want to train for.
* Crop & Resize:
  - Downsample very large images.
  - Face crop.
  - Remove borders.



## Installation Guide

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

* Windows
```cmd
.\magicDataset\Scripts\activate
```
* Linux
```cmd
source ./magicDataset/bin/activate
```
 
You should now see `(magicDataset)` at the beginning of your command prompt line, indicating that the virtual environment is activated.

### Install Dependencies

* Windows
Install torch with CUDA support

```cmd
pip install torch==2.2.1+cu121 -f https://download.pytorch.org/whl/torch_stable.html
```

Then, install the rest of the dependencies from your `requirement.txt` file:

```cmd
pip install -r requirement.txt
```
* Linux
TODO

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
- Filters images based on LAVIS question / expected answers
- Generates captions using LAVIS based on question-and-answer pairs and predefined templates.

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

