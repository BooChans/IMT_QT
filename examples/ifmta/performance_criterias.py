# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 15:57:04 2024

@author: f24lerou
"""

#%% 8<-------------------------------------- Import modules -----------------------------------

import numpy as np

#%% 8<--------------------------------------- Functions definitions ------------------------------

def ComputeEfficiency(phase_holo, target):
    """
    ComputeEfficiency : compute the efficiency of an hologram
    
    Author : Francois Leroux
    Contact : francois.leroux.pro@gmail.com
    Status : in progress
    Last update : 2024.04.22, Brest
    Comments : 
      
    Inputs : MANDATORY : phase_holo : phase mask corresponding to the hologram to characterize
                         target : target image used during the IFTA process
             
    Outputs : efficiency, percentage of the light that end up in the illuminated zones planned by target
    """
    
    
    recovery = np.absolute(np.fft.fftshift(np.fft.fft2(np.exp(1j*phase_holo))))**2 # Final image = |TF field DOE|^2
    efficiency = np.sum(recovery[target!=0])/np.sum(recovery)
    
    return efficiency

def ComputeUniformity(phase_holo, target):
    """
    ComputeUniformity : compute the uniformity of an hologram
    
    Author : Francois Leroux
    Contact : francois.leroux.pro@gmail.com
    Status : in progress
    Last update : 2024.04.22, Brest
    Comments : 
      
    Inputs : MANDATORY : phase_holo : phase mask corresponding to the hologram to characterize
                         target : target image used during the IFTA process
             
    Outputs : uniformity, (Irradiance_max - Irradiance_min) / (Irradiance_max + Irradiance_min)
              of the image formed by phase_holo
    """
    
    recovery = np.absolute(np.fft.fftshift(np.fft.fft2(np.exp(1j*phase_holo))))**2 # Final image = |TF field DOE|^2
    recovery = recovery[target!=0]
    uniformity = (np.max(recovery)-np.min(recovery))/(np.max(recovery)+np.min(recovery))
    
    return uniformity
