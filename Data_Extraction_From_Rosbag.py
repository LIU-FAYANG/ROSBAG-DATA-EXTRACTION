import rosbag, sys, csv
import time
import string
import os #for file management make directory
#import shutil #for file management, copy file
import pandas as pd 
import csv

#verify correct input arguments: 1 or 2
if (len(sys.argv) > 2):
	print("invalid number of arguments:   " + str(len(sys.argv)))
	print("should be 2: 'bag2csv.py' and 'bagName'")
	print("or just 1  : 'bag2csv.py'")
	sys.exit(1)
elif (len(sys.argv) == 2):
	listOfBagFiles = [sys.argv[1]]
	numberOfFiles = "1"
	print("reading only 1 bagfile: " + str(listOfBagFiles[0]))
elif (len(sys.argv) == 1):
	listOfBagFiles = [f for f in os.listdir(".") if f[-4:] == ".bag"]	#get list of only bag files in current dir.
	numberOfFiles = str(len(listOfBagFiles))
	print("reading all " + numberOfFiles + " bagfiles in current directory: \n")
	for f in listOfBagFiles:
		print(f)
	print("\n press ctrl+c in the next 10 seconds to cancel \n")
	time.sleep(10)
else:
	print("bad argument(s): " + str(sys.argv))	#shouldnt really come up
	sys.exit(1)

count = 0
for bagFile in listOfBagFiles:
	count += 1
	print("reading file " + str(count) + " of  " + numberOfFiles + ": " + bagFile)
	#access bag
	bag = rosbag.Bag(bagFile)
	bagContents = bag.read_messages()
	bagName = bag.filename


	#create a new directory
	folder = string.rstrip(bagName, ".bag")
	try:	#else already exists
		os.makedirs(folder)
	except:
		pass
	#shutil.copyfile(bagName, folder + '/' + bagName)


	#get list of topics from the bag
	listOfTopics = []
	for topic, msg, t in bagContents:
		if topic not in listOfTopics:
			listOfTopics.append(topic)


	topicName = '/detection/vision_objects/front'
	filename = folder + '/' + string.replace(topicName, '/', '_slash_') + '.csv'
	with open(filename, 'w+') as csvfile:
		filewriter = csv.writer(csvfile, delimiter = ',')
		firstIteration = True	#allows header row
		for subtopic, msg, t in bag.read_messages(topicName):	# for each instant in time that has data for topicName
			#parse data from this instant, which is of the form of multiple lines of "Name: value\n"
			#	- put it in the form of a list of 2-element lists
			msgString = str(msg)
			msgList = string.split(msgString, '\n')
			instantaneousListOfData = []
			for nameValuePair in msgList:
				splitPair = string.split(nameValuePair, ':')
				for i in range(len(splitPair)):	#should be 0 to 1
					splitPair[i] = string.strip(splitPair[i])
				instantaneousListOfData.append(splitPair)
			#write the first row from the first element of each pair
			if firstIteration:	# header
				headers = ["rosbagTimestamp"]	#first column header
				for pair in instantaneousListOfData:
					headers.append(pair[0])
				filewriter.writerow(headers)
				firstIteration = False
			# write the value from each pair to the file
			values = [str(t)]	#first column will have rosbag timestamp
			for pair in instantaneousListOfData:
				if len(pair) > 1:
					values.append(pair[1])
			filewriter.writerow(values)
	bag.close()
    
	#First lets find the maximum column for all the rows
	with open(folder + "/" + "_slash_detection_slash_vision_objects_slash_front.csv", 'r') as temp_f:
		# get No of columns in each line
		col_count = [ len(l.split(",")) for l in temp_f.readlines() ]

	### Generate column names  (names will be 0, 1, 2, ..., maximum columns - 1)
	column_names = [i for i in range(max(col_count))] 

	import pandas as pd
	# inside range set the maximum value you can see in "Expected 4 fields in line 2, saw 8"
	# here will be 8 
	data = pd.read_csv(folder + "/"+"_slash_detection_slash_vision_objects_slash_front.csv",header = None,names=column_names )
	data.to_csv( folder + "_slash_detection_slash_vision_objects_slash_front.csv", index=False)

	f = pd.read_csv(folder + "_slash_detection_slash_vision_objects_slash_front.csv", usecols=[0,15,90,91,92,93,95,118,193,194,195,196,198,221,296,297,298,299,301,324,399,400,401,402,404,427,502,503,504,505,507])

	f.to_csv(folder+"_cleaned.csv", index=False)

    #Model With Traddic Lights
	f["15"] = f["15"].map({'"RedLeft"':0,'"Red"':1,'"RedRight"':2,'"GreenLeft"':3,'"Green"':4,'"GreenRight"':5,'"Yellow"':6,'"Off"':'7','"YellowRight"':8})
	f["118"] = f["118"].map({'"RedLeft"':0,'"Red"':1,'"RedRight"':2,'"GreenLeft"':3,'"Green"':4,'"GreenRight"':5,'"Yellow"':6,'"Off"':'7','"YellowRight"':8})
	f["221"] = f["221"].map({'"RedLeft"':0,'"Red"':1,'"RedRight"':2,'"GreenLeft"':3,'"Green"':4,'"GreenRight"':5,'"Yellow"':6,'"Off"':'7','"YellowRight"':8})
	f["324"] = f["324"].map({'"RedLeft"':0,'"Red"':1,'"RedRight"':2,'"GreenLeft"':3,'"Green"':4,'"GreenRight"':5,'"Yellow"':6,'"Off"':'7','"YellowRight"':8})
	f["427"] = f["427"].map({'"RedLeft"':0,'"Red"':1,'"RedRight"':2,'"GreenLeft"':3,'"Green"':4,'"GreenRight"':5,'"Yellow"':6,'"Off"':'7','"YellowRight"':8})

	#Model with Objects 
	#f["15"] = f["15"].map({'"Car"':0,'"Van"':1,'"Pedestrian"':2,'"Motorcyclist"':3,'"Truck"':4,'"Bus"':5,'"Cyclist"':6})
	#f["118"] = f["118"].map({'"Car"':0,'"Van"':1,'"Pedestrian"':2,'"Motorcyclist"':3,'"Truck"':4,'"Bus"':5,'"Cyclist"':6})
	#f["221"] = f["221"].map({'"Car"':0,'"Van"':1,'"Pedestrian"':2,'"Motorcyclist"':3,'"Truck"':4,'"Bus"':5,'"Cyclist"':6})
	#f["324"] = f["324"].map({'"Car"':0,'"Van"':1,'"Pedestrian"':2,'"Motorcyclist"':3,'"Truck"':4,'"Bus"':5,'"Cyclist"':6})
	#f["427"] = f["427"]..map({'"Car"':0,'"Van"':1,'"Pedestrian"':2,'"Motorcyclist"':3,'"Truck"':4,'"Bus"':5,'"Cyclist"':6})


	f["90"] = f["90"]/1024
	f["91"] = f["91"]/768
	f["92"] = f["92"]/1024
	f["93"] = f["93"]/768
	
	f["193"] = f["193"]/1024
	f["194"] = f["194"]/768
	f["195"] = f["195"]/1024
	f["196"] = f["196"]/768

	f["296"] = f["296"]/1024
	f["297"] = f["297"]/768
	f["298"] = f["298"]/1024
	f["299"] = f["299"]/768

	f["399"] = f["399"]/1024
	f["400"] = f["400"]/768
	f["401"] = f["401"]/1024
	f["402"] = f["402"]/768

	f["502"] = f["502"]/1024
	f["503"] = f["503"]/768
	f["504"] = f["504"]/1024
	f["505"] = f["505"]/768
	f["0"] = "x"
	f.to_csv(folder + "_cleaned.csv", index=False)

	with open(folder + "_cleaned.csv",'r') as f:
		with open(folder+ "_updated_cleaned.csv",'w') as f1:
			next(f) # skip header line
			for line in f:
				f1.write(line)


	try:
		if not os.path.exists(folder +'_txt'):
			os.makedirs(folder + '_txt')
	except OSError:
		print ('Error: Creating directory of data')


	with open(folder + "_updated_cleaned.csv", "r", ) as f:
		reader = csv.reader(f)

		rownumber = 0
		for row in reader:
			g=open(folder + '_txt'+ '/'+str(rownumber-1)+".txt","w")
			for i in row:
				if(i == 'x'):
					g.write('')
				elif(i!=''):
					g.write(i + ' ')
				else:
					g.write('\n')
			rownumber = rownumber + 1
			g.close()
			
	os.remove(folder + "_txt/-1.txt")

print("Done reading all " + numberOfFiles + " bag files.")


f = open("frames_contain_objects.txt", 'w')

directory_path = folder + '_txt'
No_of_files = len(os.listdir(directory_path))

for i in range(No_of_files):
    filename = folder+"_txt/"+str(i)+".txt"
    filesize = os.path.getsize(filename)
    i = ("%04d" % (i,))


    if filesize > 60:
        f.write(os.path.abspath("frames/"+i+".jpg"))
        f.write("\n")

f.close()