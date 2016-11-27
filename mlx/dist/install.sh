printf "Extracting reporttool to /opt/\n"
printf "Executing this command as root, please provide password."
sudo tar -xf reporttool.tar.gz -C /opt/

tool_alias="alias reporttool='/opt/reporttool/reporttool'"
if ! [ -f ~/.profile  ] ;
then
	touch ~/.profile
fi
if ! grep -Fxq "$tool_alias" ~/.profile
then
	echo $tool_alias >> ~/.profile
fi
