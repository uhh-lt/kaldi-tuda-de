import os, glob, sys

with open("local/tuda_files_to_skip.txt") as f:
    files_to_skip = f.readlines()
files_to_skip = [x.strip() for x in files_to_skip] # remove new line char

for directory in sys.argv:
	if not directory.endswith('/'):
		directory += '/'
	for file_to_skip in files_to_skip:
		for filename in glob.glob(directory + file_to_skip + '*'):
		    os.remove(filename)
