#!/bin.sh
CARS="car1 car2 car3"

while true
do
clear
rm -f /tmp/scoreboard
for file in $CARS
do
	/bin/echo -n $file " " >> /tmp/scoreboard
	tail -1 $file >> /tmp/scoreboard
done
sort -n -k 8 -t ' ' /tmp/scoreboard | awk -f scoreboard.awk
sleep 1
done
