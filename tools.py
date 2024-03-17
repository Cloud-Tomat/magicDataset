import os

def createFolders(base_folder, target):
    folder = os.path.join(base_folder, target)


    # Create the duplicates folder if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)

    return folder