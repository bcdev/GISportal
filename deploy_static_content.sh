#!/bin/sh


if [ $# != 2 ]; then
    echo "Usage: deploy_static_content <host> <debug_flag>"
    echo "    <host>            Target host"
    echo "    <debug_flag>      Debug mode if flag is 1, no debug mode otherwise"
    exit 1
fi;

host=$1
if [ $2 == 1 ]; then buildflag=dev; else buildflag=; fi

command="python ~/projects/OpEcVis_git/GISportal/build.py --clean | python ~/projects/OpEcVis_git/GISportal/build.py "${buildflag}

echo copying content to ${1} ...
scp gisportal_all.js thomass@${host}:~/projects/OpEcVis_git/GISportal
scp gisportal_js.json thomass@${host}:~/projects/OpEcVis_git/GISportal
scp gisportal_css.json thomass@${host}:~/projects/OpEcVis_git/GISportal
scp gisportal_images.json thomass@${host}:~/projects/OpEcVis_git/GISportal
cd src
scp *.js thomass@${host}:~/projects/OpEcVis_git/GISportal/src
cd windows
scp *.js thomass@${host}:~/projects/OpEcVis_git/GISportal/src/windows
cd ../libs/filtrify/js
scp *.js thomass@${host}:~/projects/OpEcVis_git/GISportal/src/libs/filtrify/js
cd ../../../../html
scp *.html thomass@${host}:~/projects/OpEcVis_git/GISportal/html
cd img
scp * thomass@${host}:~/projects/OpEcVis_git/GISportal/html/img
cd ../css
scp * thomass@${host}:~/projects/OpEcVis_git/GISportal/html/css
echo '...done. Running build script...'
ssh thomass@${host} ${command}
echo '...done.'
