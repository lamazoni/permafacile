#!/usr/bin/env bash
#
# Installation script, provide for convinience purpose only (bug may occur)
#
# PLZ BE ROOT TO EXECUTE THE SCRIPT
#set -x

# TODO: use gosu
#----------------------------------------
# Check root privileges.
# @args: N.A
# @effect: stop application if test fails
function check_root {
    local id=$(id -u)
    if [ $id -ne 0 ]; then
        echo -e "plz be root"
        exit 1
    fi
}

# change values of global array with user's input
# @args:
# $1: key that will be changed
# @effect: update entries array
function change_entries {
    local temp
    read temp
    if [ ! $temp = "" ]; then
        entries[$1]=$temp
    fi
}

function exe {
	[ dryRun == "true" ] && echo $*
	[ dryRun != "true" ] && `$*`
}

function usage {
	echo "./installDistriFacile.sh [-h] [-u <username> ] [-a <ip:port>] [-V <version> [-t <source-file.tar>]]"
	echo "-h : show this help"
	echo "-u : username (os username uid)"
	echo "-a : ip:port (no need for 80, 8001 for dev install)"
	echo "IF NO a,u OPTION, DEFAULT IS USED"
	echo "-V : install to a specific name dir"
	echo "-t : source tar file (the one from extract.sh) "
}

#----------------------------------------


declare -A entries=(
				   #remplace by your user here
				   ["user"]="ode"
				   #remplace by your ip and port here (no need for 80)
				   ["ipandport"]="192.168.253.83:81"
				   #destination folder
				   ["folder"]="."
				   #source extraction tar file
				   ["source"]="agendamoving.tar"
)
VERSION=""
OPT=$*
if [ "${OPT}" == "-h" ] ; then
	usage
	exit 0
fi
while getopts "u:a:v:t" OPT ; do
	case "$OPT" in
		u)
			entries["user"]=${OPTARG}
		;;
		a)
			entries["ipandport"]=${OPTARG}
		;;
		v)
			readonly VERSION=${OPTARG}
		;;
		t)
			if [ -z ${VERSION} ] ; then
				echo "option -v mandatory, v before t"
				exit 1
			fi
			entries["source"]=${OPTARG}
		;;
		*)
			break
		;;
	esac
done

[ ! -z ${VERSION} ] && entries["folder"]="agendaV${VERSION}"
check_root
[ $(cat /etc/passwd  | grep ${entries["user"]} | wc -l) -ne 1 ] && echo "username not found" && exit 1
iponly=$( echo ${entries["ipandport"]} | sed s~:[0-9]*~~ )
[ $(ip addr sh | grep inet | grep ${iponly} | wc -l) -ne 1 ] && echo "error ip interface not found" && exit 1

if [ ! -z ${VERSION} ] ; then
	[ -d ${entries["folder"]} ] && echo clean space first && exit 1
	[ -f ${entries["source"]} ] && echo "need file not found" && exit 1
fi

#----------------------------------------

while $( [ "${doupdate}" != "yes" ] && [ "${doupdate}" != "no" ] ) ; do
	echo "Do you want update your sytem (yes/no)(recommended : yes, default : no) ?"
	read doupdate
	[ -z ${doupdate} ] && doupdate="no" && echo no
	if [ ${doupdate} == "yes" ] ; then
		sudo apt-get update && sudo apt-get upgrade --yes
	fi
done

#----------------------------------------
error=0
for toInstall in nginx python-pip python3-pip python3-virtualenv virtualenv postgresql postgresql-client postgresql-contrib ; do
	sudo apt-get install ${toInstall} -y
	let error=error+$?
done


if [ ! -z ${VERSION} ] ; then
	virtualenv --python=/usr/bin/python3 ${entries["folder"]}
	let error=error+$?
	tar xvf ${entries["source"]}
	let error=error+$?
	mv agenda${entries["source"]}/* ${entries["folder"]}/.
	let error=error+$?
	cd ${entries["folder"]}
	let error=error+$?
else
	virtualenv --python=/usr/bin/python3 .
	let error=error+$?
	entries["folder"] = "."
	let error=error+$?
fi

. ./bin/activate
let error=error+$?

pip install -r requirements.txt
let error=error+$?

deactivate
let error=error+$?
#remplace by your postgres user/password here
su -l postgres -c psql <<EOF
CREATE EXTENSION hstore;
CREATE USER uagenda WITH PASSWORD 'agendax';
create database agenda with owner=uagenda encoding='UTF8';
EOF
let error=error+$?

echo "localhost:5432:agenda:uagenda:agendax" >> /home/${entries["user"]}/.pgpass
let error=error+$?
chown ${entries["user"]}:${entries["user"]} /home/${entries["user"]}/.pgpass
let error=error+$?
chmod 400 /home/${entries["user"]}/.pgpass
let error=error+$?
su -l ${entries["user"]} -c "psql -U uagenda -d agenda -h localhost -p 5432 -c "select True \;" "
if [ $? -eq 0 ]; then
	echo "postgres OK"
else
	echo "ERROR, check your postgres conf"
fi


sed -i s~http://[^\"]*~http://${entries["ipandport"]}~ ${entries["folder"]}/static/js/conf.js
let error=error+$?
if [ -z ${VERSION} ] ; then
	for file in "main" "templateMain" "log" "summary" ; do
		cp -p ${entries["folder"]}/templates/${file}.html ${entries["folder"]}/templates/${file}.sav.html
		cp -p ${entries["folder"]}/templates/${file}-dist.html ${entries["folder"]}/templates/${file}.html
		let error=error+$?
	done
fi
if [ ${error} -ne 0 ] ; then
	echo ERROR occured, the output need to be checked.
fi
if $( [ -z ${VERSION} ] && [ ${error} -eq 0 ] ) ; then
	echo "What to do next ? Find here below the next step :"
	echo ". ./bin/activate"
	echo "python run.py"
	echo "Lauch a webbrowser on ${entries["ipandport"]}"
fi

#TODO : change secret key
#TODO : change databasename and database user
