import os

print("Delay ==> ")
delay = input()
delay = int(delay)

path = "delayed"

try:
    os.mkdir(path)
except OSError:
    print ("Creation of the directory %s failed" % path)
else:
    print ("Successfully created the directory %s " % path)

filename = "text/"
tmp = os.listdir(filename)
No_of_files = len(os.listdir(filename))

for j in range(0,No_of_files):
    index = int(tmp[j].strip(".txt"))
    oldindex = filename + tmp[j]
    newindex = "delayed/" + str(index-delay) + '.txt'
    os.rename(oldindex,newindex)
    print("Rename: "+tmp[j]+" ==> " +str(index-delay) + '.txt')

os.remove("text")
print("Rename Over.")