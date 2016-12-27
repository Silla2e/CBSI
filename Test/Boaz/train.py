import os
import cv2
import numpy as np
from PIL import Image

recognizer = cv2.f
path = 'dataStore'

def getImagesWithName(path):
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)]
    print imagePaths,

getImagesWithName(path)