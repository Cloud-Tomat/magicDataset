# Image Dataset Generator for Deep Learning

This tool automates the generation of image datasets for deep learning purposes by crawling images from Yandex image search. It is designed to streamline the process of preparing datasets optimized for deep learning models through various features including downloading, duplicate filtering, cropping, resizing, and more.

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

