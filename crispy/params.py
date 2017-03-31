#!/usr/bin/env python

import os
import numpy as np
from numpy import sqrt,arcsin
try:
    from astropy.io import fits
except:
    import pyfits as fits


class Params():

    def __init__(self,codeRoot='.'):
        '''
        Main class containing all the sim parameters
        '''

        self.saveRotatedInput = False
        self.saveLensletPlane = False 
        self.saveDetector = True
        self.codeRoot = codeRoot
        self.prefix = self.codeRoot+'/ReferenceFiles'
        self.exportDir = self.codeRoot+'/SimResults'
        self.unitTestsOutputs = self.codeRoot+'/unitTestsOutputs'
#         self.wavecalDir = self.prefix+'/VARIAwavecal/'
#         self.wavecalDir = self.prefix+'/HighSNRWavecal/'
#         self.wavecalDir = self.prefix+'/wavecal/'
#         self.wavecalDir = self.prefix+'/wavecalR50_660/'
        self.wavecalDir = self.prefix+'/wavecalR50_770/'
#         self.wavecalName = 'VARIAcalCube.fits'
#         self.wavecalName = 'LLTFcalCube.fits'
#         self.wavecalName = 'simCalCube.fits'
        self.filelist = []
        self.lamlist = []

        ###################################################################### 
        # Basic resolution/configuration parameters
        ###################################################################### 

        self.nlens = 108            # Number of lenslets across array (account for rotation)
        self.pitch = 174e-6         # Lenslet pitch (meters)
        self.interlace = 2          # Interlacing
        self.philens = arcsin(1./sqrt(self.interlace**2+1)) # Rotation angle of the lenslets (radians)
        self.pinhole = True         # Use a pinhole grid? (not really used)
        self.pin_dia = 25e-6        # Diameter of pinholes (m) (not really used)
        self.lenslet_sampling= 1./2.# lenslet size in lambda/D
        self.lenslet_wav = 600.     # Wavelength at which this is defined (nm)

        ###################################################################### 
        # Detector stuff
        ###################################################################### 
        
        self.npix = 1024            # Number of pixels in final detector
        self.pixsize = 13e-6        # Pixel size (meters)
        self.pxperdetpix = 1       # Oversampling of the final detector pixels
        self.convolve = True        # whether to convolve the existing kernels with
                                    # gaussian kernel (simulating defocus)
        self.FWHM = 2               # FWHM of gaussian kernel
        self.FWHMlam = 660.         # Lam at which FWHM is defined
        self.gaussian = True        # Use standard Gaussian kernels instead of library
        self.gaussian_hires = True  # Use Gaussians for hires PSFLet matching, instead
                                    # of Lucy-Richardson deconvolution

        self.poisson = True        # FWHM of gaussian kernel (e/px/fr)
        self.RN = 0.0               # FWHM of gaussian kernel (e/px/fr)
        self.CIC = 1e-3             # Clock-induced charge (e/px/fr)
        self.dark = 1e-4            # Dark current noise (e/px/s)
        self.Traps = False          # Use standard Gaussian kernels instead of library

        self.QE = 0.68				# detector QE; need to make this wavelength-dependent
        self.losses = 0.34			# total losses for on-axis PSF (given by J. Krist)
        self.PhCountEff = 0.8		# Photon counting efficiency
        self.CTE = 0.893		    # Charge transfer efficiency (varies with lifetime)
        self.pol = 1.		        # Polarization losses
        self.Nreads = 10			# number of reads for a frame
        self.timeframe = 1000		# time in second for a frame (from file)

        ###################################################################### 
        # Spectrograph stuff
        ###################################################################### 
        
        self.distortPISCES=False    # If True, use measured PISCES distortion/dispersion
        self.BW = 0.18              # Spectral bandwidth (if distortPISCES==False)
        self.npixperdlam = 2        # Number of pixels per spectral resolution element
        self.R = 50                 # Spectral resolving power (extracted cubes have twice)

        self.makeHeader()

    def makeHeader(self):
        self.hdr = fits.PrimaryHDU().header
        self.hdr.append(('comment', ''), end=True)
        self.hdr.append(('comment', '*'*60), end=True)
        self.hdr.append(('comment', '*'*22 + ' General parameters ' + '*'*18), end=True)
        self.hdr.append(('comment', '*'*60), end=True)    
        self.hdr.append(('comment', ''), end=True)
        self.hdr.append(('NLENS',self.nlens,'# lenslets across array'), end=True) 
        self.hdr.append(('PITCH',self.pitch,'Lenslet pitch (meters)'), end=True) 
        self.hdr.append(('INTERLAC',self.interlace,'Interlacing'), end=True) 
        self.hdr.append(('PHILENS',self.philens*180./np.pi,'Rotation angle of the lenslets (deg)'), end=True) 
        self.hdr.append(('PIXSIZE',self.pixsize,'Pixel size (meters)'), end=True) 
        self.hdr.append(('LENSAMP',self.lenslet_sampling,'Lenslet sampling (lam/D)'), end=True) 
        self.hdr.append(('LSAMPWAV',self.lenslet_wav,'Lenslet sampling wavelength (nm)'), end=True) 
        self.hdr.append(('FWHM',self.FWHM,'FHWM of PSFLet at detector (pixels)'), end=True) 
        self.hdr.append(('FWHMLAM',self.FWHMlam,'Wavelength at which FWHM is defined (nm)'), end=True) 
        self.hdr.append(('NPIX',self.npix,'Number of detector pixels'), end=True) 
        self.hdr.append(('DISPDIST',self.distortPISCES,'Use PISCES distortion/dispersion?'), end=True) 
        if self.distortPISCES:
            self.hdr.append(('BW',self.BW,'Bandwidth'), end=True) 
            self.hdr.append(('PIXPRLAM',self.npixperdlam,'Pixels per resolution element'), end=True) 
            self.hdr.append(('R',self.R,'Spectral resolution'), end=True) 
        
