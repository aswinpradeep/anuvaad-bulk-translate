from pdf2image import convert_from_path
from PIL import Image
#from PyPDF2 import PdfWriter, PdfReader
import glob
import img2pdf
from PIL import ImageFilter
import cv2
import numpy as np
import os
from skimage.color import rgb2gray
import traceback
from skimage.transform import hough_line, hough_line_peaks
from scipy.stats import mode

from skimage.transform import rotate
from skimage.feature import canny

class PDFModify():

    def get_white_content_ratio(self,image,calculate_drop,cutting_width):
        # Convert the image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Get the width and height of the image
        height, width = gray_image.shape
        
        # # Split the image into left and right halves
        # left_half = gray_image[:, :width // 2]
        # right_half = gray_image[:, width // 2:]
        # # Calculate the average pixel intensity for each half
        # left_avg_intensity = np.mean(left_half)
        # right_avg_intensity = np.mean(right_half)
        
        # if left_avg_intensity > right_avg_intensity:
            # Start from the left end and find where intensity drops by 50% or more
        if calculate_drop == "LEFT":
            # for i in range(0, width // 4, 2):
            # #print(np.mean(gray_image[:,i:i+5]))
            #     increased_blank = 0
            #     if(np.mean(gray_image[:,i:i+2]) <= 235):
            #         for j in range(i,width // 4, 2):
            #             if(np.mean(gray_image[:,j:j+2]) >=250):
            #                 increased_blank = 1
            #             if(increased_blank == 1 and np.mean(gray_image[:,j:j+2]) <=235):
            #                 left_drop_width = i
            #         if(increased_blank == 0):
            #             left_drop_width = i
            #         return "LEFT",left_drop_width
        
            left_drop_width = 0
            for i in range(0, width // 2, 2):
                if(np.mean(gray_image[:,i:i+2]) <= cutting_width):
                    left_drop_width = i
                    break
            blank_spot = None
            for i in range(left_drop_width, width // 2, 2):
                while(np.mean(gray_image[:,i:i+2])>=253):
                    blank_spot = i
                    i=i+2
                if blank_spot != None:
                    break
            if blank_spot!=None:
                for i in range(blank_spot, width // 2, 2):
                    if(np.mean(gray_image[:,i:i+2]) <= cutting_width):
                        left_drop_width = i
                        return "LEFT",left_drop_width
            if left_drop_width == None: 
                left_drop_width = 0
            return "LEFT",left_drop_width

        # else:
            # Start from the right end and find where intensity drops by 50% or more
        if calculate_drop == "RIGHT":
            right_drop_width = width
            for i in range(width, width-(width // 2), -2):
                if np.mean(gray_image[:,i-2:i]) <= cutting_width:
                    right_drop_width = i
                    break
            blank_spot = None
            for i in range(right_drop_width, width-(width // 2), -2):
                if(np.mean(gray_image[:,i-2:i])>=253):
                    blank_spot = i
                    break
            if blank_spot!=None:
                for i in range(blank_spot, width-(width // 2), -2):
                    if(np.mean(gray_image[:,i-2:i]) <= cutting_width):
                        right_drop_width = i
                        return "RIGHT",right_drop_width
            if right_drop_width == None: 
                right_drop_width = 0
            return "RIGHT",right_drop_width

    def skew_angle_hough_transform(self,image):
        # convert to edges
        edges = canny(image)
        # Classic straight-line Hough transform between 0.1 - 180 degrees.
        tested_angles = np.deg2rad(np.arange(0.1, 180.0))
        h, theta, d = hough_line(edges, theta=tested_angles)

        # find line peaks and angles
        accum, angles, dists = hough_line_peaks(h, theta, d)

        # round the angles to 2 decimal places and find the most common angle.
        most_common_angle = mode(np.around(angles, decimals=2))[0]

        # convert the angle to degree for rotation.
        skew_angle = np.rad2deg(most_common_angle - np.pi/2)
        return rotate(image, skew_angle, cval=1)

    def func(self,filename):
        filename = filename.replace("./temporary/cropped_page_","")
        filename = filename.replace(".jpg","")
        return int(filename)
        
    def pdf_modify(self,pdf_path):
        try:
            images = convert_from_path(pdf_path)

            # for i, image in enumerate(images):
            #     image.save(f'/home/test/Downloads/1-50/samples/1/page_{i + 1}.png', 'PNG')


            for i,image in enumerate(images):
                # Check if image_np is not empty

                image_np = np.array(image)
                if image_np.size == 0:
                    print(f"Skipping empty image {i + 1}")
                    continue
                print(np.shape(image_np))
                # image_np = rgb2gray(image_np)
                # image_np = self.skew_angle_hough_transform(image_np)
                direction, intensity_drop_width = self.get_white_content_ratio(image_np, "LEFT", 245)
                # if intensity_drop_width == None or intensity_drop_width == 0:
                #     direction, intensity_drop_width = self.get_white_content_ratio(image_np, "LEFT", 235)
                width, height = image.size
                print(width,height)
                #left = width // 5
                if intensity_drop_width>15:
                    left = intensity_drop_width - 15
                    cropped_image = image.crop((left, 0, width, height)) # if the image has the oppsite side cropping move this to else cropped_image
                else: 
                    cropped_image = image

                image_np = np.array(cropped_image)
                direction, intensity_drop_width = self.get_white_content_ratio(image_np, "RIGHT", 245)
                # if intensity_drop_width == None or intensity_drop_width == 0:
                #     direction, intensity_drop_width = self.get_white_content_ratio(image_np, "RIGHT", 235)
                width, height = cropped_image.size
                if intensity_drop_width!=None or intensity_drop_width!=0:
                    if intensity_drop_width<width-15:
                        right = intensity_drop_width + 15
                        cropped_image = cropped_image.crop((0, 0, right, height))  # if the image has the oppsite side cropping move this to else cropped_image
                    else:
                        right = width
                        cropped_image = cropped_image.crop((0, 0, right, height))  # if the image has the oppsite side cropping move this to else cropped_image
                else: 
                    cropped_image = image
                    
                cropped_image.save(f'./temporary/cropped_page_{i + 1}.jpg', 'JPEG')

            path = glob.glob('./temporary/*.jpg')
            for i in path:
                name = i.split('/')[-1]
                print(name)
            # Open the image
                im = Image.open(i)
                print(im)

            # # Apply the unsharp mask filter
                im = im.filter(ImageFilter.UnsharpMask(radius=7, percent=200, threshold=8))

            # # Save the sharpened image
                im.save("./temporary/"+name)


            # /home/test/Downloads/sind/binder/page14/img/bind_2001.pdf
            # /home/test/Downloads/sind/binder/page14/img/*.jpg
            pdf_path = pdf_path.replace(".pdf","_updated.pdf")
            with open(pdf_path,"wb") as f:
                f.write(img2pdf.convert(sorted(glob.glob("./temporary/*.jpg"),key=self.func)))
            try:
                files = glob.glob(os.path.join("./temporary/", '*'))
                for file in files:
                    if os.path.isfile(file):
                        os.remove(file)
                    print("All files deleted successfully.")
            except OSError:
                print("Error occurred while deleting files.")
        except Exception:
            print(traceback.format_exc())