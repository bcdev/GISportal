#!/bin/sh

if [ $# != 4 ]; then
    echo "Usage: deploy_config <host> <thredds_url> <openid_rp_url> <debug_flag>"
    echo "    <host>            Target host"
    echo "    <thredds_url>     Base URL of thredds server being used, such as http://portal.waqss.de"
    echo "    <openid_rp_url>   URL of discovery service of OpenID server. Example: http://opec-portal-test2:8585/openid-server/provider/discovery/gis-portal"
    echo "    <debug_flag>      Debug mode if flag is 1, no debug mode otherwise"
    exit 1
fi;

host=${1}
thredds_url=${2//\//\\/}
openid_rp_url=\"${3//\//\\/}\"
if [ $4 == 1 ]; then debug=True; else debug=False; fi

echo copying config to ${host}...
cd config
scp *.py thomass@${host}:~/portal/config
scp *.csv thomass@${host}:~/portal/config
cat wmsServers.py_template | sed -e 's/<host>/'${thredds_url}'/' > wmsServers.py
scp wmsServers.py thomass@${host}:~/portal/config/wmsServers.py
rm wmsServers.py
cat settings.py_template | sed -e 's/<debug>/'${debug}'/' | sed -e 's/<openid_rp_url>/'${openid_rp_url}'/' > settings.py
scp settings.py thomass@${host}:~/portal/middleware/portalflask/settings.py
rm settings.py
echo '...done. Re-creating caches...'
ssh -t thomass@${host} '~/projects/OpEcVis_git/GISportal/clearcache'
echo '...done. Re-creating database...'
ssh -t thomass@${host} 'echo opec | sudo -S ~/projects/OpEcVis_git/GISportal/cleardb.sh'
cd ..
echo '...done.'
