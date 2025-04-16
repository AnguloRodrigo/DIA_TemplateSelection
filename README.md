# DIA_TemplateSelection
Improve template selection for kernel matching difference image analysis using a priori based off the seeing and depth quality of the input images.

Inputs a pandas readable table consistinf of columns with filenames, seeing values, and depth values of images. Outputs a list of descending order of images quality as template choice.
This code uses column headers as filename, FWHM, and M5SIGMA.
    FWHM is the full-width at half maximum of the PSF of the image.
    M5SIGMA is defined as the magnitude of point sources for which the effective counts are at signal-to-noise of 5.
One may need to change these for their correct columns.

Requirements:
    Numpy
    Pandas

How to use:
python getorder_template.py [table of images]

Example:
python getorder_template.py example_field257A.txt

 Returns ordered list as example_field257A_tmplorder.txt
