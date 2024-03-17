import os
import yaml
import argparse

parser = argparse.ArgumentParser(description='Process configuration file.')
parser.add_argument('config_file', type=str, help='The name of the YAML configuration file.')

args = parser.parse_args()


#file_path = 'exampleConf.yaml'
file_path=args.config_file



with open(file_path, 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)  # In



os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = str(data["cudaDevice"])

print(data["search"])
if data["search"]["enable"]:
    import download
    download.startCrawler(data["search"])


if data["duplicateFilter"]["enable"]:
    import removeDuplicate
    removeDuplicate.remove_duplicate_images(data["duplicateFilter"]["sourceDir"])

if data["watermarkFilter"]["enable"]:
    import watermarkFilter
    watermarkFilter.process_images(data["watermarkFilter"])

if data["cropAndResize"]["enable"]:
    import cropResize
    cropResize.process_images(data["cropAndResize"])

if data["lavisFilterAndCaption"]["enable"]:
    import filter_captionPhoto
    filter_captionPhoto.filterAndCaption(data["lavisFilterAndCaption"])

