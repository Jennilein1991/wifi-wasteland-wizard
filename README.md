# WiFi Wasteland Wizard

[![N](https://www.python.org/static/community_logos/python-powered-w-100x40.png)](https://www.python.org/)

WiFi Wasteland Wizard is a Python script using [Gurobi](http://www.gurobi.com/) linear optimization libraries to calculate an optimal access point distribution for large scale, multi level buildings. It supports extending an existing WiFi installation by suggesting new locations for access points. By defining a list of blacklisted apartments and maximum possible installments per building you can tweak an existing WiFi installation. It will also show the optimal wireless channel per access point, such that channels do not (or less) overlapp.

We deployed around 110 access point following the optimization suggestions and we can say it is gorgeous. You can find our status page with a WiFi map at https://ram.rwth-aachen.de/links/netzstatus#wifimap

[![N](https://www.gurobi.com/documentation/7.0/quickstart_mac/logo.png)](http://www.gurobi.com/)

### Knowlede & Licenses
  - Gurobi is not free. However, you can get an educational license from your University
  - To learn more about the basics of Gurobi we recommend [Praktische Optimierung mit Modellierungssprachen offered by RWTH Aachen University](http://www.wiwi.rwth-aachen.de/go/id/lsqb/file/module-34-47-75)

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

You will get an output file with this format:
> ...
>[1034]
>router=1
>existing=1
>channel=1

>[1035]
>router=0
>existing=0
>channel=-1

>[1036]
>router=1
>existing=0
>channel=6
> ....


# Features!

  + Limit the maximum suggested access points per building
  -- This will allow you to express less ports in your switching location. For example when every room is connected directly to a switch which is not PoE enabled and you inject power via single PoE injectors or a Midspan unit with less ports than the switch. We are having 24x Port PoE Midspans but 2x48x Port Switches per building.

  + Use a value function which defines what you suggest to be a good coverage
  -- We use a value function which will prefere rooms getting 2 or 3 access points in range more than having 1 or 4 (or even more) access points in range

  + Specify which rooms should in no case get an access point
  -- This can help when the tenant does not want to have an access point installed

  + Specify how far you estimate your WiFi will range (default 5 meters)
  -- To ensure less 2.4 Ghz crosstalk you might change the radios's power, or you want to calculate a 5Ghz wireless coverage map. You can then change how far you expect that a signal will propagate

  + Get a per access point channel suggestion such that the access points' channel will not (or less) overlapp

  + Ensure that rooms which are "too" close to each other do not both get an access point to decrease channel interference


# Installation

WiFi Wasteland Wizard uses Python and Gurobi libraries to make the magic happen. You will have to have Python and Gurobi setup before continuing.

In our example we are running the optimization on a Windows machine. MacOS and Linux work as well of course.

```sh
$ python ./wifiDistribution.py
```

# Todo
  + Add more precise room specific calculations
  + Add wall support
  + Add 5 Ghz channel suggestion

License
----

Apache License 1.0
