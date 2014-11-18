#!/bin/bash

if [ -z "$1" ]; then
    echo "Conversion Tool (PNG to NetCDF-4)"
    echo "call: convert.sh <png-file>"
    exit 1
fi

export TOOL_HOME=`( cd $(dirname $0); cd ..; pwd )`

exec java -Xmx2G -Dceres.context=beam \
    -Dbeam.logLevel=INFO -Dbeam.consoleLog=true \
    -Dbeam.reader.tileHeight=1024 -Dbeam.reader.tileWidth=1024 \
    -Dbeam.mainClass=com.bc.gisportal.tools.PngConverter \
    -jar "$TOOL_HOME/bin/ceres-launcher.jar" \
    $1