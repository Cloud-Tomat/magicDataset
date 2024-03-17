import os
import yaml
file_path = 'exampleConf.yaml'


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

if data["cropAndResize"]["enable"]:
    import cropResize
    cropResize.process_images(data["cropAndResize"])

if data["duplicateFilter"]["enable"]:
    import removeDuplicate
    removeDuplicate.remove_duplicate_images(data["duplicateFilter"]["sourceDir"])

if data["lavisFilterAndCaption"]["enable"]:
    import filter_captionPhoto
    filter_captionPhoto.filterAndCaption(data["lavisFilterAndCaption"])

if data["watermarkFilter"]["enable"]:
    import watermarkFilter
    watermarkFilter.process_images(data["watermarkFilter"])