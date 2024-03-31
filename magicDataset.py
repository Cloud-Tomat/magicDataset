import os
import yaml
import argparse
import logger




#read argument (conf file)
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


#set cuda device
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = str(data["cudaDevice"])



if data.get("search", {}).get("enable", False):
    logger.console("starting download process")
    import download
    download.startCrawler(data["search"])

if data.get("duplicateFilter", {}).get("enable", False):
    logger.console("detecting duplicated image")    
    import removeDuplicate
    removeDuplicate.remove_duplicate_images(data["duplicateFilter"]["sourceDir"])

if data.get("watermarkFilter", {}).get("enable", False):
    import watermarkFilter
    watermarkFilter.process_images(data["watermarkFilter"])

if data.get("cropAndResize", {}).get("enable", False):
    import cropResize
    cropResize.process_images(data["cropAndResize"])

if data.get("lavisFilterAndCaption", {}).get("enable", False):
    import filter_captionPhoto
    filter_captionPhoto.filterAndCaption(data["lavisFilterAndCaption"])

