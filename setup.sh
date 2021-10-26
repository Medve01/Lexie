mkdir /opt/Lexie
mkdir /opt/Lexie/lexie
cp -R ./lexie /opt/Lexie/
cp -f requirements.txt /opt/Lexie
cp -f wsgi.py /opt/Lexie
chown -R www-data:www-data /opt/Lexie
if ! cmp ./lexie-gunicorn.service /etc/systemd/system/lexie-gunicorn.service >/dev/null 2>&1
then
	cp -f ./lexie-gunicorn.service /etc/systemd/system/lexie-gunicorn.service
	systemctl daemon-reload
fi
pip3 install -r requirements.txt
systemctl restart lexie-gunicorn