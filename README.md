# dnsmasq-analyzer

## Database table 
- [titles.sql](titles.sql)
- [queries.sql](queries.sql)


## Installation
```
#
sudo -s

# 
cd /etc/
git clone <this repo>
cd dnsmasq-analyzer

#
cp env.sample env
vim env

# 
pip install -r requirements.txt

# 
cp dnsmasq-analyzer.service /usr/lib/systemd/system/
systemctl daemon-reload
systemctl enable start dnsmasq-analyzer
systemctl start start dnsmasq-analyzer
systemctl status status dnsmasq-analyzer
```