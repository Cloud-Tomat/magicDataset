import os
import torch
from PIL import Image
import requests
from lavis.models import load_model_and_preprocess,model_zoo


class qnaClass():
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else 'cpu')
        print(self.device)
        print(torch.cuda.get_device_name())
        self.image=None
        self.model, self.vis_processors, self.txt_processors = load_model_and_preprocess(name="blip_vqa", model_type="vqav2", is_eval=True, device=self.device)

    def loadImage(self,raw_image):
        self.image = self.vis_processors["eval"](raw_image).unsqueeze(0).to(self.device)


    def shortAnswer(self,question,minLen=2,maxLen=2):
        questionProcessed = self.txt_processors["eval"](question)
        return self.model.predict_answers(
            samples={
                "image": self.image, 
                "text_input": questionProcessed}, 
            inference_method="generate",
            num_beams=3,
            min_len=minLen,
            max_len=maxLen)[0]
        


