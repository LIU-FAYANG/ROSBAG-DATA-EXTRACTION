# ROSBAG-DATA-EXTRACTION
extract image and bounding box coordinate from rosbag
## Image Extraction 
Copy the compressed file to a certain location and decompress the file:
```
cp ./2b_bag_1113.tar.gz(compressed file name) ~/Documents 
sync
tar -xzvf filename.tar.gz  //decompress to current repository 

```

Build msg types for the rostopic
```
cd Documents/msg_ws/
ls
catkin bulid 
```

Set up: install the image_view package
```
sudo apt install ros-melodic-image-view 
roscd image_view
rosmake image_view
sudo apt-get install mjpegtools
```

Run the roscore and play the recorded data inside the rosbag,check the ros topics with images and bounding box corrdinates.
```
roscore
rqt_image_view   #image viewer, sycronized with the running rosbag topic
rosbag play ~/Documents/2020-11-13-15-33-10.bag 
Rosbag play ~/DOcuments/2020-11-13-15-33-10.bag -s 250  // -s: start point

rostopic list //get the list of rostopic, in this case, the image_rects contains the frames and boject_detect_front contan the coordinates
```

ROS topics related to frames and bouding boxes:
```
/camera/image_rects : traffic lights
/stereo/long/image_rects : traffic lights
/stereo/short/image_rects : obstales 

/detection/vision_objects/traffic_light
/detection/vision_objects/front

```

Image Extraction

ROS tutorial link:
http://wiki.ros.org/rosbag/Tutorials/Exporting%20image%20and%20video%20data#Tutorial_setup

Need to check the UNIX timestamp to obtain the extracted csv file to get the PFS(frames per second) value(in csv file):


Take note that different rosbag may have different rostopic name for the data you want to extract.

```
roscore
rosbag info (path of the rosbag)

rosrun image_view image_saver _sec_per_frame:=0.1 image:=/stereo/long/image_rects theora   //10 frames per second
rosrun image_view image_saver _sec_per_frame:=0.05 image:=/camera/image_rects theora       //20 frames per second.

rosbag play (path of the rosbag)
```

# Extract bounding box coordinates in YOLO format.

## Instruction: put Data_Extraction_From_Rosbag_final.py and the bagfiles in the same folder, run the python script txt files will be extracted to bagfilename_txt.


Linux OS:
Download latest version of Ubuntu from: https://ubuntu.com/download

Start-up disk: https://rufus.ie/

PACKAGE:
Rosbag package installation:
https://anaconda.org/conda-forge/ros-rosbag
Cryptodome package installation:
https://anaconda.org/anaconda/pycryptodomex


Origional bag_to_csv.py from [This Site](http://www.clearpathrobotics.com/assets/guides/kinetic/ros/Converting%20ROS%20bag%20to%20CSV.html)

The python file will convert every rostopic into csv files.
Choose the one with name: _slash_detection_slash_vision_objects_slash_front.csv, which contains the coordinates of the bounding box:(in yolo format)

Note: Do not convert the csv file into a xsl file,that may result in data loss.

## Simply convert the scv files to multiple txt files.
Simple python program, read each row from the csv file.
Every extracted row is an array, we can spilt the array the write into the csv file.

```
import csv

with open("DATA.csv", "r", ) as f:
    reader = csv.reader(f)

    rownumber = 0
    for row in reader:
        g=open(str(rownumber)+".txt","w")
        for i in row:
            if(i == 'x'):
                g.write('')
            elif(i!=''):
                g.write(i + ' ')
            else:
                g.write('\n')
        rownumber = rownumber + 1
        g.close()
```

## Data Preparation(Pandas) 

Refer to [Label for each column of the csv file](https://github.com/streetdrone-home/Autoware/blob/master/ros/src/msgs/autoware_msgs/msg/DetectedObject.msg)
Keep the useful columns, delete others.

Note: all rows are marked with ‘x’ in front, to avoid excel auto delete those blank row, because we want each frame match the corresponding txt file. If there's mothing deteted for that frame, just extract blank txt files.

Each row corresponds to each frame extracted from the rosbag, each detected object need to be separated by one space.

Then change the class labels form text to numbers:
```
Class labels:(starts at 0):
RedLeft
Red
RedRight
GreenLeft
Green
GreenRight
Yellow 
Off
YellowRight 
```

Data Normalization:
Divide x_center and width by image width(1024), y_center and height by image height(768).

***image width and height might be different for different rosbag, depend on the image extracted from the bag file.


Code walk through:

Original bag_to_scv file below with minor modifications, avoid copying the rosbag file once again in the same directory. The original script is quite time consuming duo to redundant back up process. In addition, we only need specific rosbag topic to be extracted in csv format instead for all the rostopics, I did some modifications on that, otherwise it's time consuming and it'll hover unnecessary disk space.
   
```
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
	folder = bagName.rstrip(".bag")
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


	topicName = '/detection/vision_objects/traffic_light'
#	topicName = '/detection/vision_objects/front'


	filename = folder + '/' + topicName.replace( '/', '_slash_') + '.csv'
	with open(filename, 'w+') as csvfile:
		filewriter = csv.writer(csvfile, delimiter = ',')
		firstIteration = True	#allows header row
		for subtopic, msg, t in bag.read_messages(topicName):	# for each instant in time that has data for topicName
			#parse data from this instant, which is of the form of multiple lines of "Name: value\n"
			#	- put it in the form of a list of 2-element lists
			msgString = str(msg)
			msgList = msgString.split( '\n')
			instantaneousListOfData = []
			for nameValuePair in msgList:
				splitPair = nameValuePair.split(':')
				for i in range(len(splitPair)):	#should be 0 to 1
					splitPair[i] = splitPair[i].strip()
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
   
```
Data cleaning process below:

```
   
	#Find the maximum number of columns among all the rows
	
	#with open(folder + "/" + "_slash_detection_slash_vision_objects_slash_front.csv", 'r',encoding = "ISO-8859-1") as temp_f:
	#with open(folder + "/" + "_slash_detection_slash_vision_objects_slash_front.csv", 'r') as temp_f:
	
	#Encoding error solution: try utf-8
	
	with open(folder + "/" + "_slash_detection_slash_vision_objects_slash_traffic_light.csv", 'r') as temp_f:
		# get No of columns in each line
		col_count = [ len(l.split(",")) for l in temp_f.readlines() ]

	### Generate column names  (names will be 0, 1, 2, ..., maximum columns - 1)
	#Blank csv file, rosbag file error.
	if col_count == 0:
		print(folder +" has no detected object.")
		continue 
	#column_names = [i for i in range(max(col_count))] 


        #Hard coding the column index from 1 to 1000, since there're maximum 9 objects can be detected in one frame. It's working but might need some modification. 
	column_names = [i for i in range(1000)] 

	import pandas as pd
	# inside range set the maximum value you can see in "Expected 4 fields in line 2, saw 8"
	# here will be 8 

	#data = pd.read_csv(folder + "/"+"_slash_detection_slash_vision_objects_slash_front.csv",header = None,names=column_names )
	#data.to_csv( folder + "_slash_detection_slash_vision_objects_slash_front.csv", index=False)

	
	#Mixed type data in the same column solved...
	data = pd.read_csv(folder + "/"+"_slash_detection_slash_vision_objects_slash_traffic_light.csv",header = None,names=column_names, engine='python')
	data.loc[0] = ""
	data.to_csv( folder + "_slash_detection_slash_vision_objects_slash_traffic_light.csv", index=False)


	#maximum number of objects detected in one frame:9, still hard coding, may be there's better way...		
	f = pd.read_csv(folder + "_slash_detection_slash_vision_objects_slash_traffic_light.csv", usecols=[0,15,90,91,92,93,95,118,193,194,195,196,198,221,296,297,298,299,301,324,399,400,401,402,404,427,502,503,504,505,507,530,605,606,607,608,610,633,708,709,710,711,713,736,811,812,813,814,816,839,914,915,916,917,919,])

	f.to_csv(folder+"_cleaned.csv", index=False)

    #Model With Traddic Lights
	f["15"] = f["15"].map({'"RedLeft"':0,'"Red"':1,'"RedRight"':2,'"GreenLeft"':3,'"Green"':4,'"GreenRight"':5,'"Yellow"':6,'"Off"':'7','"YellowRight"':8})
	f["118"] = f["118"].map({'"RedLeft"':0,'"Red"':1,'"RedRight"':2,'"GreenLeft"':3,'"Green"':4,'"GreenRight"':5,'"Yellow"':6,'"Off"':'7','"YellowRight"':8})
	f["221"] = f["221"].map({'"RedLeft"':0,'"Red"':1,'"RedRight"':2,'"GreenLeft"':3,'"Green"':4,'"GreenRight"':5,'"Yellow"':6,'"Off"':'7','"YellowRight"':8})
	f["324"] = f["324"].map({'"RedLeft"':0,'"Red"':1,'"RedRight"':2,'"GreenLeft"':3,'"Green"':4,'"GreenRight"':5,'"Yellow"':6,'"Off"':'7','"YellowRight"':8})
	f["427"] = f["427"].map({'"RedLeft"':0,'"Red"':1,'"RedRight"':2,'"GreenLeft"':3,'"Green"':4,'"GreenRight"':5,'"Yellow"':6,'"Off"':'7','"YellowRight"':8})
	f["530"] = f["530"].map({'"RedLeft"':0,'"Red"':1,'"RedRight"':2,'"GreenLeft"':3,'"Green"':4,'"GreenRight"':5,'"Yellow"':6,'"Off"':'7','"YellowRight"':8})
	f["633"] = f["633"].map({'"RedLeft"':0,'"Red"':1,'"RedRight"':2,'"GreenLeft"':3,'"Green"':4,'"GreenRight"':5,'"Yellow"':6,'"Off"':'7','"YellowRight"':8})
	f["736"] = f["736"].map({'"RedLeft"':0,'"Red"':1,'"RedRight"':2,'"GreenLeft"':3,'"Green"':4,'"GreenRight"':5,'"Yellow"':6,'"Off"':'7','"YellowRight"':8})
	f["839"] = f["839"].map({'"RedLeft"':0,'"Red"':1,'"RedRight"':2,'"GreenLeft"':3,'"Green"':4,'"GreenRight"':5,'"Yellow"':6,'"Off"':'7','"YellowRight"':8})

	#Model with Objects 
	#f["15"] = f["15"].map({'"Car"':0,'"Van"':1,'"Pedestrian"':2,'"Motorcyclist"':3,'"Truck"':4,'"Bus"':5,'"Cyclist"':6})
	#f["118"] = f["118"].map({'"Car"':0,'"Van"':1,'"Pedestrian"':2,'"Motorcyclist"':3,'"Truck"':4,'"Bus"':5,'"Cyclist"':6})
	#f["221"] = f["221"].map({'"Car"':0,'"Van"':1,'"Pedestrian"':2,'"Motorcyclist"':3,'"Truck"':4,'"Bus"':5,'"Cyclist"':6})
	#f["324"] = f["324"].map({'"Car"':0,'"Van"':1,'"Pedestrian"':2,'"Motorcyclist"':3,'"Truck"':4,'"Bus"':5,'"Cyclist"':6})
	#f["427"] = f["427"]..map({'"Car"':0,'"Van"':1,'"Pedestrian"':2,'"Motorcyclist"':3,'"Truck"':4,'"Bus"':5,'"Cyclist"':6})


	f["90"] = f["90"]/1224
	f["91"] = f["91"]/1024
	f["92"] = f["92"]/1224
	f["93"] = f["93"]/1024
	
	f["193"] = f["193"]/1224
	f["194"] = f["194"]/1024
	f["195"] = f["195"]/1224
	f["196"] = f["196"]/1024

	f["296"] = f["296"]/1224
	f["297"] = f["297"]/1024
	f["298"] = f["298"]/1224
	f["299"] = f["299"]/1024

	f["399"] = f["399"]/1224
	f["400"] = f["400"]/1024
	f["401"] = f["401"]/1224
	f["402"] = f["402"]/1024

	f["502"] = f["502"]/1224
	f["503"] = f["503"]/1024
	f["504"] = f["504"]/1224
	f["505"] = f["505"]/1024

	f["605"] = f["605"]/1224
	f["606"] = f["606"]/1024
	f["607"] = f["607"]/1224
	f["608"] = f["608"]/1024

	f["708"] = f["708"]/1224
	f["709"] = f["709"]/1024
	f["710"] = f["710"]/1224
	f["711"] = f["711"]/1024

	f["811"] = f["811"]/1224
	f["812"] = f["812"]/1024
	f["813"] = f["813"]/1224
	f["814"] = f["814"]/1024

	f["914"] = f["914"]/1224
	f["915"] = f["915"]/1024
	f["916"] = f["916"]/1224
	f["917"] = f["917"]/1024
	f["0"] = "x"
	
```
Convert from cleaned csv file to txt files.
```
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

	directory_path = folder + '_txt'
	No_of_files = len(os.listdir(directory_path))

```
remove empty txt files. The reason why I do this is for this system, the 'blank' txt files will be filled with enters, which makes it's size bigger than 0,so we cannot use os.path.getsize() to solve this problem.
```

	
	for i in range(No_of_files):
		filename = folder + "_txt/" + str(i) + ".txt"
		with open(filename, 'r') as read_obj:
			# read first character
			one_char = read_obj.read(1)
			# if not fetched then file is empty, 
			if one_char == '\n':
				os.remove(filename)
'''	
    for i in range(No_of_files):
        filename = folder+"_txt/"+str(i)+".txt"
        filesize = os.path.getsize(filename)

        if filesize <= 60:
            os.remove(filename)
'''

print("Done reading all " + numberOfFiles + " bag files.")




```

After the images and txt files are extracted from the bagfile.
These are some useful python files that delete the empty txt files, list out the frames with detected objects. 

Delete_empty.py
```
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

```
Object_detected.py
```
import os

f = open("frames_contain_objects.txt", 'w')

directory_path = 'txt'
No_of_files = len(os.listdir(directory_path))
No_of_files

for i in range(No_of_files):
    filename = "txt/"+str(i)+".txt"
    filesize = os.path.getsize(filename)
    i = ("%04d" % (i,))


    if filesize > 60:
        f.write(os.path.abspath("frames/"+i+".jpg"))
        f.write("\n")

f.close()
```

If the extracted txt file does not match with the extracted images: 
use delay.py to rename the txt files.

delay.py:

```
import os

print("Delay ==> ")
delay = input()
delay = int(delay)

path = "2020-11-18-16-38-31/2020-11-18-16-38-31_txt"
filename = "2020-11-18-16-38-31/2020-11-18-16-38-31-txt"
try:
    os.mkdir(path)
except OSError:
    print ("Creation of the directory %s failed" % path)
else:
    print ("Successfully created the directory %s " % path)


tmp = os.listdir(filename)
No_of_files = len(os.listdir(filename))

for j in range(0,No_of_files):
    index = int(tmp[j].strip(".txt"))
    oldindex = filename + "/"+ tmp[j]
    newindex = path + "/" + str(index-delay) + '.txt'
    os.rename(oldindex,newindex)
    print("Rename: "+tmp[j]+" ==> " +str(index-delay) + '.txt')

os.rmdir(filename)
print("Rename Over.")

```
Some useful command:
Error in mounting and unmount:
```
Sudo fdisk -l
Sudo ntfsfx diskname
```
Compress and decompress:
```
tar  -xzvf filename.tar.gz ~/pathtofile
Tar -xzvf filename.tar.gz

Sudo apt-install ncompress
Compress -v filename/path 
```

Fast Copy:
```
Rsync -ah --progress filename destpath 
```

