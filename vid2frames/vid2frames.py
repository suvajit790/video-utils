
# Importing all necessary libraries
import cv2
import os
import argparse

def vid2frames(source, destination, img_format):
    # Read the video from specified path
    cam = cv2.VideoCapture(source)
    
    try:
        # creating a folder named data
        if not os.path.exists(destination):
            os.makedirs(destination)
    
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
            name = os.path.join(destination, str(currentframe) + '.' + img_format)
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

# Initialize the Parser
parser = argparse.ArgumentParser(description ='Video to frames generator')
  
# Adding Arguments
parser.add_argument('-s', '--source',
                    type = str,
                    required = True,
                    help ='Path to video')

parser.add_argument('-d','--destination',
                    type = str,
                    required = True,
                    help ='Path to save dir')

parser.add_argument('-imgf','--image_format',
                    type = str,
                    required = False,
                    default = 'png',
                    choices = ['jpg', 'png', 'gif', 'tif'],
                    help ='Path to save dir')
  
args = parser.parse_args()


vid2frames(source=args.source, destination=args.destination, img_format=args.image_format)