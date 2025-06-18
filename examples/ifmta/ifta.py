 # -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 09:58:42 2024 under Python 3.11.7

@author: f24lerou
"""

# 8<--------------------------- Import modules ---------------------------

import numpy as np

from ifmta.tools import Discretization, SoftDiscretization
from ifmta.performance_criterias import ComputeEfficiency, ComputeUniformity

# 8<------------------------- Functions definitions ----------------------



def Ifta(target, *, image_size=None, n_iter=25, rfact=1.2, n_levels=0, compute_efficiency=0, compute_uniformity=0, seed=0):

    """
    Ifta : Iterative Fourier Transform Algorithm
    
    Author : Francois Leroux
    Contact : francois.leroux.pro@gmail.com
    Status : in progress
    Last update : 2024.03.01, Brest
    Comments : for even support size, coordinates are defined like [-2,-1,0,1] (N = 4)
    
    Inputs : MANDATORY : target {2D float np.array}[Irradiance] : image we want to get at infinity under plane wave illumination  
                         image_size {tupple (1x2)}[pixel] : size of the image plane 
                                                            should have larger elements than target_image.shape 
                                                            is equal to holo_size
    
              OPTIONAL :  n_iter : number of iterations of each loop of the algorithm {int} - default value = 25
                          r_fact : reinforcment factor. Forces the energy to stay in the ROI - default value = 1.2
                          n_levels : number of levels over which the phase will be discretized 
                                    default value = 0 : no Discretization
                          compute_efficiency {bool} : If 1, efficiency is computed and returned along the loop
                                                      default value = 0
                          compute_uniformity {bool} : If 1, uniformity is computed and returned along the loop
                                                      default value = 0
                        
    Outputs : a binary cross
    """
    
    if compute_efficiency:
        efficiency = np.zeros(n_iter)             # memory allocation
        
    if compute_uniformity:
        uniformity = np.zeros(n_iter)             # memory allocation
    
    target_size = target.shape
    
    target_amp = np.asarray(target, float)       # conversion target to float
    target_amp = np.sqrt(target_amp)             # get target amplitude
    
    if image_size == None:
        image_amp = target_amp
        image_size = image_amp.shape
        
    else:
        image_amp = np.zeros(image_size)             # Amplitude output field = 0
        image_amp[image_size[0]//2-target_size[0]//2:image_size[0]//2-target_size[0]//2+target_size[0], 
                  image_size[1]//2-target_size[1]//2:image_size[1]//2-
                  target_size[1]//2+target_size[1]] = target_amp   # Amplitude = target image in window
    
    
    if type(seed) == int:
        image_phase = 2*np.pi*np.random.rand(image_size[0], image_size[1]) # Random image phase
    else:
        image_phase = seed
                                               
    image_field = image_amp*np.exp(1j * image_phase)      # Initiate input field
    
    # First loop - continous phase screen computation
    
    for k in range(n_iter):
        holo_field = np.fft.ifft2(np.fft.ifftshift(image_field))  # field ifta = TF-1 field image
        holo_phase = np.angle(holo_field)                         # save ifta phase
        holo_field = np.exp(holo_phase * 1j)                      # force the module of holo_field to 1 (no losses)
        image_field = np.fft.fftshift(np.fft.fft2(holo_field))    # field image = TF field ifta
        image_phase = np.angle(image_field)                       # save image phase
        image_amp[image_size[0]//2-target_size[0]//2:image_size[0]//2-target_size[0]//2+target_size[0], 
                  image_size[1]//2-target_size[1]//2:
                      image_size[1]//2-
                      target_size[1]//2+target_size[1]] = rfact*target_amp  # force the amplitude of the ifta 
                                                                            # to the target amplitude inside the ROI. 
                                                                            # amplitude freedom : outside the ROI,
                                                                            # the amplitude is free.
        image_field = image_amp*np.exp(image_phase * 1j)                    # new image field computation
        
        if n_levels ==0 and compute_efficiency:
            efficiency[k] = ComputeEfficiency(holo_phase, image_amp)
            
        if n_levels ==0 and compute_uniformity:
            uniformity[k] = ComputeUniformity(holo_phase, image_amp)

    # Second loop - discretized phase screen

    if n_levels != 0:

        for k in range(n_iter):
            holo_field = np.fft.ifft2(np.fft.ifftshift(image_field))  # field ifta = TF-1 field image
            holo_phase = np.angle(holo_field)                         # get ifta phase. phase values between 0 and 2pi 
            holo_phase = Discretization(holo_phase, n_levels)         # phase Discretization
            holo_field = np.exp(holo_phase * 1j)                      # force the amplitude of the ifta to 1 (no losses)
            image_field = np.fft.fftshift(np.fft.fft2(holo_field))    # image = TF du ifta
            image_phase = np.angle(image_field)                       # save image phase
            image_amp[image_size[0]//2-target_size[0]//2:
                      image_size[0]//2-target_size[0]//2+target_size[0], 
                      image_size[1]//2-target_size[1]//2:image_size[1]//2-target_size[1]//2+
                      target_size[1]] = rfact*target_amp               # force the amplitude of the ifta to the target amplitude 
                                                                       # inside the ROI. Outside the ROI, the amplitude is free
            image_field = image_amp*np.exp(image_phase * 1j)           # new image field computation
            
            if compute_efficiency:
                efficiency[k] = ComputeEfficiency(holo_phase, image_amp)
                
            if compute_uniformity:
                uniformity[k] = ComputeUniformity(holo_phase, image_amp)

    if compute_efficiency and not(compute_uniformity):
        return holo_phase, efficiency
    
    if compute_uniformity and not(compute_efficiency):
        return holo_phase, uniformity
    
    if compute_efficiency and compute_uniformity:
        return holo_phase, efficiency, uniformity

    return holo_phase



def IftaPhaseSoftQuantization(target, image_size, *, n_iter = 25, rfact = 1.2, n_levels = 0, 
                              compute_efficiency = 0, compute_uniformity=0, seed=0):

    """
    IftaPhaseSoftQuantization : Iterative Fourier Transform Algorithm with phase soft quantization
    
    Author : Francois Leroux
    Contact : francois.leroux.pro@gmail.com
    Status : in progress
    Last update : 2024.03.01, Brest
    Comments : for even support size, coordinates are defined like [-2,-1,0,1] (N = 4)
    
    Inputs : MANDATORY : target {2D float np.array}[Irradiance] : image we want to get at 
                                                                  infinity under plane wave illumination  
                          image_size {tupple (1x2)}[pixel] : size of the ifta 
                                                          Should have larger elements than target_image.shape 
    
              OPTIONAL :  n_iter {int} : number of iteration of each loop of the algorithm - default value = 25
                          r_fact {float} : reinforcment factor. Forces the energy to stay in 
                                          the ROI - default value = 1.2
                          n_levels : number of levels over which the phase will be 
                                    discretized - default value = 0 : no Discretization
                          compute_efficiency {bool} : If 1, efficiency is computed and returned along the loop
                                                      default value = 0
                          compute_uniformity {bool} : If 1, uniformity is computed and returned along the loop
                                                      default value = 0
                        
    Outputs : holo_phase
    """

    if compute_efficiency:
        efficiency = np.zeros(n_iter)             # memory allocation
        
    if compute_uniformity:
        uniformity = np.zeros(n_iter)             # memory allocation

    target_size = target.shape
    
    target_amp = np.asarray(target, float)       # conversion target to float
    target_amp = np.sqrt(target_amp)             # get target amplitude

    image_amp = np.zeros(image_size)                                                                             
    image_amp[image_size[0]//2-target_size[0]//2:image_size[0]//2-     # Amplitude output field = 0
              target_size[0]//2+target_size[0], 
              image_size[1]//2-target_size[1]//2:image_size[1]//2-
              target_size[1]//2+target_size[1]] = target_amp       # Amplitude = target image in window
    
    
    if type(seed) == int:
        image_phase = 2*np.pi*np.random.rand(image_size[0], image_size[1]) # Random image phase
    else:
        image_phase = seed   
    
    image_field = image_amp*np.exp(1j * image_phase)               # Initiate input field
    
    # First loop - continous phase screen computation
    
    for k in range(n_iter):
        holo_field = np.fft.ifft2(np.fft.ifftshift(image_field))         # field ifta = TF-1 field image
        holo_phase = np.angle(holo_field)                                 # save ifta phase
        holo_field = np.exp(holo_phase * 1j)                              # force the amplitude of the ifta to 1 (no losses)
        image_field = np.fft.fftshift(np.fft.fft2(holo_field))           # field image = TF field ifta
        image_phase = np.angle(image_field)                             # save image phase
        image_amp[image_size[0]//2-target_size[0]//2:image_size[0]//2-
                  target_size[0]//2+target_size[0], 
                  image_size[1]//2-target_size[1]//2:image_size[1]//2-
                  target_size[1]//2+target_size[1]] = rfact*target_amp  # force the amplitude of the ifta to the target 
                                                                        # amplitude inside the ROI. Outside the ROI, the 
                                                                        # amplitude is free
        image_field = image_amp*np.exp(image_phase * 1j)                # new image field computation
        
        if n_levels ==0 and compute_efficiency:
            efficiency[k] = ComputeEfficiency(holo_phase, image_amp)
            
        if n_levels ==0 and compute_uniformity:
            uniformity[k] = ComputeUniformity(holo_phase, image_amp)

    # Second loop - soft quantization

    if n_levels != 0:

        for k in range(n_iter):
            holo_field = np.fft.ifft2(np.fft.ifftshift(image_field))       # field ifta = TF-1 field image
            holo_phase = np.angle(holo_field)                              # get ifta phase. phase values between 0 and 2pi 
            holo_phase = SoftDiscretization(holo_phase, n_levels, half_interval=(k+1)*0.5/(n_iter))                                                                 # phase Discretization
            holo_field = np.exp(holo_phase * 1j)                           # force the amplitude of the ifta to 1 (no losses)
            image_field = np.fft.fftshift(np.fft.fft2(holo_field))         # image = TF du ifta
            image_phase = np.angle(image_field)                            # save image phase
            image_amp[image_size[0]//2-target_size[0]//2:image_size[0]//2- # force the amplitude of the ifta to the target
                      target_size[0]//2+target_size[0],                    # amplitude inside the ROI. Outside the ROI, the 
                      image_size[1]//2-target_size[1]//2:image_size[1]//2- # amplitude is free
                      target_size[1]//2+target_size[1]] = rfact*target_amp  
            image_field = image_amp*np.exp(image_phase * 1j)               # new image field computation
            
            if compute_efficiency:
                efficiency[k] = ComputeEfficiency(holo_phase, image_amp)
                
            if compute_uniformity:
                uniformity[k] = ComputeUniformity(holo_phase, image_amp)

    if compute_efficiency and not(compute_uniformity):
        return holo_phase, efficiency
    
    if compute_uniformity and not(compute_efficiency):
        return holo_phase, uniformity
    
    if compute_efficiency and compute_uniformity:
        return holo_phase, efficiency, uniformity

    return holo_phase


def IftaOverCompensation(target, image_size, *, n_iter = 25, compute_efficiency = 0, seed=0):
    """
    IftaOverCompensation : 
    
    Author : Francois Leroux
    Contact : francois.leroux.pro@gmail.com
    Status : in progress
    Last update : 2024.04.12, Brest
    Comments : 
    
    Inputs : MANDATORY : target {2D float np.array}[Irradiance] : image we want to get at 
                                                                  infinity under plane wave illumination  
                          image_size {tupple (1x2)}[pixel] : size of the ifmta     
             
            OPTIONAL :  n_iter {int} : number of iteration of each loop of the algorithm - default value = 25
    """

    












