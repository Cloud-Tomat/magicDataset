import gradio as gr
from imageCrawler import imageCrawler  # Assuming this is the correct import for your image crawler
from PIL import Image
import re


# Function to start the image crawler in a separate thread and manage the global flag and output directory
def startCrawler(searchParams):


    yandex = imageCrawler(debug=searchParams["debug"])
    for search in searchParams["searchs"]:
        retry=0
        numImages=0
        while numImages==0 and retry<2:
            numImages=yandex.download(search[0], searchParams["targetDir"], searchParams["minResolution"], maxNumberImages=search[1])
            retry+=1

