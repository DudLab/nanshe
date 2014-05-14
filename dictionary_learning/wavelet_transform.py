# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ ="$May 1, 2014 2:24:55 PM$"



import numpy
import scipy
import scipy.misc
import vigra


def bin_coeffs(n):
    """
        Generates a row in Pascal's triangle (binomial coefficients).
        
        Args:
            n(int):      which row of Pascal's triangle to return.
        
        Returns:
            cs(numpy.ndarray): a numpy array containing the row of Pascal's triangle.
        
        
        Examples:
            >>> bin_coeffs(0)
            array([1])
                   
            >>> bin_coeffs(1)
            array([1, 1])
                   
            >>> bin_coeffs(2)
            array([1, 2, 1])
                   
            >>> bin_coeffs(4)
            array([1, 4, 6, 4, 1])
                   
            >>> bin_coeffs(4.0)
            array([1, 4, 6, 4, 1])
    """
    
    # Below 0 is irrelevant. 
    if n < 0:
        n = 0
    
    # Get enough repeats of n to get each coefficent
    ns = numpy.repeat(n, n + 1).astype(int)
    # Get all relevant k's
    ks = numpy.arange(n + 1).astype(int)
    
    # Get all the coefficents in order
    cs = scipy.misc.comb(ns, ks)
    cs = numpy.around(cs)
    cs = cs.astype(int)
    
    return(cs)


def h(i, n = 4):
    """
        Generates a 1D numpy array used to make the kernel for the wavelet transform.
        
        Args:
            i(int):      which scaling to use.
            n(int):      which row of Pascal's triangle to return.
        
        Returns:
            r(numpy.ndarray): a numpy array containing the row of Pascal's triangle.
        
        
        Examples:
            >>> h(0)
            array([ 0.0625,  0.25  ,  0.375 ,  0.25  ,  0.0625])
            
            >>> h(0, 4)
            array([ 0.0625,  0.25  ,  0.375 ,  0.25  ,  0.0625])
            
            >>> h(1, 4)
            array([ 0.0625,  0.25  ,  0.375 ,  0.25  ,  0.0625])
            
            >>> h(2, 4)
            array([ 0.0625,  0.    ,  0.25  ,  0.    ,  0.375 ,  0.    ,  0.25  ,
                    0.    ,  0.0625])
            
            >>> h(3, 4)
            array([ 0.0625,  0.    ,  0.    ,  0.    ,  0.25  ,  0.    ,  0.    ,
                    0.    ,  0.375 ,  0.    ,  0.    ,  0.    ,  0.25  ,  0.    ,
                    0.    ,  0.    ,  0.0625])
            
            >>> h(4, 4)
            array([ 0.0625,  0.    ,  0.    ,  0.    ,  0.    ,  0.    ,  0.    ,
                    0.    ,  0.25  ,  0.    ,  0.    ,  0.    ,  0.    ,  0.    ,
                    0.    ,  0.    ,  0.375 ,  0.    ,  0.    ,  0.    ,  0.    ,
                    0.    ,  0.    ,  0.    ,  0.25  ,  0.    ,  0.    ,  0.    ,
                    0.    ,  0.    ,  0.    ,  0.    ,  0.0625])
            
            >>> h(2, 1)
            array([ 0.5,  0. ,  0.5])
    """
    
    # Below 1 is irrelevant.
    if i < 1:
        i = 1
    
    # Below 0 is irrelevant. 
    if n < 0:
        n = 0
    
    # Get the binomial coefficients.
    cs = list(bin_coeffs(n))
    
    # Get the right number of zeros to fill in
    zs = list(numpy.zeros(2**(i-1) - 1).astype(int))
    
    # Create the contents of the 1D kernel before normalization
    r = []
    if len(cs) > 1:
        for _ in cs[:-1]:
            r.append(_)
            r.extend(zs)
        
        r.append(cs[-1])
    else:
        r.append(_)
    
    r = numpy.array(r)
    r = r.astype(float)
    
    # Normalization on the L_1 norm.
    r /= 2**n
    
    return(r)


def vigra_kernel_h(i, n = 4, border_treatment = vigra.filters.BorderTreatmentMode.BORDER_TREATMENT_REFLECT):
    """
        Generates a vigra.filters.Kernel1D using h(i).
        
        Args:
            i(int):                                                 which scaling to use.
            n(int):                                                 which row of Pascal's triangle to return.
            border_treatment(vigra.filters.BorderTreatmentMode):    determines how to deal with the borders.
        
        Returns:
            k(numpy.ndarray): a numpy array containing the row of Pascal's triangle.
        
        
        Examples:
            >>> vigra_kernel_h(1) # doctest: +ELLIPSIS
            <vigra.filters.Kernel1D object at 0x...>
    """
    
    # Generate the vector for the kernel
    h_kern = h(i, n)
    
    # Determine the kernel center
    h_kern_half_width = (h_kern.size - 1) / 2
    
    # Default kernel
    k = vigra.filters.Kernel1D()
    # Center the kernel
    k.initExplicitly(-h_kern_half_width, h_kern_half_width, h_kern)
    # Set the border treatment mode.
    k.setBorderTreatment(border_treatment)
    
    return(k)


def wavelet_transform(im0, scale = 5):
    """
        performs integral steps of the wavelet transform on im0 up to the given scale. If scale is an iterable, then 
        
        Args:
            i(int):                                                 which scaling to use.
            n(int):                                                 which row of Pascal's triangle to return.
            border_treatment(vigra.filters.BorderTreatmentMode):    determines how to deal with the borders.
        
        Returns:
            k(numpy.ndarray): a numpy array containing the row of Pascal's triangle.
        
        
        Examples:
            >>> wavelet_transform(numpy.eye(3).astype(numpy.float32), 1) # doctest: +NORMALIZE_WHITESPACE
            (array([[[ 0.59375, -0.375  , -0.34375],
                     [-0.375  ,  0.625  , -0.375  ],
                     [-0.34375, -0.375  ,  0.59375]]]),
             array([[[ 1.    ,  0.     ,  0.     ],
                    [ 0.     ,  1.     ,  0.     ],
                    [ 0.     ,  0.     ,  1.     ]],
                   [[ 0.40625,  0.375  ,  0.34375],
                    [ 0.375  ,  0.375  ,  0.375  ],
                    [ 0.34375,  0.375  ,  0.40625]]]))
    """
    
    # Make sure that we have scale as a list.
    # If it is not a list, then make a singleton list.
    try:
        scale = numpy.array(list(scale))
        
        if scale.ndim > 1:
            raise Error("Scale should only have 1 dimension. Instead, got scale.ndim = \"" + str(scale.ndim) + "\".")
        
        if scale.shape[0] != im0.ndim:
            raise Error("Scale should have a value of each dimension of im0. Instead, got scale.shape[0] = \"" + str(scale.shape[0]) + "\" and im0.ndim = \"" + str(im0.ndim) + "\".")
    
    except TypeError:
        scale = numpy.repeat([scale], im0.ndim)
    
    imOut = numpy.zeros((scale.max() + 1,) + im0.shape) # Why 6? When are we doing the 5th? I know Ferran told us before, but let's check again.
    W = numpy.zeros((scale.max(),) + im0.shape) # Need differences, but should we have 5 dimensions? Made 5 anyways, unlike Ferran.
    
    imOut[0] = im0
    imPrev = im0.copy()
    imCur = im0.copy()
    for i in xrange(1, scale.max() + 1): # Ferran does not do the 5th yet, but we will
        
        h_ker = vigra_kernel_h(i)
        
        for d in xrange(len(scale)):
            if i <= scale[d]:
                imCur = vigra.filters.convolveOneDimension(imCur, d, h_ker)
        
        W[i-1] = imPrev - imCur
        imOut[i] = imCur
        imPrev = imCur
    
    return((W, imOut))