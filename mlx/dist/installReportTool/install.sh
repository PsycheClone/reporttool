printf "Extracting reporttool to /opt/\n"
printf "Executing this command as root, please provide "
sudo tar -xf reporttool.tar.gz -C /opt/

tool_alias="alias reporttool='/opt/reporttool/reporttool'"
printf "Checking if .profile exists in user home folder.\n"
if ! [ -f ~/.profile  ] ;
then
	touch ~/.profile
	printf ".profile created.\n"
fi
printf "Checking if the alias was already added.\n"
if ! grep -Fxq "$tool_alias" ~/.profile
then
	echo $tool_alias >> ~/.profile
	printf "Added alias reporttool."
fi
