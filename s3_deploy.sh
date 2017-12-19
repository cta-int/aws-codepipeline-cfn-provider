#!/usr/bin/env bash

set -eux
BUCKET_KEY=${1-$FILE_NAME}
BUCKET_NAME=${2-$BUCKET}
pipenv shell
pipenv --python 3.6.1
pipenv install
mkdir -p build
cp -r $VIRTUAL_ENV/lib/python3.6/site-packages/* build/
cp -r utils build/
cp -r pipeline_lambda build/
cd build
zip -r pipeline_lambda.zip *
aws s3 cp pipeline_lambda.zip s3://$BUCKET_NAME/$BUCKET_KEY
cd ..
rm -rf build