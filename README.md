# DIA_TemplateSelection
Improve template selection for kernel matching difference image analysis using a priori based off the seeing and depth quality of the input images.

Inputs a list of filenames, FWHM values, and m5sigma values of images in a pandas readable table. Outputs a list of descending order of images quality as template choice.

Example:
python getorder_templates.py <file pattern (e.g. *.dcmp)>
    - can specify directory where data is located with --input_dir
