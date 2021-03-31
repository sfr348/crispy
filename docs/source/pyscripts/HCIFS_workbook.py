import numpy as np
import glob
from astropy.io import fits
import sys
import os
from crispy.tools.initLogger import getLogger
log = getLogger('crispy')
os.chdir('/home/groot/HCIL/crispy/crispy/HCIFS/')

# load HCIFS parameters
from params import Params
par = Params()
par.hdr

# load flat files
# note that I changed the filenames to make sure they sort in 
# the way I expect
folder = '/home/groot/HCIL/HCIFS/flat/'

file_list = os.listdir(folder)
file_list.sort()
orig_filelist = [folder+val for val in file_list[:-1]]
par.lamlist = [550.,577.,600.,620.,632.8,640.,650.,670.,694.3,720.,740.]

log.info(orig_filelist)
log.info(par.lamlist)

# Flip the x axis of the images in order for the dispersion 
# direction to go from left to right as the wavelength increases
par.filelist = []
for fname in orig_filelist:
    img = fits.getdata(fname)[:,::-1]
    new_fname = par.wavecalDir+fname.split('/')[-1]
    fits.writeto(new_fname,img,overwrite=True)
    par.filelist.append(new_fname)
log.info(par.filelist)

# build calibration
from crispy.tools.wavecal import buildcalibrations
buildcalibrations(par,
                    inspect=True,         # if True, constructs a bunch of images to verify a good calibration
                    inspect_first=True,         # if True, constructs an image to verify a good calibration
                    genwavelengthsol=True, # Compute wavelength at the center of all pixels
                    makehiresPSFlets=True, # this requires very high SNR on the monochromatic frames
                    makePSFWidths=True,
                    makePolychrome=True,   # This is needed to use least squares extraction
                    upsample=3,            # upsampling factor of the high-resolution PSFLets
                    nsubarr=3,             # the detector is divided into nsubarr^2 regions for PSFLet averaging
                    apodize=False,          # to match PSFlet spot locations, only use the inner circular part of the 
                                           #detector, hence discarding the corners of the detector where lenslets are 
                                           #distorted
                    finecal=False
                  ) 

lam_midpts,lam_endpts = calculateWaveList(par,method='optext')

# extract the datacube
from crispy.IFS import reduceIFSMap
cube = reduceIFSMap(par,par.filelist[5],
                        method='sum',medsub=False
                       )


for k in range(cube.data.shape[0]):
	print('k: {}, mean: {}'.format(k, np.mean(cube.data[k, 30:70, 30:70])))
