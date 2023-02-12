#!/bin/bash

while getopts v: flag
do
    case "${flag}" in
        v) v=${OPTARG};;
    esac
done


rm -rf ./build
mkdir ./build
cp -r ./res ./build
python2 -m compileall ./build

meta=$(<meta.xml)
meta="${meta/\{\{VERSION\}\}/$v}"

cd ./build
echo "$meta" > ./meta.xml

folder="mod.wotStat_$v.wotmod"

zip -dvr -0 -X $folder res -i "*.pyc"
zip -vr -0 -X $folder meta.xml

cd ../
cp ./build/$folder $folder
rm -rf ./build