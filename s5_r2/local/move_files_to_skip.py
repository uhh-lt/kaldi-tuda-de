import os, glob, sys

with open("local/tuda_files_to_skip.txt") as f:
    files_to_skip = f.readlines()
files_to_skip = [x.strip() for x in files_to_skip] # remove new line char

for directory in sys.argv[1:]:
	if not directory.endswith('/'):
		directory += '/'
	backup_path = directory + ".backup_skipped_files/"
	if not os.path.isdir(backup_path):
		os.makedirs(backup_path)
	print("Move_files_to_skip.py: Moving files to skip from " + directory + " to " + backup_path)
	for file_to_skip in files_to_skip:
		for filename in glob.glob(directory + file_to_skip + '*'):
			path = os.path.normpath(filename)
			splitted_path = path.split(os.sep)
			os.rename(filename, backup_path + splitted_path[-1])
