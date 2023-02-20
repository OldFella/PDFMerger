"""
Script to merge and compress all PDFs of a given directory.
"""


import PyPDF2 as pdf
import os
import argparse
import subprocess
import os.path
import sys
import shutil
import random
import re

PATH = os.path.dirname(os.path.realpath(__file__))

def compress(input_file_path, output_file_path, power=0):
    """
    Function to compress PDF via Ghostscript command line interface
    (https://github.com/theeko74/pdfc/blob/master/pdf_compressor.py)
    """
    quality = {
        0: '/default',
        1: '/prepress',
        2: '/printer',
        3: '/ebook',
        4: '/screen'
    }

    # Basic controls
    # Check if valid path
    if not os.path.isfile(input_file_path):
        print("Error: invalid path for input PDF file")
        sys.exit(1)

    # Check if file is a PDF by extension
    if input_file_path.split('.')[-1].lower() != 'pdf':
        print("Error: input file is not a PDF")
        sys.exit(1)

    gs = get_ghostscript_path()
    print("Compress PDF...")
    initial_size = os.path.getsize(input_file_path)
    subprocess.call([gs, '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                    '-dPDFSETTINGS={}'.format(quality[power]),
                    '-dNOPAUSE', '-dQUIET', '-dBATCH',
                    '-sOutputFile={}'.format(output_file_path),
                     input_file_path]
    )
    final_size = os.path.getsize(output_file_path)
    ratio = 1 - (final_size / initial_size)
    print("Compression by {0:.0%}.".format(ratio))
    print("Final file size is {0:.1f}MB".format(final_size / 1000000))


def get_ghostscript_path():
    gs_names = ['gs', 'gswin32', 'gswin64']
    for name in gs_names:
        if shutil.which(name):
            return shutil.which(name)
    raise FileNotFoundError(f'No GhostScript executable was found on path ({"/".join(gs_names)})')



def merge(dir, out, sort):
	print('Load PDFs...')
	files = os.listdir(dir)
	files = list(filter(lambda f: f.endswith(('.pdf')), files))

	if sort:
		numbers_check = [int(re.search(r'\d+', s).group()) for s in files]
		if len(numbers_check) == len(files):
			files = sorted(files, key=lambda s: int(re.search(r'\d+', s).group()))
		else:
			files = sorted(files)

	merger = pdf.PdfFileMerger()


	print('Merge PDFs...')
	for file in files:
		merger.append(dir + "/" + file, file)

	merger.setPageMode('/UseOutlines')
	print('Save PDF...')
	merger.write(out)
	merger.close()

def replace(to_keep, to_replace):
	os.replace(to_replace, to_keep)
	# os.remove(to_replace)

def main():
	parser = argparse.ArgumentParser(description = 'Merge PDFs')
	parser.add_argument('-i', type = str, help = 'Relative path to the pdf files. Default = Current Path', default = PATH)
	parser.add_argument('-o', metavar = '--output', type = str, help = 'Name of the output file. Default = output.pdf', default = 'output.pdf')
	parser.add_argument('-s', metavar = '--sort', type = bool, help = 'Sort the files. Default = True', default = True)
	parser.add_argument('-c', metavar = '--compress', type = int, help = 'Compression degree the resulting pdf. Default = -1 (for no compression)', default = -1)
	

	args = parser.parse_args()

	OUTPUT = args.i + '/' + args.o

	merge(args.i, OUTPUT, args.s)

	compression_power = args.c
	if compression_power != -1:
		rand = random.randint(100000, 999999)
		TMP = f'tmp_{rand}.pdf'
		print('Create ' + TMP + '...')
		compress(OUTPUT, TMP, compression_power)
		print('Delete '+ TMP + '...')
		replace(OUTPUT, args.i+ '/' + TMP)

	print('Done.')


if __name__ == '__main__':
	main()