# ROSBAG-DATA-EXTRACTION
extract image and bounding box coordinate from rosbag
## Image Extraction 
Copy the compressed file to a certain location and decompress the file:
```
cp ./2b_bag_1113.tar.gz(compressed file name) ~/Documents 
sync
cd Documents/
tar -xzvf 2b_bag_1113.tar.gz  //decompress
```

Build msg types for the rostopic
```
cd Documents/msg_ws/
ls
catkin bulid 
```

Set up: install the image_view package
```
roscd image_view
rosmake image_view
sudo apt-get install mjpegtools
```

Run the roscore and play the recorded data inside the rosbag
```
roscore

rostopic list //get the list of rostopic, in this case, the image_rects contains the frames and boject_detect_front contan the coordinates

rosbag play ~/Documents/2020-11-13-15-33-10.bag 
Rosbag play ~/DOcuments/2020-11-13-15-33-10.bag -s 250  // -s: start point
rqt_image_view 
```

Image Extraction
```
sudo apt install ros-melodic-image-view 
roscd image_view
rosmake image_view 
Sudo apt-get install mjpegtools
roscore
rosbag info (path of the rosbag)

rosbag play (path of the rosbag)
rosrun image_view image_saver _sec_per_frame:=0.1 image:=/camera/image_rects theora       //10 frames per second.
```

## Convert rosbag topics to csv files

Download bag_to_csv.py from [This Site](http://www.clearpathrobotics.com/assets/guides/kinetic/ros/Converting%20ROS%20bag%20to%20CSV.html)

The python file will convert every rostopic into csv files.
Choose the one with name: _slash_detection_slash_vision_objects_slash_front.csv, which contains the coordinates of the bounding box:(in yolo format)

Delete other files.

Note: Do not convert the csv file into a xsl file, otherwise later the csv_to_txt file won’t work.
Data preparation can be done with excel.

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

## Data Preparation 

Refer to [Label for each column of the csv file](https://github.com/streetdrone-home/Autoware/blob/master/ros/src/msgs/autoware_msgs/msg/DetectedObject.msg)
Keep the useful columns, delete others.

Note: those 6602 rows are marked with ‘x’ in front, to avoid excel auto delete those blank row, because we want each frame match the corresponding txt file.

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

The prepared dataset can refer to the DATA.csv file inside csv_to_txt folder.

