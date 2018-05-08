#Liam Dick
#Recursive BFS code loosely based on algorithm written by Neelam Yadav
#This code creates a directed net that represents a simple air
#travel network. Vertices represent airports, and edges represent flights.
#A weight has been added to each edge to represent flight time, so that the
#final output will display the path time.
#Another weight has been added to each edge to represent flight price, so
#that the final output will display the path price.

#This version attempts to make each edge an object with a weight
 
from collections import defaultdict
from tkinter import *

#This class represents a time as a specific object and associated time zone
class Time:

    def __init__(self, milTime, zone): #NOTE: milTime '0040' must be passed in as '40'
        self.min = milTime % 100 #minutes past the hour
        self.hrs = milTime // 100 #hours past the day
        if zone == "EST": #timezone assignments
            self.zone = -5
        elif zone == "CST":
            self.zone = -6
        elif zone == "MST":
            self.zone = -7
        elif zone == "PST":
            self.zone = -8
        elif zone == "GMT":
            self.zone = 0

    def getHrs(self):
        return self.hrs
    def getMin(self):
        return self.min
    def getZone(self):
        return self.zone
    def getTime(self):
        return (self.getHrs() * 100) + self.getMin()

    def getGMT(self): #Gets the GMT
        hrs = self.getHrs() - self.getZone()
        if hrs >= 24: #Rollover
            hrs -= 24
        return (hrs * 100) + self.getMin()
    def getHrsGMT(self): #Gets the hour in GMT
        return self.getGMT() // 100
    def getTimeGMT(self): #gets the GMT as a time object
        return Time(self.getGMT(),"GMT")

    #returns an integer representing the elapsed time between this object and
    #another time object (endTime)
    def timeUntil(self, endTime): 
        hrsOut = 0
        minOut = 0
        if endTime.getHrsGMT() < self.getHrsGMT(): #Rolls over hour difference
            hrsOut = endTime.getHrsGMT() - self.getHrsGMT() + 24
        else: #Simple hour difference
            hrsOut =  endTime.getHrsGMT() - self.getHrsGMT()
        if endTime.getMin() < self.getMin(): #Rolls over minute difference
            minOut = endTime.getMin() - self.getMin() + 60
            hrsOut -= 1 #reduces hour count if rolled over
        else:
            minOut = self.getMin() - endTime.getMin()
        return (hrsOut * 100) + minOut

    #returns an integer representing the elapsed time between two integers
    #representing specific military times (time1,time2)
    @staticmethod
    def addTime(time1,time2): #takes two integers in time format and returns the summed time
        hrsOut = (time1 // 100) + (time2 // 100)
        minOut = (time1 % 100) + (time2 % 100)
        if minOut > 60:
            hrsOut += 1
            minOut -= 60
        return (hrsOut * 100) + minOut
            
        
#This class represents a directed net using adjacency list representation
#TRANSLATION: stores a vertex, and what that vertex is connected (adjacent) to
class Network:
  
    def __init__(self,canvas):
        self.canvas = canvas #sets which canvas to draw the network on
        self.APCount = 0 #No. of vertices (Airports)
        self.net = defaultdict(list) #default dictionary to store net
        self.flights = defaultdict(list) #default dictionary to store flights
        self.airports = {}
        #TRANSLATION: Uses a key-based list to add multiple values to the same
        #list entry, that way it can store the list element with an associated
        #recall value

    #returns the Airport object stored in the airports dictionary at the position 'rank'
    def getAP(self, rank):
        return self.airports[rank]

    #function to add an airport to the network
    def addAirport(self,airport, yJustify = -2, xJustify = 0):
        airport.setRank(self.APCount) #sets what value the airport will have in pathfinding
        self.airports[self.APCount] = airport #adds airport to airport dictionary using rank as key 
        self.APCount += 1 #Adds another airport to the airport counter
        #Graphic commands here
        self.canvas.create_oval(airport.getX()-3,airport.getY()-3,
                                airport.getX()+3,airport.getY()+3,
                                fill = "blue violet") #Creates airport dot
        self.canvas.create_text(airport.getX()- (6 * xJustify),
                                airport.getY()- (6 * yJustify),
                                fill = "white",
                                text = airport.getCode(),
                                font = "Fixedsys 10 bold") #Creates airport canvas label
    #function to add a flight to the network
    def addFlight(self,flight):
        self.net[(flight.getDept()).getRank()].append(flight.getArrv().getRank()) #stores flight in net
        self.flights[(flight.getDept()).getRank()].append(flight) #stores flight object in flights
        #graphic commands here
        self.canvas.create_line(flight.getDept().getX(),
                                flight.getDept().getY(),
                                flight.getArrv().getX(),
                                flight.getArrv().getY(),
                                width = 1,
                                fill = "blue")
    #function to create a new airport and add it to net
    def newAirport(self, x, y, code, tzone, name):
        airport = self.Airport(x, y, code, tzone, name)
        self.addAirport(airport)
    #function to create a new flight and add it to the net
    def newFlight(self, deptR, arrvR, dTime, aTime, price):
        dept = self.getAP(deptR) #uses rank call
        arrv = self.getAP(arrvR)
        flight = self.Flight(dept, arrv, dTime, aTime, price)
        self.addFlight(flight)

    #recursive utility function to get paths
    def findAllPathsUtil(self, start, destination, visited, path, paths, pathF, pathsF): 
        # Mark the current node as visited and store in path
        visited[start]= True
        path.append(start)
        #If current vertex is same as destination, then append path to paths, and pathF to pathsF
        if start == destination:
            paths.append(path[:])
            pathsF.append(pathF[:])
        else:
            #If current vertex is not destination
            #Recur for all the vertices adjacent to this vertex
            iPos = 0 #integer that moves with i in following loop
            for i in self.net[start]: #for all airport ranks adjacent to this one
                if visited[i]==False: #if the path has not been here yet
                    pathF.append(self.flights[start][iPos]) #append the flight in the same position in
                                                            #flights[start] as i is in the net to pathF
                    self.findAllPathsUtil(i, destination, visited, path, paths, pathF, pathsF) #recur
                    pathF.pop() #Remove current flight from pathF[]
                iPos += 1 #iterate integer that tracks loop
        #Remove current vertex from path[] and mark it as unvisited
        path.pop()
        visited[start]= False
    #returns all paths from startAP to destination AP
    def findAllPaths(self, startAP, destinationAP):
        #Mark all the vertices as not visited
        visited =[False]*(self.APCount)
        #Create an array to store a series of rank paths
        pathsR = []
        #Create an array to store a rank path
        pathR = []
        #create an array to store a series of flights
        path = []
        #create an array to store a series of flight paths
        paths = []
        #Call the recursive helper function to print all paths
        self.findAllPathsUtil(startAP.getRank(), destinationAP.getRank(), visited,
                              pathR, pathsR, path, paths)
        #returns an array of paths
        return paths
    
    #Finds the time along a path that is in the air
    def findAirTime(self,path):
        aElap = 0
        for flight in path: #adds elapsed time of flight to aElap for every flight
            aElap = Time.addTime(aElap,flight.getElap())
        return aElap
    #Finds the time along a path that is on the ground
    def findGroundTime(self, path):
        gElap = 0
        for i in range(len(path) - 2): #layover time
            gElap = Time.addTime(gElap,
                                 path[i].getArrvGMT().timeUntil(path[i + 1].getDeptGMT()))
        return gElap
    
    #find how long a path takes and returns an int
    def findPathTime(self, path):
        return Time.addTime(self.findAirTime(path),self.findGroundTime(path))
    
    #returns the fastest path from startAP to destination AP as a list of flights
    def findFastPath(self, startAP, destinationAP):
        paths = self.findAllPaths(startAP, destinationAP) #gets and stores all paths from startAP to destAP
        #Set the first entry as the basis for comparison
        fastPath = paths[0]
        fastTime = self.findPathTime(paths[0])
        #loops through list of paths
        for path in paths:
            #loops through flights in path
            pathTime = self.findPathTime(path)
            #changes fath if this route is the fastest
            if pathTime < fastTime:
                fastTime = pathTime
                fastPath = path[:]
        return fastPath

    #Finds the time along a path that is in the air
    def findPrice(self,path):
        price = 0
        for flight in path:
            price += flight.getPrice()
        return price
    #returns the fastest path from startAP to destination AP as a list of flights
    def findCheapPath(self, startAP, destinationAP):
        paths = self.findAllPaths(startAP, destinationAP)#gets and stores all paths from startAP to destAP
        #Set the first entry as the basis for comparison
        cheapPath = paths[0]
        cheapPrice = self.findPrice(paths[0])
        #loops through list of paths
        for i in range(len(paths)):
            path = paths[i]
            #checks if path is dead end, continues if it is
            if (path[len(path) - 1].getArrv(). getCode()
                !=
                destinationAP.getCode()):
                continue
            #loops through flights in path
            pathPrice = self.findPrice(path)
            #changes fath if this route is the fastest
            if pathPrice < cheapPrice:
                cheapPrice = pathPrice
                cheapPath = path[:]
        return cheapPath

    #This helper class represents an flight
    class Flight:

        def __init__(self, dept, arrv, dTime, aTime, price): #NOTE: dtime and atime are INT
            self.dept = dept #departure airport
            self.arrv = arrv #arrival airport
            self.dTime = Time(dTime,self.dept.getTZone()) #flight departure time object
            self.aTime = Time(aTime,self.dept.getTZone()) #flight arrival time object
            self.price = price #flight price in USD

        def getDeptGMT(self): #returns the time the plane leaves in GMT as a time object
            return self.dTime.getTimeGMT()

        def getArrvGMT(self): #returns the time the plane arrives in GMT as a time object
            return self.aTime.getTimeGMT()
        
        def getDeptLoc(self): #returns the time the plane leaves in local time as a time object
            return self.dTime

        def getArrvLoc(self): #returns the time the plane arrives in local time as a time object
            return self.aTime

        def getDeptTime(self): #returns the time the plane leaves in local time as an int
            return self.dTime.getTime()

        def getArrvTime(self): #returns the time the plane arrives in local time as an int
            return self.aTime.getTime()

        def getElap(self):
            return self.getDeptGMT().timeUntil(self.getArrvGMT())

        def getDept(self): #returns the departure airport
            return self.dept

        def getArrv(self): #returns the arrival airport
            return self.arrv

        def getPrice(self): #returns price of the flight
            return self.price

    #This helper clas represents an airport
    class Airport:

        def __init__(self, x, y, code, tzone, name):
            self.x = x #stores x coord for map
            self.y = y #stores y coord for map
            self.rank = -1 #Stores rank of airport for pathfinding
            self.code = code #stores three character airport code
            self.name = name #stores the name of the airport
            self.tzone = tzone #stores timezone the airport is in as a string

        def setRank(self,rank): #sets the rank of the airport
            self.rank = rank

        def getRank(self): #returns rank of the airport
            return self.rank

        def getX(self): #returns x coord of the airport
            return self.x
        
        def getY(self): #returns y coord of the airport
            return self.y
        
        def getCode(self): #returns code of the airport
            return self.code

        def getName(self): #returns name of the airport
            return self.name

        def getTZone(self): #returns timezone of the airport as a string
            return self.tzone

#END GRAPH CLASS
#Create a window to display the net using the methods above
class NetDisplay():
    def __init__(self):
        window = Tk() #Creates window
        window.title("Airline Trip Planner")
        self.canvas = Canvas(window, width = 800, height = 600, bg = "black")
        self.canvas.pack()
        self.drawUS(self.canvas) #Draws background map of US
        
        self.n = Network(self.canvas)
        #initialize airpots with newAirport and newFlight functions
        # def newAirport(self, x, y, code, tzone, name):
        #Airports are initialized here, broken up into four different zones based on
        #the hub airport servicing that zone. Comments for 'phantom' airports allows
        #the author to keep track of overlapping areas of service. The commented number
        #at the end of each call of newAirport indicates the rank of that airport in
        #the airport dictionary of self.n so that these numbers can be readily available
        #for newFlight calls when authoring. Further organization tags and indicators
        #are used in conjunction with a helper function to more efficently store many
        #flights
        #SLC ZONE
        #WEST (All PST)
        self.n.newAirport(48,96,"PTL","PST","Portland") #0
        self.n.newAirport(32,272,"SFO","PST","San Franscico") #1
        self.n.newAirport(64,352,"LAX","PST","Los Angeles")  #2 BIG
        self.n.newAirport(128,320,"LAS","PST","Las Vegas") #3 FAST
        #HUB
        self.n.newAirport(192,240,"SLC","MST","Salt Lake City") #4
        #SMALL
        self.n.newAirport(80,48,"SEA","PST","Seattle") #5 
        self.n.newAirport(208,112,"HLN","MST","Helena") #6 
        self.n.newAirport(144,160,"BSE","MST","Boise")#7 
        #EAST
        self.n.newAirport(288,272,"DEN","MST","Denver") #8
        self.n.newAirport(160,384,"PNX","MST","Phoenix") #9
        self.n.newAirport(48,240,"SCM","PST","Sacramento") #10
        #DFW ZONE
        #SOUTH
        self.n.newAirport(512,464,"MSY","CST","New Orleans")#11
        #Denver #8
        self.n.newAirport(640,496,"TPA","EST","Tampa")  #12 BIG
        self.n.newAirport(336,464,"SAT","CST","San Antonio") #13 FAST
        #HUB
        self.n.newAirport(400,416,"DFW","CST","Dallas - Fort Worth") #14
        #SMALL
        self.n.newAirport(384,336,"OKC","CST","Oklahoma City") #15 
        self.n.newAirport(240,432,"ELP","CST","El Paso") #16 
        self.n.newAirport(400,256,"LNK","CST","Lincoln")#17 
        #NORTH
        self.n.newAirport(256,352,"SAF","MST","Santa Fe") #18
        self.n.newAirport(432,272,"MCI","CST","Kansas City") #19
        self.n.newAirport(592,384,"ATL","EST","Atlanta") #20
        #ORD ZONE
        #SECT 1
        self.n.newAirport(448,160,"MSP","CST","Minneapolis - Saint Paul") #21
        self.n.newAirport(496,288,"STL","CST","St. Louis") #22
        #Atlanta #20 # BIG
        self.n.newAirport(592,208,"DTW","EST","Detroit") #23 FAST
        #HUB
        self.n.newAirport(528,224,"ORD","CST","Chicago") #24
        #SMALL
        self.n.newAirport(624,208,"CLE","EST","Cleveland") #25 
        self.n.newAirport(448,224,"DSM","CST","Des Moines") #26 
        self.n.newAirport(656,160,"BUF","EST","Buffalo")#27
        #SECT 2
        #Kansas City #19
        self.n.newAirport(560,336,"BNA","CST","Nashville") #28
        self.n.newAirport(656,352,"CLT","EST","Charlotte") #29
        #JFK ZONE
        #SOUTH
        #Atlanta #20
        #Charlotte #29
        self.n.newAirport(688,528,"MIA","EST","Miami")  #30 BIG
        self.n.newAirport(688,272,"DCA","EST","Washington D.C.") #31 FAST
        #HUB
        self.n.newAirport(720,208,"JFK","EST","New York") #32
        #SMALL
        self.n.newAirport(656,224,"PIT","EST","Pittsburgh") #33
        #Cleveland #25 
        #Buffalo #27 
        #NORTH
        self.n.newAirport(768,160,"BOS","EST","Boston") #34
        #Detroit #23
        #Atlanta #20

        #Calls a helper function four times to create four hub zones using
        #comment organization system to keep track of rank
        self.hubZone(0,1,2,3,4,5,6,7,8,9,10)
        self.hubZone(11,8,12,13,14,15,16,17,18,19,20)
        self.hubZone(21,22,20,23,24,25,26,27,19,28,29)
        self.hubZone(20,29,30,31,32,33,25,27,34,23,20)

        #Creates commuter flights between nearby airports at a steep price
        #Vegas - LA 
        self.n.newFlight(3,2,915,1025,160)
        self.n.newFlight(2,3,915,1030,160)
        #New Orleans - Tampa 
        self.n.newFlight(11,12,915,1025,160)
        self.n.newFlight(12,11,915,1030,160)
        #Charlotte - DC 
        self.n.newFlight(31,29,915,1025,160)
        self.n.newFlight(29,31,915,1030,160)
        #Miami - Tampa 
        self.n.newFlight(12,30,920,1005,160)
        self.n.newFlight(30,12,920,1005,160)

        #Creates long distance flights between hub airports
        #Due to the frequency of time zone chances on inter-hub flights,
        #manual entry was required for these flights, as a helper function
        #would not produce the required particulars
        #SLC
        #Overnight
        self.n.newFlight(4,32,100,830,125) #530 to 430
        self.n.newFlight(4,24,145,625,125) #340
        self.n.newFlight(4,14,200,530,125) #230
        #830
        self.n.newFlight(4,32,900,1630,125) #530 to 430
        self.n.newFlight(4,24,945,1425,125) #340
        self.n.newFlight(4,14,1000,1330,125) #230
        #1030
        self.n.newFlight(4,32,1100,1830,125) #530 to 430
        self.n.newFlight(4,24,1145,1625,125) #340
        self.n.newFlight(4,14,1200,1530,125) #230
        #1400
        self.n.newFlight(4,32,1400,2130,125) #530 to 430
        self.n.newFlight(4,24,1445,1925,125) #340
        self.n.newFlight(4,14,1400,1730,125) #230
        #1630
        self.n.newFlight(4,32,1700,30,125) #530 to 430
        self.n.newFlight(4,24,1745,2225,125) #340
        self.n.newFlight(4,14,1700,2130,125) #230
        #1845
        self.n.newFlight(4,32,1800,130,125) #530 to 430
        self.n.newFlight(4,24,1945,25,125) #340
        self.n.newFlight(4,14,1900,2230,125) #230
        #JFK
        #Overnight
        self.n.newFlight(32,4,100,330,125) #530 to 430
        self.n.newFlight(32,14,145,425,125) #340
        self.n.newFlight(32,24,200,430,125) #230
        #830
        self.n.newFlight(32,4,900,1130,125) #530 to 430
        self.n.newFlight(32,14,945,1225,125) #340
        self.n.newFlight(32,24,1000,1230,125) #230
        #1030
        self.n.newFlight(32,4,1100,1330,125) #530 to 430
        self.n.newFlight(32,14,1145,1425,125) #340
        self.n.newFlight(32,24,1200,1430,125) #230
        #1400
        self.n.newFlight(32,4,1400,1630,125) #530 to 430
        self.n.newFlight(32,14,1445,1725,125) #340
        self.n.newFlight(32,24,1400,1630,125) #230
        #1630
        self.n.newFlight(32,4,1700,1930,125) #530 to 430
        self.n.newFlight(32,14,1745,2025,125) #340
        self.n.newFlight(32,24,1700,2030,125) #230
        #1845
        self.n.newFlight(32,4,1800,2030,125) #530 to 430
        self.n.newFlight(32,14,1945,2225,125) #340
        self.n.newFlight(32,24,1900,2230,125) #230
        #DFW
        #Overnight
        self.n.newFlight(14,32,100,630,125) #530 to 430 done
        self.n.newFlight(14,4,145,425,125) #340 
        self.n.newFlight(14,24,200,430,125) #230 
        #830
        self.n.newFlight(14,32,900,1430,125) #530 to 430
        self.n.newFlight(14,4,945,1225,125) #340
        self.n.newFlight(14,24,1000,1230,125) #230
        #1030
        self.n.newFlight(14,32,1100,1630,125) #530 to 430
        self.n.newFlight(14,4,1145,1425,125) #340
        self.n.newFlight(14,24,1200,1430,125) #230
        #1400
        self.n.newFlight(14,32,1400,1930,125) #530 to 430
        self.n.newFlight(14,4,1445,1725,125) #340
        self.n.newFlight(14,24,1400,1630,125) #230
        #1630
        self.n.newFlight(14,32,1700,2230,125) #530 to 430
        self.n.newFlight(14,4,1745,2025,125) #340
        self.n.newFlight(14,24,1700,2030,125) #230
        #1845
        self.n.newFlight(14,32,1900,30,125) #530 to 430
        self.n.newFlight(14,4,1945,2225,125) #340
        self.n.newFlight(14,24,1900,2230,125) #230
        #ORD
        #Overnight
        self.n.newFlight(24,4,100,630,125) #530 to 430
        self.n.newFlight(24,32,145,425,125) #340
        self.n.newFlight(24,14,200,430,125) #230
        #830
        self.n.newFlight(24,4,900,1430,125) #530 to 430
        self.n.newFlight(24,32,945,1225,125) #340
        self.n.newFlight(24,14,1000,1230,125) #230
        #1030
        self.n.newFlight(24,4,1100,1630,125) #530 to 430
        self.n.newFlight(24,32,1145,1425,125) #340
        self.n.newFlight(24,14,1200,1430,125) #230
        #1400
        self.n.newFlight(24,4,1400,1930,125) #530 to 430
        self.n.newFlight(24,32,1445,1725,125) #340
        self.n.newFlight(24,14,1400,1630,125) #230
        #1630
        self.n.newFlight(24,4,1700,2230,125) #530 to 430
        self.n.newFlight(24,32,1745,2025,125) #340
        self.n.newFlight(24,14,1700,2030,125) #230
        #1845
        self.n.newFlight(24,4,1900,30,125) #530 to 430
        self.n.newFlight(24,32,1945,2225,125) #340
        self.n.newFlight(24,14,1900,2230,125) #230
        
        

        #Makes a frame
        frame1 = Frame(window)
        frame1.pack()
        #Adds labels to frame
        #Label Row 1
        labelStart = Label(frame1, text = "Starting Airport")
        labelDest = Label(frame1, text = "Destination Airport")
        labelOption = Label(frame1, text = "Route Options")
        labelDept = Label(frame1, text = "Depature Time: ")
        labelStart.grid(row = 1, column = 1)
        labelDest.grid(row = 1, column = 3)
        labelOption.grid(row = 1, column = 5)
        labelDept.grid(row = 1, column = 7)
        #Label Row 2
        labelPrice = Label(frame1, text = "Trip Price: ")
        labelTime = Label(frame1, text = "Trip Duration: ")
        labelArrv = Label(frame1, text = " Arrival Time: ")
        labelPrice.grid(row = 2, column = 3)
        labelTime.grid(row = 2, column = 5)
        labelArrv.grid(row = 2, column = 7)
        #Output fields Row 2
        self.priceOut = StringVar()
        self.timeOut = StringVar()
        self.deptOut = StringVar()
        self.arrvOut = StringVar()
        labelPriceOut = Label(frame1, textvariable = self.priceOut)
        labelTimeOut = Label(frame1, textvariable = self.timeOut)
        labelDeptOut = Label(frame1, textvariable = self.deptOut)
        labelArrvOut = Label(frame1, textvariable = self.arrvOut)
        labelPriceOut.grid(row = 2, column = 4)
        labelTimeOut.grid(row = 2, column = 6)
        labelDeptOut.grid(row = 1, column = 8)
        labelArrvOut.grid(row = 2, column = 8)

        #Button
        btProcess = Button(frame1, text = "       Find Flight Path       ", command = self.process)
        btProcess.grid(row = 2, column = 1, columnspan = 2)

        #Option Dropdown menu
        Olist = ["Cheapest Path", "Fastest Path"] #TestList
        self.option = StringVar(window)
        options = OptionMenu(frame1,self.option,*Olist) #self.option.get() tells what string this is
        options.grid(row = 1, column = 6)

        #Airport Dropdown Menus
        Alist = [] #makes an empty list
        for i in range(len(self.n.airports)):
            Alist.append(self.n.airports[i].getName()) #Will generate Alist
        #Alist = ["Kennedy","OHara","LAX"] #TestList
        self.start = StringVar(window)
        self.end = StringVar(window)
        starts = OptionMenu(frame1,self.start,*Alist) #self.start.get() tells what string this is
        starts.grid(row = 1, column = 2)
        ends = OptionMenu(frame1,self.end,*Alist) #self.end.get() tells what string this is
        ends.grid(row = 1, column = 4)

    def process(self): #Processes buttons
        destAP = 0
        startAP = 0
        if self.start.get() == self.end.get(): #if destination and start are the same
                self.priceOut.set("Error!")
                self.timeOut.set("Error!")
                return
        path = 0
        #translates dropdown inputs to airport objects by searching airport
        #array for matching names
        for i in range(len(self.n.airports) - 1): 
            if self.n.airports[i].getName() == self.start.get():
                startAP = self.n.airports[i]
                continue
            if self.n.airports[i].getName() == self.end.get():
                destAP = self.n.airports[i]
                continue
        if self.option.get() == "Fastest Path":
            path = self.n.findFastPath(startAP,destAP)
            time = self.n.findPathTime(path)
            self.timeOut.set(str(time // 100) + ":" + str(time % 100))
            price = self.n.findPrice(path)
            self.priceOut.set("$" + str(price))
            self.deptOut.set(str((path[0].getDeptTime()) // 100) +":"+
                             str((path[0].getDeptTime()) % 100))
            self.arrvOut.set(str((path[len(path)-1].getArrvTime()) // 100) +":"+
                             str((path[len(path)-1].getArrvTime()) % 100))
            self.drawPath(self.canvas, path)
        if self.option.get() == "Cheapest Path":
            path = self.n.findCheapPath(startAP,destAP)
            time = self.n.findPathTime(path)
            self.timeOut.set(str(time // 100) + ":" + str(time % 100))
            price = self.n.findPrice(path)
            self.priceOut.set("$" + str(price))
            self.deptOut.set(str((path[0].getDeptTime()) // 100) +":"+
                             str((path[0].getDeptTime()) % 100))
            self.arrvOut.set(str((path[len(path)-1].getArrvTime()) // 100) +":"+
                             str((path[len(path)-1].getArrvTime()) % 100))
            self.drawPath(self.canvas, path)
            

    def drawUS(self, canvas): #Draws background map of US
        #Connect-the-dots style plot of an outline of the contiguous US
        plot = [ [3,2],[5,3],[5,2],[21,5],[27,5],[31,6],
                 [29,8],[31,8],[32,7],[35,7],[36,8],[34,8],[
                 33,10],[33,13],[34,14],[34,11],[36,8],[
                 37,9],[36,11],[37,10],[38,12],[37,13],[
                 37,14],[38,14],[41,11],[41,10],[43,10],[
                 43,8],[46,7],[47,6],[47,3],[48,4],[49,3],[
                 50,6],[47,10],[48,10],[48,11],[49,10],[
                 49,11],[46,12,47,12],[43,13],[46,14],[
                 45,16],[45,18],[44,16],[44,17],[45,20],[
                 41,26],[41,28],[43,32],[43,34],[42,35],[
                 40,32],[40,30],[38,29],[37,30],[33,29],[
                 33,30],[34,31],[28,30],[24,33],[25,35],[
                 22,35],[15,27],[14,27],[13,28],[7,25],[
                 5,25],[5,23],[2,21],[1,12], [3,2]]
        for i in range(len(plot) - 1):
            self.drawLine(canvas,
                          plot[i][0],
                          plot[i][1],
                          plot[i + 1][0],
                          plot[i + 1][1],
                          16, "gray26", "map")

    #Draws the route of a path of flights
    def drawPath(self, canvas, path):
        canvas.delete("path") #deletes previously drawn path
        for flight in path:
            self.drawLine(canvas,
                          flight.getDept().getX(),
                          flight.getDept().getY(),
                          flight.getArrv().getX(),
                          flight.getArrv().getY(),
                          1, "cyan", "path")

    #Simplifies create_line for use with grid system
    def drawLine(self, canvas, x1,y1,x2,y2, mult, fill, tag):
        canvas.create_line(x1 * mult, y1 * mult, x2 * mult, y2 * mult,
                           width = 3, fill = fill, tag = tag)

    #Creates a helper function that produces many hub flights at a low rate
    def hubZone(self,x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10):
        #HUB SECT 1
        #HUB Overnight (Messy)
        #Terrible hours make overnight flights cheaper
        self.n.newFlight(x4,x0,50,205,40)#215 #Appox. elapsed flight time
        self.n.newFlight(x4,x1,5,225,40) #220
        self.n.newFlight(x4,x2,15,125,40) #210 BIG
        self.n.newFlight(x4,x3,10,140,40) #130
        #HUB RedEye (500 - 820(720 PST))
        self.n.newFlight(x0,x4,530,820,60) #150
        self.n.newFlight(x1,x4,500,800,60) #155
        self.n.newFlight(x2,x4,525,820,60) #155 BIG
        self.n.newFlight(x3,x4,550,810,60) #120
        self.n.newFlight(x5,x4,545,805,60) #200 SM
        self.n.newFlight(x6,x4,535,815,60) #140 SM
        self.n.newFlight(x7,x4,545,805,60) #120 SM
        #HUB AM (830 - 1115 (1015 PST))
        self.n.newFlight(x4,x0,850,1005,60)#215
        self.n.newFlight(x4,x1,830,955,60) #220
        self.n.newFlight(x4,x2,835,945,60) #210 BIG
        self.n.newFlight(x4,x3,830,900,60) #130
        #HUB Nooners(1030 - 1350 (1250 PST))
        self.n.newFlight(x0,x4,1020,1310,60)
        self.n.newFlight(x1,x4,1030,1330,60) 
        self.n.newFlight(x2,x4,1045,1345,60)
        self.n.newFlight(x3,x4,1050,1350,60) 
        #HUB SECT 2
        #HUB Early Afternoon (1400 - 1610)
        self.n.newFlight(x4,x8,1420,1550,60) #130
        self.n.newFlight(x4,x2,1400,1510,60) #210 BIG
        self.n.newFlight(x4,x9,1415,1600,60) #145
        self.n.newFlight(x4,x10,1410,1610,60)#200
        #HUB Late Afternoon (1630 - 1830)
        self.n.newFlight(x8,x4,1650,1830,60) #140
        self.n.newFlight(x2,x4,1530,1825,60) #155 BIG
        self.n.newFlight(x9,x4,1640,1820,60) #140
        self.n.newFlight(x10,x4,1630,1815,60)#145
        #HUB PM (1845 - 2050)
        self.n.newFlight(x4,x8,1900,2030,60) #130
        self.n.newFlight(x4,x2,1845,1950,60) #210 BIG
        self.n.newFlight(x4,x9,1855,2040,60) #145
        self.n.newFlight(x4,x10,1850,2050,60)#200
        #HUB LateNight (2100 - 2300)
        self.n.newFlight(x8,x4,2050,2230,60) #140
        self.n.newFlight(x2,x4,2005,2300,60) #155 BIG
        self.n.newFlight(x9,x4,2055,2235,60) #140
        self.n.newFlight(x10,x4,2110,2255,60)#145
        self.n.newFlight(x4,x5,2045,2305,60) #200 SM
        self.n.newFlight(x4,x6,2035,2315,60) #140 SM
        self.n.newFlight(x4,x7,2045,2305,60) #120 SM
        
        
NetDisplay()
 

