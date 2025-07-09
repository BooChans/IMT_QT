# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 13:44:30 2024 under Python 3.11.7

@author: f24lerou
"""

# 8<----------------------------------------- Import modules -----------------------------------

import numpy as np

from ifmta.image_processing import Binning, ReverseBinning, Crop

def PropagatePhaseScreen(phaseScreen, *, 
                         object_pp=None, image_pp=None, wavelength=None, propagation_distance=None,
                         image_length=None):
    """
    PropagatePhaseScreen : Fraunhoffer propagation from phase screen
    
    Author : Francois Leroux
    Contact : francois.leroux.pro@gmail.com
    Status : in progress
    Last update : 2024.04.12, Brest
    Comments :
      
    Inputs : MANDATORY : phaseScreen {np.array 2D} : the phase screen
    
             OPTIONAL : wavelength [m]
                        propagation_distance
                        image_pp
                        
    Outputs : image plane irradiance
    """
    
    object_field = np.exp(1j*phaseScreen)
    
    if image_pp == None:
        image = np.abs(np.fft.fftshift(np.fft.fft2(object_field)))**2
        if image_length == None:
            return image
        
    else:    
        object_length = wavelength * propagation_distance / image_pp
        object_size = object_length//object_pp
        object_field = np.pad(object_field, (0,int(object_size-object_field.shape[0])))
        image_pp = wavelength * propagation_distance / (object_field.shape[0]*object_pp)
        image = np.abs(np.fft.fftshift(np.fft.fft2(object_field)))**2
        
        if image_length == None:
            return image, image_pp
        
        else:
            image_size = int(image_length//image_pp + 1)
            image = Crop(image, image_size), image_pp
            
            return image
            
def PropagateComplexAmplitudeScreen(object_field, *, zero_padding_factor=None,
                                    object_pp=None, image_pp=None, wavelength=None, propagation_distance=None,
                                    image_length=None):
    """
    PropagateComplexAmplitudeScreen : Fraunhoffer propagation from complex amplitude screen
    
    Author : Francois Leroux
    Contact : francois.leroux.pro@gmail.com
    Status : in progress
    Last update : 2024.04.12, Brest
    Comments :
      
    Inputs : MANDATORY : complexAmplitudeScreen {np.array 2D} : the complex amplitude screen
                        
    Outputs : image plane irradiance
    """
    
    if image_pp == None and zero_padding_factor == None:
        print("We here bro, None x2 checked")
        image = np.abs(np.fft.fftshift(np.fft.fft2(object_field)))**2
        
        if image_length == None:
            print("okay we're here bro")
            return image
        else:
            image_size = int(image_length//image_pp + 1)
            image = Crop(image, image_size)
            return image
        
    elif image_pp == None and zero_padding_factor != None:
        object_field_padded = np.pad(object_field, (0, (zero_padding_factor-1)*np.max(object_field.shape)))
        image = np.abs(np.fft.fftshift(np.fft.fft2(object_field_padded)))**2
        
        if image_length == None:
            return image
        else:
            image_size = int(image_length//image_pp + 1)
            image = Crop(image, image_size)
            return image
        
    elif image_pp != None and zero_padding_factor == None:
        
        image_pp_original = wavelength * propagation_distance / (object_field.shape[0] * object_pp)
        
        if image_pp_original > image_pp :
            object_length = wavelength * propagation_distance / image_pp
            object_size = object_length//object_pp
            object_field = np.pad(object_field, (0,int(object_size-object_field.shape[0])))
            image_pp = wavelength * propagation_distance / (object_field.shape[0]*object_pp)
            image = np.abs(np.fft.fftshift(np.fft.fft2(object_field)))**2
            
            if image_length == None:
                return image
            else:
                image_size = int(image_length//image_pp + 1)
                image = Crop(image, image_size)
                return image
            
        else:
            print("WARNING : no zero padding needed to achieve image_pp requierement")
            image = np.abs(np.fft.fftshift(np.fft.fft2(object_field)))**2
            n = int(image_pp//image_pp_original)
            new_size_0 = int(image.shape[0] - image.shape[0]%n)
            new_size_1 = int(image.shape[1] - image.shape[1]%n)
            #image = image[:new_size_0, :new_size_1]
            #image = Binning(image, (n * image//n, n * image//n))
        
            if image_length == None:
                return image
            else:
                image_size = int(image_length//image_pp + 1)
                image = Crop(image, image_size)
                return image
        
    else:
        raise TypeError("Image_pp and zero_padding_factor can not be set at the same time")