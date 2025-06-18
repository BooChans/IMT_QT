# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 13:44:30 2024 under Python 3.11.7

@author: f24lerou
"""

# 8<----------------------------------------- Import modules -----------------------------------

import numpy as np

# 8<--------------------------------------- Functions definitions ------------------------------


def Discretization(phase, n_levels):
    """
    discretization : return an array of phase values between 0 and 2pi, discretized over n_levels

    Author : Francois Leroux
    Contact : francois.leroux.pro@gmail.com
    Status : done
    Last update : 2024.03.07, Brest

    Comments :

    Inputs : MANDATORY : phase {float}
                          n_levels {int}

    Outputs : phase : the discretized phase, values between 0 and 2pi - 2pi/n_levels
    """

    if n_levels == 0:

        return phase

    else:

        phase = np.remainder(
            phase, 2 * np.pi
        )  # continuous phase values between 0 and 2pi
        phase = (
            phase * (n_levels) / (2 * np.pi)
        )  # continuous phase values between 0 and n_levels
        phase = np.round(
            phase
        )  # phase discretization. discrete phase values between 0 and n_levels
        phase = 2 * np.pi / n_levels * phase  # discretized phase between 0 and 2pi
        phase = np.remainder(
            phase, 2 * np.pi
        )  # discretized phase between 0 and 2pi - 2pi/n_levels

    return phase


def SoftDiscretization(phase, n_levels, half_interval):
    """
    softDiscretization : return an array of phase values between 0 and 2pi, Softdiscretized over n_levels

    Author : Francois Leroux
    Contact : francois.leroux.pro@gmail.com
    Status : done
    Last update : 2024.03.07, Brest

    Comments :

    Inputs : MANDATORY : phase {float}
                          n_levels {int}
                          half_interval : only the phase between n-half_interval and n+half_interval will be discretized.
                                          Should be less than 0.5
    Outputs : phase : the discretized phase, values between 0 and 2pi - 2pi/n_levels
    """

    if n_levels == 0:

        return phase

    else:

        phase = np.remainder(
            phase, 2 * np.pi
        )  # continuous phase values between 0 and 2pi
        phase = (
            phase * (n_levels) / (2 * np.pi)
        )  # continuous phase values between 0 and n_levels
        phase[np.remainder(phase, 1) <= half_interval] = (
            np.round(  # phase soft discretization.
                phase[np.remainder(phase, 1) <= half_interval]
            )
        )  # discrete phase values between 0 and n_levels-1
        phase[np.remainder(phase, 1) >= 1 - half_interval] = (
            np.round(  # phase soft discretization.
                phase[np.remainder(phase, 1) >= 1 - half_interval]
            )
        )  # discrete phase values between 0 and n_levels-1
        phase = 2 * np.pi / n_levels * phase  # discretized phase between 0 and 2pi
        phase = np.remainder(
            phase, 2 * np.pi
        )  # discretized phase between 0 and 2pi - 2pi/n_levels

    return phase


def GetCartesianCoordinates(nrows, **kargs):
    """
    GetCartesianCoordinates : generate two arrays representing the cartesian coordinates

    Author : Francois Leroux
    Contact : francois.leroux.pro@gmail.com
    Status : in progress
    Last update : 2024.03.05, Brest
    Comments : For even support size, coordinates are defined like [-2,-1,0,1] (N = 4)
               (i.e the origin is the top right pixel of the four central ones)

    Inputs : MANDATORY : nrows {int} : the number of rows

              OPTIONAL : ncols {int} : the number of columns

    Outputs : [X,Y], two arrays representing the cartesian coordinates
    """

    # read optinal parameters values
    ncols = kargs.get("ncols", nrows)

    [X, Y] = np.meshgrid(
        np.arange(-ncols // 2 + ncols % 2, ncols // 2 + ncols % 2),
        np.arange(nrows // 2 - 1 + nrows % 2, (-nrows) // 2 - 1 + nrows % 2, step=-1),
    )

    return np.array([X, Y])


def Replicate(phase_holo, n_replications):
    """
    Replicate : replicate an hologram n_replications times in x and y directions

    Author : Francois Leroux, Chat GPT was used.
    Contact : francois.leroux.pro@gmail.com
    Status : in progress
    Last update : 2024.03.05, Brest
    Comments : Peut servir à augmenter la taille

    Inputs : MANDATORY : array {np.array 2D} : the array to zeros padd

              OPTIONAL : zeros_padding_factor {int} : the zeros padding factor

    Outputs : array_zeros_padded : the array zeros padded
    """

    phase_holo_replicated = np.full(np.array(phase_holo.shape) * n_replications, np.nan)

    for i in range(n_replications):
        for j in range(n_replications):
            phase_holo_replicated[
                i * phase_holo.shape[0] : (i + 1) * phase_holo.shape[0],
                j * phase_holo.shape[1] : (j + 1) * phase_holo.shape[1],
            ] = phase_holo

    return phase_holo_replicated


def RadToUint8(discretized_phase, n_levels):

    discretized_phase = discretized_phase * 255 / (2 * np.pi * (1 - 1 / n_levels))

    return np.asarray(discretized_phase, dtype=np.uint8)


def ComputeFocal(d1, d2):
    """
    computeFocal : compute the focal lenght needed for conjugating a point at distance d1 with
                   respect to the lens in object space
                   to a point at distance d2 with respect to the lens in image space
                   Descartes formula: 1/d2 + 1/d1 = 1/f => f = d1*d2/(d1+d2)

    Author : Francois Leroux
    Contact : francois.leroux.pro@gmail.com
    Status : in progress
    Last update : 2024.02.29, Brest

    Comments :

    Inputs : MANDATORY : d1 {float}[m] : absolute distance object point - lens
                          d2 {float}[m] : absolute distance lens - image point

    Outputs : f : the focal lenght of the corresponding convergent lens
    """

    f = d1 * d2 / (d1 + d2)

    return f


def Alphabet():
    """
    Alphabet : return an array containing all the letters of latin alphabet, in CAPITAL

    Author : Francois Leroux
    Contact : francois.leroux.pro@gmail.com
    Status : done
    Last update : 2024.06.10, Brest

    Comments :

    Inputs : MANDATORY : none

    Outputs : alphabet : an array containing all the letters of latin alphabet, in CAPITAL
    """

    alphabet = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
    ]

    return alphabet
