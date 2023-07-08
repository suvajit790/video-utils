
# Importing all necessary libraries
import cv2
import os
import argparse

# Initialize the Parser
parser = argparse.ArgumentParser(description ='Video to frames generator')
  
# Adding Arguments
parser.add_argument('-s', '--source',
                    type = string,
                    required = True,
                    help ='Path to video')

parser.add_argument('-d','--destination',
                    type = string,
                    required = True,
                    help ='Path to save dir')

parser.add_argument('-imgf','--image_format',
                    type = string,
                    required = False,
                    default = 'png',
                    choices = ['jpg', 'png', 'gif', 'tif']
                    help ='Path to save dir')
  
args = parser.parse_args()
  
# Read the video from specified path
cam = cv2.VideoCapture(args.source)
  
try:
    # creating a folder named data
    if not os.path.exists(args.destination):
        os.makedirs(args.destination)
  
# if not created then raise error
except OSError:
    print ('Error: Creating directory of data')
  
# frame
currentframe = 0
  
while(True):
    # reading from frame
    ret,frame = cam.read()
  
    if ret:
        # if video is still left continue creating images
        name = os.path.join(args.destination, str(currentframe) + '.' + args.image_format)
        print ('Creating...' + name)
  
        # writing the extracted images
        cv2.imwrite(name, frame)
  
        # increasing counter so that it will
        # show how many frames are created
        currentframe += 1
    else:
        break
  
# Release all space and windows once done
cam.release()
