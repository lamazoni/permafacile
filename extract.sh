#!/usr/bin/env bash
OPATH=`pwd`
cd ..
DPATH=`pwd`
cd ${DPATH}/
if [ -z $1 ] ; then
	echo Postfix needed
	exit 1
fi
[ ! -d ${DPATH}/agenda ] && echo error directory needed && exit 1 ;
#-----------------------
OPATH=`pwd`
echo Moving from ${OPATH} to ${DPATH}/
cd ${DPATH}/

ls -1 ./agenda/*.txt > ${DPATH}/tmplistFiles.txt
ls -1 ./agenda/*.py >> ${DPATH}/tmplistFiles.txt
ls -1 ./agenda/*.sql >> ${DPATH}/tmplistFiles.txt
echo ./agenda/static >> ${DPATH}/tmplistFiles.txt
echo ./agenda/templates >> ${DPATH}/tmplistFiles.txt
echo ./agenda/installDistriFacile.sh >> ${DPATH}/tmplistFiles.txt

if [ ! -d "agenda$1" ]; then
    mkdir -p ${DPATH}/agenda$1/agenda
else
    echo ERROR
    exit 1
fi
for file in $(cat tmplistFiles.txt) ; do
    cp -pr $file ${DPATH}/agenda$1/agenda/.
done
tar cvf ./agenda$1.tar ./agenda$1
rm -rf ${DPATH}/agenda$1
#TODO : remove secret key
#TODO : remove databasename and database user
