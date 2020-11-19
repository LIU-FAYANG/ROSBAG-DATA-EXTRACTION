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