#!/bin/bash

GUI=$1
# LOCAL=$2

print_usage()
{
	echo "(file history) usage ./install gui|terminal"
	exit 1
}


if [[ $GUI = "gui" ]]; then
	echo "installing gui version"
elif [[ $GUI = "terminal" ]]; then
	echo "installing terminal version"
else
	print_usage
fi


# if [[ $LOCAL = "local" ]];then
# 	echo "installing locally"
# elif [[ $LOCAL = "system" ]];then
# 	echo "installing system wide"
# else
# 	print_usage
# fi

sudo apt install -y python3-pip
sudo apt install -y python3-tk
# sudo python3 -m pip install -r ./requirements.txt
# sudo pip3 install -r ./requirements.txt
# https://stackoverflow.com/questions/49324802/pip-always-fails-ssl-verification
sudo python3 -m pip install --trusted-host files.pythonhosted.org --trusted-host pypi.org --trusted-host pypi.python.org -r requirements.txt

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
