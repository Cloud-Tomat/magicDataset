import os
import shutil
from PIL import Image
import imagehash
import tools  # Assuming this is a module you've defined for folder operations

def remove_duplicate_images(base_folder, hash_size=8, distance_threshold=5):
    hashes = {}
    duplicate_folder = tools.createFolders(base_folder, "duplicates")
    corrupted_folder = tools.createFolders(base_folder, "corrupted")

    for root, dirs, files in os.walk(base_folder):
        # Ignore the duplicates and corrupted directories themselves
        if root.startswith(duplicate_folder) or root.startswith(corrupted_folder):
            continue

        for filename in files:
            if filename.endswith('.jpg'):
                filepath = os.path.join(root, filename)
                print(f"Analyzing {filepath}")
                try:
                    with Image.open(filepath) as img:
                        # Compute the hash using perceptual hash with a specified hash_size
                        hash_val = imagehash.phash(img, hash_size=hash_size)
                        #hash_val = imagehash.crop_resistant_hash(img, min_segment_size=500, segmentation_image_size=1000)
                        #hash_val = imagehash.whash(img)
                        #hash_val = imagehash.dhash(img)
                except Exception as e:
                    print(f"Failed to process {filename}: {e}")
                    shutil.move(filepath, os.path.join(corrupted_folder, filename))
                    continue

                # Compare computed hash with existing hashes
                found_duplicate = False
                min=[1e6,None]
                for stored_hash in hashes.keys():
                    distance=hash_val - stored_hash
                    if distance<min[0]:
                        min[0]=distance
                        min[1]=hashes[stored_hash]
                    if distance <= distance_threshold:
                        print(f"Duplicate found: {filename} is a duplicate of {hashes[stored_hash]}. Moving {filename} to duplicates.")
                        duplicate_path = os.path.join(duplicate_folder, filename)
                        # Ensure a unique name for the duplicate in the destination folder
                        while os.path.exists(duplicate_path):
                            base, extension = os.path.splitext(duplicate_path)
                            duplicate_path = f"{base}_duplicate{extension}"
                        shutil.move(filepath, duplicate_path)
                        found_duplicate = True
                        break
                
                print(f"closest {min[1]} distance {min[0]}")

                if not found_duplicate:
                    # Store the relative path from base_folder to the image for more accurate identification
                    relative_path = os.path.relpath(filepath, base_folder)
                    hashes[hash_val] = relative_path

# Example usage
base_folder = 'path/to/your/images'
remove_duplicate_images(base_folder, hash_size=8, distance_threshold=5)
