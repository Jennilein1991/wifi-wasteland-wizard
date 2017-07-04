# WiFi Wasteland Wizard :sparkles:

 
WiFi Wasteland Wizard is a Python script using [Gurobi](http://www.gurobi.com/) linear optimization libraries to calculate an optimal access point distribution for large scale, multi level buildings. It supports extending an existing WiFi installation by suggesting new locations for access points. By defining a list of blacklisted apartments and maximum possible installments per building you can tweak an existing WiFi installation. It will also show the optimal wireless channel per access point, such that channels do not (or less) overlapp.

We deployed around 110 access points following the optimization suggestions and we can say it is gorgeous. You can find our status page with a WiFi map at https://ram.rwth-aachen.de/links/netzstatus#wifimap

[![N](https://www.gurobi.com/documentation/7.0/quickstart_mac/logo.png)](http://www.gurobi.com/)

### Knowledge & Licenses
  - Gurobi is not free. However, you can get an educational license from your University
  - To learn more about the basics of Gurobi we recommend [Praktische Optimierung mit Modellierungssprachen offered by RWTH Aachen University](http://www.wiwi.rwth-aachen.de/go/id/lsqb/file/module-34-47-75)


### Features!
+ Limit the maximum suggested access points per building
  + This will allow you to express less ports in your switching location. For example when every room is connected directly to a switch which is not PoE enabled and you inject power via single PoE injectors or a Midspan unit with less ports than the switch. We are having 24x Port PoE Midspans but 2x48x Port Switches per building.

+ Use a value function which defines what you suggest to be a good coverage
  + We use a value function which will prefere rooms getting 2 or 3 access points in range more than having 1 or 4 (or even more) access points in range

+ Specify which rooms should in no case get an access point
  + This can help when the tenant does not want to have an access point installed

+ Specify how far you estimate your WiFi will range (default 701 cm)
  + To ensure less 2.4 Ghz crosstalk you might change the radios's power, or you want to calculate a 5Ghz wireless coverage map. You can then change how far you expect that a signal will propagate

+ Get a per access point channel suggestion such that the access points' channel will not (or less) overlapp

+ Ensure that rooms which are "too" close to each other do not both get an access point to decrease channel interference

+ **Precise notice about how far the suggested access point distribution is away from the optimal solution (due to the added constraints)**

+ See how many rooms are having how many access points in range:
<pre>
Amount range 0: 0
Amount range 1: 31
Amount range 2: 137
Amount range 3: 164
Amount range 4: 20
Amount range 5: 3
</pre>


### Input
- List of existing access points (room list)
- Map for mapping rooms to buildings
- List for maximum number of access points per building possible
- Blacklist for rooms you do not want to get an access point
- N*N dimensional matrix containing distance from one room to another (in cm)
- Contraint Set adapted to your setup
  
### Output
- List of rooms to be equipped with an access point, sorted by building
- Per room flag (if the room should get an access point)
- Per room/access point wireless channel suggestion
- How close you are to the optimal solution (in %) due to additional constraints (like max access points in one building)
  - **By this you can see if you need more ports in a building to get the best coverage**

You will get an output file with this format:

<pre> ...
[1034]
router=1
existing=1
channel=1

[1035]
router=0
existing=0
channel=-1

[1036]
router=1
existing=0
channel=6
....

How many rooms are seeing how many access points:
Amount range 0: 0
Amount range 1: 31
Amount range 2: 137 <- having 137 rooms are seeing 2 access points in defined range
Amount range 3: 164
Amount range 4: 20
Amount range 5: 3

New access points to setup sorted by building:
buildingA:1034,2228,2111,2122,2115,2240,2056,2022,2255,2243,2336,2008,
buildingB:<perfect coverage achieved>
buildingC:<perfect coverage achieved>
buildingD:1255,1035,1036,
buildingE:<perfect coverage achieved>
buildingF:1254,
</pre>


### Adjusting Contraints and providing ressource files

<pre>
maximalAPNumberInRange = 99 #if you specify a linear impossible contraint, there will be no solution
minimalAPNumberInRange = 1 #same here. Use the value function to specify how many APs you wish to have in range
accessPointRange = 701 #7.01m how far an access point can send its signal
channelRange = 1000 #10m how far an access points' channel can interfere with a different AP on the same channel
neighboursRange = 500 #5m # How far are rooms away from each other to be considered neighbours
</pre>

Edit these files to fit your buildings:
+ app_distance.txt
<pre>
-1001:<b>0.0</b>;300.0;1671.0961........323;
-1002:300.0;<b>0.0</b>;1386.5650........123;
-1005:1671.096191;1386.565063;<b>0.0</b>;300.000488;600.00......;
</pre>
+ app_to_house.txt
<pre>
#house,app
buildingA:2333
buildingA:2153
buildingB:1221
buildingB:1337
buildingC:1234
...
</pre>
+ existing_ap.txt
<pre>
#app,ap-prio <- prio not implemented
2511:
2514:
2311:
...
</pre>
+ max_ports.txt
<pre>
buildingA:20
buildingB:20
buildingC:22
buildingD:10
buildingE:20
buildingF:20
</pre>
+ blacklist.txt
<pre>
2113,comment
2511,
2111,somecomment
1221,
1377,
...
</pre>

### Run it

WiFi Wasteland Wizard uses Python and Gurobi libraries to make the magic happen. You will have to have Python and Gurobi setup before continuing.

In our example we are running the optimization on a Windows machine. MacOS and Linux work as well of course.

```sh
$ python ./wifiDistribution.py
```

### Todo
  + Add more precise room specific calculations
  + Add wall support
  + Add 5 Ghz channel suggestion

License
----
[![N](https://www.python.org/static/community_logos/python-powered-w-100x40.png)](https://www.python.org/)

Apache License 1.0
