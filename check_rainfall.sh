#!/bin/bash

while getopts “:w:c:” opt; do
  case $opt in
    w) warn=$OPTARG ;;
    c) crit=$OPTARG ;;
  esac
done

aweekago=$(date -d "7 days ago" +%Y-%m-%d)
now=$(date +%Y-%m-%d)
diff=$(mysql --defaults-extra-file=weather.ini -NBs  -e "SELECT avg(Rainfall - ETo) FROM aggregated_weather WHERE Date BETWEEN \"${aweekago}\" AND \"${now}\"" ${db})

OK=0
WARNING=1
CRITICAL=2
UNKNOWN=3

state=${OK}
msg="OK:"
if [[ "x${warn}" == "x" ]]; then
	warn=-0.5 
fi
if [[ "x${crit}" == "x" ]]; then
	crit=-2
fi



if (( $(echo "${diff} < ${warn}" |bc -l) )); then
 	state=${WARNING}
	msg="WARNING:"
fi
if (( $(echo "${diff} < ${crit}" |bc -l) )); then
 	state=${CRITICAL}
	msg="CRITICAL:"
fi

echo "${msg} Rainfall - evapotransipration is ${diff}|diff=${diff};${warn};${crit}"
exit ${state}
