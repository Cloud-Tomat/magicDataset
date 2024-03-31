import os
from PIL import Image,ImageDraw
import numpy as np
import tools
import shutil
import face_recognition
from tqdm import tqdm
import logger

def locate_and_expand_face(pil_image, expand_percentage=0):
    """
    Locates a face in a PIL image and optionally expands the detection box.
    Tries a 90° rotation if no face is detected, but returns coordinates for the original orientation.
    
    Parameters:
    - pil_image: Input PIL image.
    - expand_percentage: How much to expand the detection box by (percentage).
    
    Returns:
    - The coordinates of the (optionally expanded) face box in the original image's orientation.
    """
    def detect_faces(image_array):
        # Attempt to detect faces in the given image array
        return face_recognition.face_locations(image_array, model="large")

    def adjust_box_for_rotation(box, rotation_degree):
        """
        Adjusts the coordinates of the detected face box for the original image's orientation
        after a 90-degree rotation was used for detection.
        
        Parameters:
        - box: The detected face box coordinates as (top, right, bottom, left).
        - rotation_degree: The degree of rotation applied to the image for face detection.
        
        Returns:
        - Adjusted face box coordinates in the orientation of the original image.
        """
        left, top, right, bottom = box
        if rotation_degree == 0:
            return box
        elif  rotation_degree== 90:
            newLeft=min(pil_image.width-top,pil_image.width-bottom)
            newRight=max(pil_image.width-top,pil_image.width-bottom)
            newTop=min(pil_image.height - right,pil_image.height - left)
            newBottom=max(pil_image.height - right,pil_image.height - left)
            return [newLeft,newTop,newRight,newBottom]
        elif rotation_degree==-90:
            newLeft=top
            newRight=bottom
            newTop=min(pil_image.height - right,pil_image.height - left)
            newBottom=max(pil_image.height - right,pil_image.height - left)  
            return [newLeft,newTop,newRight,newBottom]
        return box

    original_image = np.array(pil_image)
    scale = min(512 / pil_image.width, 512 / pil_image.height)
    resized_image = pil_image.resize((int(pil_image.width * scale), int(pil_image.height * scale)))
    resized_image_array = np.array(resized_image)

    face_locations = detect_faces(resized_image_array)

    rotation_degree = 0
    if not face_locations:
        # Rotate the image by 90° and try again
        rotated_resized_image = resized_image.rotate(90, expand=True)
        rotated_resized_image_array = np.array(rotated_resized_image)
        face_locations = detect_faces(rotated_resized_image_array)
        rotation_degree=90
        if not face_locations:
            rotated_resized_image = resized_image.rotate(-90, expand=True)
            rotated_resized_image_array = np.array(rotated_resized_image)
            face_locations = detect_faces(rotated_resized_image_array)
            rotation_degree = -90 

    if not face_locations:
        return [],0

    top, right, bottom, left = face_locations[0]
    original_box = [left / scale, top / scale, right / scale, bottom / scale]

    if rotation_degree != 90:
        original_box = adjust_box_for_rotation(original_box, rotation_degree)

    # Expand the box
    width_expand = (original_box[2] - original_box[0]) * expand_percentage / 100
    height_expand = (original_box[3] - original_box[1]) * expand_percentage / 100

    expanded_box = [
        max(0, original_box[0] - width_expand),
        max(0, original_box[1] - height_expand),
        min(pil_image.width, original_box[2] + width_expand),
        min(pil_image.height, original_box[3] + height_expand)
    ]

    return expanded_box,len(face_locations)


def save_image_box(pil_image, face_box, save_path):
    """
    Draws a rectangle around the face and saves the image.
    
    Parameters:
    - pil_image: PIL Image object of the original image.
    - face_box: The coordinates of the face box as a tuple (left, top, right, bottom).
    - save_path: Path where the modified image will be saved.
    """
    # Create a drawing context
    face=pil_image.copy()
    draw = ImageDraw.Draw(face)
    
    # Draw the rectangle around the face
    # Note: The 'outline' parameter color and width can be changed as needed
    if face_box:
        draw.rectangle(face_box, outline="red", width=3)
    
    # Save the image with the rectangle
    face.save(save_path)

def crop_resize(pil_image, target_size, face_box):
    """
    Crops the PIL image to the given aspect ratio, ensuring the face box is included.
    
    Parameters:
    - pil_image: The original PIL Image object.
    - target_size: Tuple (target_width, target_height) indicating the desired aspect ratio.
    - face_box: The coordinates of the face box as a tuple (left, top, right, bottom).
    
    Returns:
    - Cropped PIL image.
    """
    original_width, original_height = pil_image.size
    target_width, target_height = target_size
    
    # Calculate the target aspect ratio and the original aspect ratio
    target_aspect = target_width / target_height
    original_aspect = original_width / original_height
    
    # Calculate the dimensions of the maximum possible crop that respects the target aspect ratio
    if target_aspect > original_aspect:
        # Width is the limiting factor
        crop_width = original_width
        crop_height = int(crop_width / target_aspect)
    else:
        # Height is the limiting factor
        crop_height = original_height
        crop_width = int(crop_height * target_aspect)
    
    # Determine the initial centered crop box
    left = (original_width - crop_width) / 2
    top = (original_height - crop_height) / 2
    right = left + crop_width
    bottom = top + crop_height
    
    if face_box:
        # Adjust the crop box to ensure it includes the face box, if possible
        face_left, face_top, face_right, face_bottom = face_box
        
        # Check if face box is wider or taller than the crop area and adjust
        if face_right - face_left > crop_width:
            # Face box is wider than the crop area
            # Center the crop around the face box horizontally
            center_x = (face_left + face_right) / 2
            left = max(0, center_x - crop_width / 2)
            right = left + crop_width
        elif face_bottom - face_top > crop_height:
            # Face box is taller than the crop area
            # Center the crop around the face box vertically
            center_y = (face_top + face_bottom) / 2
            top = max(0, center_y - crop_height / 2)
            bottom = top + crop_height
        else:
            # Adjust horizontally if needed
            if face_left < left:
                left -= min(left - face_left, left)
                right = left + crop_width
            elif face_right > right:
                right += min(face_right - right, original_width - right)
                left = right - crop_width
                
            # Adjust vertically if needed
            if face_top < top:
                top -= min(top - face_top, top)
                bottom = top + crop_height
            elif face_bottom > bottom:
                bottom += min(face_bottom - bottom, original_height - bottom)
                top = bottom - crop_height
    
    # Perform the crop
    cropped_image = pil_image.crop((int(left), int(top), int(right), int(bottom)))
    
    return cropped_image.resize(target_size,resample=Image.LANCZOS)

def discard (filepath,targetDir):
    subdir, filename = os.path.split(filepath)
    shutil.move(filepath, os.path.join(targetDir, filename))

def process_images(config):
    corrupted_folder = tools.createFolders(config['sourceDir'], "corrupted")
    source_dir = config['sourceDir']
    dimension = config['resize']['dimension']
    eliminateMutliFaces=config["filter"]["eliminateMutliFaces"]
    eliminateNoiFace=config["filter"]["eliminateNoiFace"]
    #percentage_to_crop = config['cropBorders']['percentageToCrop']

    excluded_folder = tools.createFolders(source_dir, "wrongNumberOfFaces")
    corrupted_folder = tools.createFolders(source_dir, "corrupted")

    files=os.listdir(source_dir)

    rejected=0
    processed=0
    for filename in tqdm(files,desc="crop&resize"):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(source_dir, filename)
            try:
                pil_image = Image.open(image_path)
                face_box,numFaces = locate_and_expand_face(pil_image, 30)
                if numFaces==0 and eliminateNoiFace:
                    discard(image_path,excluded_folder)
                    rejected+=1
                elif numFaces>1 and eliminateMutliFaces:
                    discard(image_path,excluded_folder)
                    rejected+=1
                else:
                    processed+=1
                    cropped_and_resized_image = crop_resize(pil_image, dimension, face_box)
                    cropped_and_resized_image.save(image_path)  # Overwrite the original image
                    print(f"Processed and saved {filename}")
            except Exception as e:
                discard(image_path,corrupted_folder)
                print(f"Error processing {filename}: {e}")

    logger.console(f"Moved {rejected} files to {excluded_folder} folder")
    logger.console(f"Processed {processed} files")


# Example usage
if __name__ == "__main__":
    directory="C:\\Users\\Nicolas\\sandbox\\nsfw_image\\training\\ella\\working_images\\real_images_captionned"

    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(directory, filename)
            try:
                pil_image = Image.open(image_path)
                face_box = locate_and_expand_face(pil_image, 30)
                cropped_and_resized_image = crop_resize(pil_image, (512,512), face_box)
                cropped_and_resized_image.save(image_path)  # Overwrite the original image
                print(f"Processed and saved {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")


