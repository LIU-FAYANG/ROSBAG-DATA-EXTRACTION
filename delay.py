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
