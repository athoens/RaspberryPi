import logging
import sched, time, os


def ReadTemperature(path):
    """   Reads the temperature value from a data file for one sensor  """  
    
    # Open the file from the path
    tfile = open(path + "w1_slave") 
    # Read and close the file
    text = tfile.read() 
    tfile.close() 
    # Split the text with new lines (\n) and select the second line. 
    secondline = text.split("\n")[1] 
    # Split the line into words, referring to the spaces, and select the last word. 
    temperaturedata = secondline.split(" ")[-1] 
    # The first two characters are "t=", so get rid of those and convert the temperature from a string to a number. 
    temperature = float(temperaturedata[2:]) 
    # Put the decimal point in the right place and display it. 
    temperature = temperature / 1000 
    return temperature

        
def WriteSensor2File():
    """ Writes the time and temperature value from all sensors into a text file """
    
    # try:
    # text file name is the current date
    fname = (time.strftime("%b%d_%Y") + '.csv')
    exists = os.path.isfile(fname) 
    # open file for appending
    fh = open(fname,'a')
    
    # find all devices sensors
    sensor_count  = 0
    list_sen = []
    # finding all files starting with 28
    for afile in os.listdir("/sys/bus/w1/devices/"):
    #for afile in os.listdir("."):
        if afile.startswith("28-"):
            sensor_count += 1
            list_sen.append(afile)
            
    #print("Found " + str(sensor_count) +" sensors", list_sen)
    
    if not exists: 
        l = ["date and time"] 
        for j in range(0, sensor_count):
            l.append(', ' + list_sen[j])
        s = ''.join(l)
        fh.write(s + '\n')
    
    l = [time.strftime("%Y-%m-%d %H:%M:%S")] 
    for j in range(0, sensor_count):
        path = str(list_sen[j] + "/")
        # path on Raspberry PI
        #path = "/sys/bus/w1/devices/" + str(list_sen[j] + "/")
        temperature = ReadTemperature(path)
        l.append(', ' + str(temperature))
    s = ''.join(l) + '\n'
    
    # temperature = ReadTemperature()
    #s = time.strftime("%Y-%m-%d %H:%M:%S") + ', ' + str(temperature) + '\n'
    fh.write(s)
    fh.close()

    #finally:
    #  sc.enter(5*60, 1, WriteSensor2File, (sc,))
    
def CallScheduler(sc):    
    """ calls the scheduler with a handler """
    
    try: 
        WriteSensor2File()
    finally:
        sc.enter(5*60, 1, CallScheduler, (sc,))
        #sc.enter(10, 1, CallScheduler, (sc,))


def main():
    # log file name is the current date
    flogname = (time.strftime("%b%d_%Y") + '.log')
    #print (time.strftime("%b%d_%Y"))
    logging.basicConfig(filename=flogname, format='%(asctime)s %(message)s',
                        level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

    """ starting the schedule """
    WriteSensor2File()
    
    tstep = 5*60
    s = sched.scheduler(time.time, time.sleep)
    s.enter(tstep, 1, CallScheduler, (s,))
    s.run()       
    
    
if __name__ == '__main__':
    main()
