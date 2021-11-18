#!/bin/bash

GUI=$1
LOCAL=$2

print_usage()
{
	echo "(file history) usage ./install gui|terminal local|system"
	exit 1
}


if [[ $GUI = "gui" ]]; then
	echo "installing gui version"
elif [[ $GUI = "terminal" ]]; then
	echo "installing terminal version"
else
	print_usage
fi


if [[ $LOCAL = "local" ]];then
	echo "installing locally"
elif [[ $LOCAL = "system" ]];then
	echo "installing system wide"
else
	print_usage
fi

load_libs()
{
	echo "loading dependencies"
	git clone https://github.com/vincemann/ez-bash.git
	mv ./ez-bash/lib .
	rm -rf ./ez-bash
}


load_libs


echo "creating symlink in path (/usr/local/bin)"
chmod a+x "./show-last-files.py"
sudo ln -sf "$(pwd)/show-last-files.py" "/usr/local/bin/show-last-files"
