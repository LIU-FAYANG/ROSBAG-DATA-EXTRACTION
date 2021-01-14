import os

directory_path =  'delayed'
No_of_files = len(os.listdir(directory_path))

#remove empty txt files
for i in range(No_of_files):
	filename = directory_path + "/"+str(i)+".txt"
	with open(filename, 'r') as read_obj:
		# read first character
		one_char = read_obj.read(1)
		# if not fetched then file is empty
		if one_char == '\n':
			os.remove(filename)
	