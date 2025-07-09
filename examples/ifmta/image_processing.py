# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 13:55:37 2024 Under Python 3.11.7

@author: f24lerou
"""

#%% 8<------------------------------------ Import functions  ----------------------------------

import matplotlib.pyplot as plt
import numpy as np

#%%

def IsSaturated(full_path, *, saturation=1):
    """
    IsSaturated : tells wether an image is saturated or not
    
    Author : Francois Leroux
    Contact : francois.leroux.pro@gmail.com
    Status : in progress
    Last update : 2024.03.05, Brest
    Comments :
      
    Inputs : MANDATORY : full_path {str} : the image address
    
             OPTIONNAL : saturation : the value at which the image saturate
    """
    
    img = plt.imread(full_path) # between 0 and 1 for .png images
    if img.max() >= saturation:
        return True
    else:
        return False, img.max()
    

def Crop(img, new_size, *, center = [0,0]):
    """
    Crop : crop an image
    
    Author : Francois Leroux
    Contact : francois.leroux.pro@gmail.com
    Status : in progress
    Last update : 2024.03.05, Brest
    Comments :
      
    Inputs : MANDATORY : img {np.array 2D} : the image to crop
                         new_size {int}[px] : the dimension of the cropped image 
                                              (the cropped image will be a new_size by new_size array)
    """
    
    img_cropped = img[center[0]+img.shape[0]//2-new_size//2:center[0]+img.shape[0]//2+new_size//2,
                      center[1]+img.shape[1]//2-new_size//2:center[1]+img.shape[1]//2+new_size//2]
    
    return img_cropped

def ReverseBinning(image, n):
    
    """
    ReverseBinning : replace one pixel of image by a square of n by n pixels
                     in order to compute a larger area in the Fourrier domain 
                     with np.fft
    
    Author : Francois Leroux, Chat GPT was used.
    Contact : francois.leroux.pro@gmail.com
    Status : in progress
    Last update : 2024.03.05, Brest
    Comments : Peut servir à augmenter la taille 
      
    Inputs : MANDATORY : image {np.array 2D} : the image to reverse bin
                         n {int} [px]: the length size of one pixel of thr original image in the new image
                        
    Outputs : array_zeros_padded : the array zeros padded
    """

    return np.kron(image, np.ones((n, n)))

def Binning(image, new_shape):
    
    """
    Binning : image binning
    
    Author : https://scipython.com/blog/binning-a-2d-imageay-in-numpy/
    Contact : francois.leroux.pro@gmail.com
    Status : in progress
    Last update : 2024.04.03, Brest
    Comments : Can be used to 
      
    Inputs : MANDATORY : image {np.imageay 2D} : the image to bin
                         new_shape {2 by 1 tupple} [px]: the new shape. Must be a divider of image.shape
                        
    Outputs : The binned image
    """
    
    shape = (new_shape[0], image.shape[0] // new_shape[0],
             new_shape[1], image.shape[1] // new_shape[1])
    return image.reshape(shape).mean(-1).mean(1)