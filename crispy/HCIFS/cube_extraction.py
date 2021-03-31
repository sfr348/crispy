# created by He Sun on 09/20/2019
# modified from HCIFS_Workbook.ipynb developed by Maxime Rizzo

import numpy as np
import matplotlib.pyplot as plt
import glob
import time
from astropy.io import fits
import sys
import os
import sys
folder = 'C:/Lab/crispy'
if folder not in sys.path: sys.path.append(folder)

from crispy.tools.initLogger import getLogger
from params import Params
from crispy.tools.wavecal import buildcalibrations
from crispy.IFS import reduceIFSMap

def main():
	log = getLogger('crispy')
	os.chdir('C:/Lab/crispy/crispy/HCIFS/')

	par = Params()
	par.hdr

	# folder= 'C:/Lab/FPWCmatlab/IFS/flat8/'
	folder= 'C:/Lab/FPWCmatlab/IFS/flat100/'
	file_list = os.listdir(folder)
	file_list.sort()
	par.lamlist = [600.,620.,640.,650.,670.,694.3,720.]
	#par.lamlist = [550., 577., 600., 620., 632.8, 640., 650., 670., 694.3, 720., 740.]
	orig_filelist = [folder+val for val in file_list]
	orig_filelist = orig_filelist#[3:10]

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

	# create a flag once finish calibrating the IFS
	f = open('C:/Lab/FPWCmatlab/IFS/flags/crispyflag.txt', 'w+')
	f.close()
	time.sleep(1)

	# extract data cube once we get new images
	log.info('Running CRISPY data cube extraction ...')
	while True:
		if os.path.exists('C:/Lab/FPWCmatlab/IFS/flags/newimgflag.txt'):
			broadband_image = 'C:/Lab/FPWCmatlab/IFS/data/broadband_image.fits'
			with fits.open(broadband_image) as PSF_file:
				# invert the file to make sure dispersion goes from left to right
				cube = reduceIFSMap(par,PSF_file[0].data[:,::-1],name='PSF',method='sum',medsub=False)
			hdu = fits.PrimaryHDU()
			hdu.data = cube.data
			hdu.writeto('C:/Lab/FPWCmatlab/IFS/data/cube.fits')
			time.sleep(2)
			f = open('C:/Lab/FPWCmatlab/IFS/flags/newcubeflag.txt', 'w+')
			f.close()
			os.remove('C:/Lab/FPWCmatlab/IFS/flags/newimgflag.txt')
			os.remove(broadband_image)
			
		time.sleep(1)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('Interrupted')
		os.remove('C:/Lab/FPWCmatlab/IFS/flags/crispyflag.txt')
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)