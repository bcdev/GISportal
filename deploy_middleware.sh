#!/bin/sh

if [ $# != 1 ]; then
    echo "Usage: deploy_middleware <host>"
    echo "    <host>            Target host"
    exit 1
fi;

host=${1}

echo "deploying middleware to ${host}..."
cd middleware
scp *.py thomass@${host}:~/projects/OpEcVis_git/GISportal/middleware
cd portalflask
scp *.py thomass@${host}:~/projects/OpEcVis_git/GISportal/middleware/portalflask
cd core
scp *.py thomass@${host}:~/projects/OpEcVis_git/GISportal/middleware/portalflask/core
cd ../models
scp *.py thomass@${host}:~/projects/OpEcVis_git/GISportal/middleware/portalflask/models
cd ../static
scp *.py thomass@${host}:~/projects/OpEcVis_git/GISportal/middleware/portalflask/static
cd ../views
scp *.py thomass@${host}:~/projects/OpEcVis_git/GISportal/middleware/portalflask/views
cd ../../..
echo '...done. Re-loading apache...'
ssh -t thomass@${host} 'echo opec | sudo -S /etc/init.d/bc-run-opec-portal reload'
echo '...done.'
