import os
from PIL import Image
import numpy as np
import tools
import shutil
import face_recognition


def resize_image(image, max_dimension):
    original_width, original_height = image.size
    ratio = min(max_dimension / original_width, max_dimension / original_height)
    new_size = (int(original_width * ratio), int(original_height * ratio))
    resized_image = image.resize(new_size, Image.LANCZOS)
    return resized_image

def crop_borders(image, percentage_to_crop):
    width, height = image.size
    crop_value_width = int(width * (percentage_to_crop / 100))
    crop_value_height = int(height * (percentage_to_crop / 100))
    cropped_image = image.crop((crop_value_width, crop_value_height, width - crop_value_width, height - crop_value_height))
    return cropped_image

def processFaces(config, source_dir, corrupted_folder, border=100):
    corruptedFiles=[]
    
    percentageToFaceCrop = config['percentageToFaceCrop']
    min_crop_dimension = config['minCropDimension']

    # List to hold filenames, face sizes, and locations
    files_faces_locations = []
    # List of filenames to be modified
    modified_files = []

    # Function to resize image for faster face detection
    def resize_image_for_detection(image):
        max_dimension = 756
        original_size = image.size
        max_original_dimension = max(original_size)
        scale = max_dimension / max_original_dimension if max_original_dimension > max_dimension else 1
        if scale < 1:  # Only resize if necessary
            new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
            resized_image = image.resize(new_size, Image.LANCZOS)
            return resized_image, scale
        return image, scale

    # Scan directory for JPEG images
    for filename in os.listdir(source_dir):
        print("processing faces, file ",filename)
        if filename.lower().endswith('.jpg'):

            image_path = os.path.join(source_dir, filename)
            try:
                with Image.open(image_path) as img:
                    resized_image, scale = resize_image_for_detection(img)
                    image_array = np.array(resized_image)
                    face_locations = face_recognition.face_locations(image_array,model="large")

                    if face_locations:
                        # Calculate face areas on the resized image
                        face_areas = [(bottom - top) * (right - left) for top, right, bottom, left in face_locations]
                        largest_area_index = face_areas.index(max(face_areas))
                        largest_face_area = face_areas[largest_area_index] / (scale ** 2)  # Adjust to original image size
                        largest_face_location = face_locations[largest_area_index]
                        # Adjust face location to original image size
                        adjusted_location = tuple(int(coord / scale) for coord in largest_face_location)
                        files_faces_locations.append((filename, largest_face_area, adjusted_location))
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
                shutil.move(image_path, os.path.join(corrupted_folder, filename))
                corruptedFiles.append(filename)
                continue 


    # Sort by face area
    files_faces_locations.sort(key=lambda x: x[1], reverse=True)

    # Select top x%
    num_files_to_modify = int(len(files_faces_locations) * (percentageToFaceCrop / 100))
    selected_files = files_faces_locations[:num_files_to_modify]

    # Process selected images
    for filename, _, face_location in selected_files:
        if filename in corruptedFiles:
            continue
        image_path = os.path.join(source_dir, filename)
        with Image.open(image_path) as img:
            original_height, original_width = img.size
            top, right, bottom, left = face_location

            # Apply border, ensuring within image bounds
            borderX=0.3*(right-left)
            borderY=0.3*(bottom-top)
            top, bottom = max(top - borderY, 0), min(bottom + borderY, original_height)
            left, right = max(left - borderX, 0), min(right + borderX, original_width)

            # Ensure minimum crop dimensions, adjusting if necessary
            width, height = right - left, bottom - top
            if width < min_crop_dimension:
                extra = (min_crop_dimension - width) // 2
                left, right = max(left - extra, 0), min(right + extra, original_width)
            if height < min_crop_dimension:
                extra = (min_crop_dimension - height) // 2
                top, bottom = max(top - extra, 0), min(bottom + extra, original_height)

            # Adjust for over-expansion
            left, right = max(left, 0), min(right, original_width)
            top, bottom = max(top, 0), min(bottom, original_height)

            # Crop and save the image
            cropped_image = img.crop((left, top, right, bottom))
            cropped_image.save(image_path)
            modified_files.append(filename)

    return modified_files




def process_images(config):
    corrupted_folder = tools.createFolders(config['sourceDir'], "corrupted")
    source_dir = config['sourceDir']
    crop_percentage = config['faceCrop']['percentageToFaceCrop']
    max_dimension = config['resize']['maxDimension']
    percentage_to_crop = config['cropBorders']['percentageToCrop']


    facesImg=processFaces(config["faceCrop"],source_dir,corrupted_folder)


    for filename in os.listdir(source_dir):
        print("processing ",filename)
        if filename.endswith(('.jpg')):
            file_path = os.path.join(source_dir, filename)
            try:
                # Open the image
                img = Image.open(file_path)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
                shutil.move(file_path, os.path.join(corrupted_folder, filename))
                continue 
            

            if not filename in facesImg:
                if config['cropBorders']['enable']:
                    img = crop_borders(img, percentage_to_crop)

            if config['resize']['enable']:
                img = resize_image(img, max_dimension)

    
            
            img.save(file_path)  # Overwrite the original image

