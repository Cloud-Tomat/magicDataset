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
Follow the instructions here : 

https://medium.com/analytics-vidhya/how-to-install-dlib-library-for-python-in-windows-10-57348ba1117f

* Then, install the rest of the dependencies from your `requirement.txt` file:

```cmd
pip install -r requirement.txt
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
pip install -r requirement-linux.txt
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
python magicDataset.py examples/full_example.yaml
```

## yaml file description

### General configuration

Pass where to place the image
```cmd
outDir: &outDir "output"
```
CUDA device to use in PCI ID order
```cmd
cudaDevice : 1
```

Each section are optionnal
### Search Section
```cmd
search:
  enable: true        #enable serach module
  engine: yandex      #image search engine, today support yandex, more will come in the future
  targetDir: *outDir  #path of the target directory for download
  debug : false       #show actions in chrome browser visible or not
  minResolution: 2    #Minimum image resolution in MegaPixel
  searchs:            #list of search to perform [search request, number of images]
    - [photo of a man, 100] #will download 100 images matching with min resolution of 2M 
    - [indian man, 50] #will download 50 images matching with min resolution of 2M
```

### Remove duplicate
Move similar image and place them in duplicate folder
```cmd
duplicateFilter:
  enable: true       #enable this filter
  sourceDir: *outDir  #where are the file to analyze
  threshold: 5        #hash distance, below image are considered identical

```
### Remove duplicate
Move watermarked image to watermked folder
This filter just detect if there is a text in the central part of the image
```cmd
watermarkFilter:
  enable: true
  sourceDir: *outDir    #where are the file to analyze  
  #watermak search will be performed on a temporary center crop
  #this avoid to consider signature and small corner overlay text
  searchCropPercent: 70
```
### Crop & Resize
This part does the following:
* Crop
Perform a crop to the maximum possible size to have the specified homothetic ratio.
In the example below we ask for 512x512 image meaning the crop will be the biggest possible size.
If keepFace is enabled, the algorithm ensure that the bigest face in the image will be in the crop area, usefull when the face is not in the center part of the image (for instance a personn standing).
If not enabled or if no face are detected perform a central crop.
* Resize
Resize the image to the specified dimension.
* Filter per number of faces
You can specify here to move image to wrongNumberofFace folder if more than one face or no face are detected.

```cmd
cropAndResize:
  enable: true          #enable this feature
  sourceDir: *outDir    #where are the file to analyze
  #Kohya doesn't like very large image
  resize:
    enable: true          #enable large image resize
    dimension: [512,512]  #homothetic resizing to this max dimension
    keepFace: True
  filter:
    eliminateMutliFaces: true   #remove photo with more than 1 face  
    eliminateNoiFace: true   #remove photo with No  face
```
### Q&A filter & Captionning

This is the cherry on the cake. This section allows to :
* Filter image based on question and answer resulting BLIP image to text
  just ask question and tell what are the expected answer.
  If expected answer doesn't match, move the image to discarded folder.
* Caption the image based on a template pattern
Just type the caption text, insert between { } the question to BLIP specifying min and max length


```cmd
lavisFilterAndCaption:
  enable: true        #enable this filter
  sourceDir: *outDir    #where are the file to analyze
  #list of question and expected answers, if answer of lavis not in expected answer,
  #image will be mvoe to discarded foldere
  questions:
    - question: "is it a man?"
      expectedAnswers: ["yes","man"]

    - question: "face visible?"
      expectedAnswers: ["yes"]

    - question: "is it a color photo?"
      expectedAnswers: ["yes"]
  #template for captionning
  #Question between { }, 3 arguments expected, the question, min answer length and max answer length
  caption: "a man,  {describe face emotion.,1,1} face, {ethnicity of the person,1,1} ethnicty, {describe the clothes.,5,8}, {describe hair., 1,1} hairs,  {describe the background.,5,8} background"

```



## Usage

Define your configuration in a YAML file as shown in the example provided. Each section corresponds to a configurable feature module of the tool, including `search`, `duplicateFilter`, `cropAndResize`, `lavisFilterAndCaption`, and `watermarkFilter`.

Ensure all dependencies are installed and run the tool with your YAML configuration file as the input.

## Contributing

Contributions are welcome to enhance the tool's capabilities, such as adding support for more image search engines or improving image processing features. Feel free to submit issues and pull requests.

