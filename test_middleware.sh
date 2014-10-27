#!/bin/sh

if [ $# != 1 ]; then
    echo "Usage: test_middleware <host>"
    echo "    <host>            Target host"
    exit 1
fi;

host=${1}

./deploy_middleware.sh ${host}
cd middleware/portalflask-tests
scp * thomass@${host}:~/projects/OpEcVis_git/GISportal/middleware/portalflask-tests
echo 'Uploading resources...'
cd resources
scp * thomass@${host}:~/projects/OpEcVis_git/GISportal/middleware/portalflask-tests/resources
echo '...done. Testing middleware...'
ssh -t thomass@${host} 'export BEAM_HOME=/home/thomass/beam-5.0;
export JAVA_HOME=/opt/java;
export JDK_HOME=/opt/java;
export PATH=$PATH:$JAVA_HOME/bin;
export LD_LIBRARY_PATH=/opt/gdal-1.11.0/lib:$JDK_HOME/jre/lib/amd64/server:$LD_LIBRARY_PATH;
export PYTHONPATH=/home/thomass/projects/portal/middleware;
python projects/OpEcVis_git/GISportal/middleware/portalflask-tests/portalflask_tests.py'
echo '...done.'