#!/bin/sh

if [ $# != 2 ]; then
    echo "Usage: deploy_openid <host> <endpointuri>"
    echo "    <host>            Target host"
    echo "    <endpointuri>     Endpoint of OpenID service. Example: http://opec-portal-test2:8585/openid-server/provider/server/o2"
    exit 1
fi;

host=${1}
endpointuri=${2//\//\\/}

cd openid-server/src/main/resources/com/bc/openid
cat openid.properties_template | sed -e 's/<host>/'${endpointuri}'/' > openid.properties

echo 'building openid-server'
cd ../../../../../..
mvn clean package

echo 'deploying openid-server to' ${host}
echo 'copying webapp...'
cd target
scp *.war thomass@${host}:~
rm ../src/main/resources/com/bc/openid/openid.properties
cd ..
echo '...done. Deploying...'
ssh -t thomass@${host} 'rm -rf /opt/apache-tomcat-6.0.37/webapps/openid-server*'
ssh -t thomass@${host} 'rm -rf /opt/apache-tomcat-6.0.37/work/Catalina/localhost/openid-server/'
ssh -t thomass@${host} 'echo opec | sudo -S cp ~/openid-server-*.war /opt/apache-tomcat-6.0.37/webapps/openid-server.war'
echo '...done.'
