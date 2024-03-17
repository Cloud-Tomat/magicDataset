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
    # Process selected images
    for filename, _, face_location in selected_files:
        if filename in corruptedFiles:
            continue
        image_path = os.path.join(source_dir, filename)
        with Image.open(image_path) as img:
            original_width, original_height = img.size
            top, right, bottom, left = face_location

            # Calculate initial crop dimensions with added border
            borderX = 0.3 * (right - left)
            borderY = 0.3 * (bottom - top)
            left = max(left - borderX, 0)
            right = min(right + borderX, original_width)
            top = max(top - borderY, 0)
            bottom = min(bottom + borderY, original_height)

            # Calculate the actual width and height after adding the border
            width = right - left
            height = bottom - top

            # Ensure minimum crop dimensions
            if width < min_crop_dimension:
                shortfall = min_crop_dimension - width
                # Adjust left and right, ensuring not to exceed the image bounds
                left = max(left - shortfall / 2, 0)
                right = min(right + shortfall / 2, original_width)
                if right - left < min_crop_dimension:  # Check if adjustments were not enough
                    if left == 0:  # If left is at bound, extend right as much as possible
                        right = min_crop_dimension
                    if right == original_width:  # If right is at bound, extend left as much as possible
                        left = original_width - min_crop_dimension

            if height < min_crop_dimension:
                shortfall = min_crop_dimension - height
                # Adjust top and bottom, ensuring not to exceed the image bounds
                top = max(top - shortfall / 2, 0)
                bottom = min(bottom + shortfall / 2, original_height)
                if bottom - top < min_crop_dimension:  # Check if adjustments were not enough
                    if top == 0:  # If top is at bound, extend bottom as much as possible
                        bottom = min_crop_dimension
                    if bottom == original_height:  # If bottom is at bound, extend top as much as possible
                        top = original_height - min_crop_dimension

            # Final cropping operation
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

