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

#### Windows
* Install torch with CUDA support

```cmd
pip install torch==2.2.1+cu121 -f https://download.pytorch.org/whl/torch_stable.html
```

* Install Chrome if not already done

* Install dlib 
Follow the instructions here: 

https://medium.com/analytics-vidhya/how-to-install-dlib-library-for-python-in-windows-10-57348ba1117f

* Then, install the rest of the dependencies from your `requirements.txt` file:

```cmd
pip install -r requirements.txt
```
#### Linux
* Install torch with CUDA support
```cmd
pip install torch==2.2.1+cu121 -f https://download.pytorch.org/whl/torch_stable.html
```

* Install Packaged required to build dlib (ubuntu distribs)
```cmd
sudo apt update 
sudo apt install libopenblas-dev liblapack-dev
sudo apt install cmake
sudo apt-get install build-essential
sudo apt install python[version]-dev
sudo apt-get install libgl1
```

* Install Chrome if not already done
```cmd
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```

* And finally install requirements
```cmd
pip install -r requirements-linux.txt
```

## Running the Application

Copy `exampleConf.yaml` to a new file and adapt the content to your needs. The YAML file is heavily commented for easy understanding.

Activate the virtual environment if not already done:

```cmd
.\magicDataset\Scripts\activate
```

Run the script:

```cmd
python magicDataset.py examples/full_example.yaml
```

## YAML File Description

### General configuration

Pass where to place the image
```yaml
outDir: &outDir "output"
```
CUDA device to use in PCI ID order
```yaml
cudaDevice : 1
```

Each section is optional
### Search Section
```yaml
search:
  enable: true        # enable search module
  engine: yandex      # image search engine, today support yandex, more will come in the future
  targetDir: *outDir  # path of the target directory for download
  debug : false       # show actions in chrome browser visible or not
  minResolution: 2    # Minimum image resolution in MegaPixel
  searches:            # list of search to perform [search request, number of images]
    - [photo of a man, 100] # will download 100 images matching with min resolution of 2M 
    - [indian man, 50] # will download 50 images matching with min resolution of 2M
```

### Remove duplicate
Move similar image and place them in duplicate folder
```yaml
duplicateFilter:
  enable: true       # enable this filter
  sourceDir: *outDir  # where are the file to analyze
  threshold: 5        # hash distance, below image are considered identical
```

### Remove watermark
Move watermarked image to watermarked folder
This filter just detects if there is a text in the central part of the image
```yaml
watermarkFilter:
  enable: true
  sourceDir: *outDir    # where are the file to analyze  
  # watermark search will be performed on a temporary center crop
  # this avoids considering signature and small corner overlay text
  searchCropPercent: 70
```

### Crop & Resize
This part does the following:
* Crop to the maximum possible size to have the specified homothetic ratio.
* Resize the image to the specified dimension.
* Filter per number of faces to move image to wrongNumberofFace folder if more than one face or no face are detected.
```yaml
cropAndResize:
  enable: true          # enable this feature
  sourceDir: *outDir    # where are the file to analyze
  resize:
    enable: true        # enable large image resize
    dimension: [512,512]  # homothetic resizing to this max dimension
    keepFace: True
  filter:
    eliminateMultiFaces: true   # remove photo with more than 1 face  
    eliminateNoFace: true       # remove photo with no face
```

### Q&A filter & Captioning

Filter images based on question and answer. Caption the image based on a template pattern.
```yaml
lavisFilterAndCaption:
  enable: true        # enable this filter
  sourceDir: *outDir  # where are the file to analyze
  questions:
    - question: "is it a man?"
      expectedAnswers: ["yes","man"]
    - question: "face visible?"
      expectedAnswers: ["yes"]
    - question: "is it a color photo?"
      expectedAnswers: ["yes"]
  caption: "a man, {describe face emotion.,1,1} face, {ethnicity of the person,1,1} ethnicity, {describe the clothes.,5,8}, {describe hair., 1,1} hairs, {describe the background.,5,8} background"
```


## Contributing

Contributions are welcome to enhance the tool's capabilities, such as adding support for more image search engines or improving image processing features. Feel free to submit issues and pull requests.
