
import os
from PIL import Image
import shutil
from qna import qnaClass
import json
import re
import tools
from tqdm import tqdm
import logger

def discard (filepath,targetDir):
    subdir, filename = os.path.split(filepath)
    shutil.move(filepath, os.path.join(targetDir, filename))






def process_image(qna, filepath, qa_pairs, discardedDir):

    infos = []  # List to hold the info for each QA pair that leads to discarding
    for qa in qa_pairs:
        question = qa['question']
        expected_answers = [answer.casefold() for answer in qa['expectedAnswers']]  # Convert all expected answers to lowercase
        actual_answer = qna.shortAnswer(question).casefold()
        info = f"Question: {question}\nGiven Answer: {actual_answer}\nExpected Answer: {', '.join(expected_answers)}"
        infos.append(info)
        # Check if the actual answer matches any of the expected answers
        if actual_answer not in expected_answers:

            # Create and write to the .txt file when discarding
            base_name = os.path.splitext(os.path.basename(filepath))[0]
            txt_filename = f"{base_name}_info.txt"
            txt_filepath = os.path.join(discardedDir, txt_filename)
            with open(txt_filepath, 'w') as txt_file:
                txt_file.write(info + "\n")
            print(f"Moved {os.path.split(filepath)[1]} to discarded due to incorrect answer.")
            # Move the image file
            discard(filepath, discardedDir)  # Assuming this function moves the file to discardedDir
            return False  # Assuming one incorrect answer is enough to discard the file

    return True



def generate_caption(qna,filepath, template):
   
    # Initialize the caption with the template
    caption = template
    
    # Regular expression to find placeholders in the template
    placeholders = re.findall(r'\{(.*?)\}', template)
    
    for placeholder in placeholders:
        question, minLength, maxLength = placeholder.split(',')
        maxLength = int(maxLength)  # Convert maxLength to an integer
        minLength = int(minLength)  # Convert minLength to an integer
        answer = qna.shortAnswer(question.strip(), minLen=minLength+1,maxLen=maxLength+1)  # Get the answer from qnaClass
        caption = caption.replace(f"{{{placeholder}}}", answer, 1)  # Replace one placeholder at a time
    
    # Save the processed caption
    base_name = os.path.splitext(filepath)[0]  # Get the base name of the file
    caption_filepath = f"{base_name}.txt"
    
    with open(caption_filepath, 'w') as caption_file:
        caption_file.write(caption)
    print(f"Caption saved to {caption_filepath}")


def filterAndCaption(params):

    base_folder=params["sourceDir"]
    excluded_folder = tools.createFolders(base_folder, "excluded")
    corrupted_folder = tools.createFolders(base_folder, "corrupted")

    qna=qnaClass()

    files=os.listdir(base_folder)
    removed=0
    captionned=0
    for filename in tqdm(files,desc="captionning and QA filter"):

        print("processing ",filename)
        file_path = os.path.join(base_folder, filename)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue

        if not filename.endswith('.jpg') and  not filename.endswith('.png'):
            continue

        print(f"Processing {file_path}")
        try:
            raw_image = Image.open(file_path).convert('RGB')
        except:
            discard(file_path,corrupted_folder)
            print(f"Moved {filename} to discarded due to corrupted file.")
            continue

        raw_image=raw_image.resize((512, 512), Image.LANCZOS)

        
        qna.loadImage(raw_image)                
        if process_image(qna,file_path,params["questions"],excluded_folder):
            captionned+=1
            generate_caption(qna,file_path,params["caption"])
        else:
            removed+=1
    logger.console(f"Captionned {captionned} files")
    logger.console(f"Moved {removed} files to {excluded_folder} folder")