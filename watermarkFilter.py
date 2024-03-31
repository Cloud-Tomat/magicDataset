from PIL import Image
import easyocr
import os
import shutil
import tools  # Assuming this is a helper module you've created
import numpy as np
from tqdm import tqdm
import logger
reader = easyocr.Reader(['en'])  # 'en' for English

def detect_text(image_path, cropSizePercent,corrupted_folder):
    """
    Use EasyOCR to detect text in a center-cropped area of the image.
    """

    try:
        # Open the image
        img = Image.open(image_path)
    except Exception as e:
        filename=os.path.basename(image_path)
        print(f"Failed to process {filename}: {e}")
        shutil.move(image_path, os.path.join(corrupted_folder, filename))
        return 



    # Calculate the crop size
    width, height = img.size
    crop_width = width * cropSizePercent // 100
    crop_height = height * cropSizePercent // 100
    left = (width - crop_width) // 2
    top = (height - crop_height) // 2
    right = (width + crop_width) // 2
    bottom = (height + crop_height) // 2

 

    # Perform the crop
    img_cropped = img.crop((left, top, right, bottom))
    
    img_cropped=img_cropped.resize((512, 512), Image.LANCZOS)
    
    # Use EasyOCR to detect text in the cropped image
    result = reader.readtext(np.array(img_cropped))
    return not len(result) == 0

def process_images(params):
    base_folder = params["sourceDir"]
    cropSizePercent = params["searchCropPercent"]
    excluded_folder = tools.createFolders(base_folder, "watermarked")
    corrupted_folder = tools.createFolders(base_folder, "corrupted")

    # Iterate through all files in the directory
    files=os.listdir(base_folder)
    removed=0
    for filename in tqdm(files,"detecting watermark"):
        print("processing ", filename)
        # Construct the full file path
        file_path = os.path.join(base_folder, filename)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue
        
        if not filename.endswith('.jpg') and not filename.endswith("png"):
            continue




        # Detect if the image has text, using the specified crop size percent
        has_text = detect_text(file_path, cropSizePercent, corrupted_folder)



        # Move the file to the appropriate subdirectory if text is detected
        if has_text:
            print(f"Text detected in {filename}, moving to 'watermarked' folder.")
            shutil.move(file_path, os.path.join(excluded_folder, filename))
            removed+=1
    logger.console(f"Moved {removed} files to f{excluded_folder} folder")
