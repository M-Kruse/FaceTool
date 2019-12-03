#!/bin/bash

#https://github.com/davisking/dlib-models

SHAPE_MODEL_URL="https://github.com/davisking/dlib-models/raw/master/shape_predictor_5_face_landmarks.dat.bz2"
FACE_MODEL_URL="https://github.com/davisking/dlib-models/raw/master/dlib_face_recognition_resnet_model_v1.dat.bz2"

echo "[INFO] Downloading ${SHAPE_MODEL_URL}"
wget $SHAPE_MODEL_URL > /dev/null 2>&1
if [[ $? > 0 ]]
	then
		echo "[ERROR] Failed to download ${SHAPE_MODEL_URL}. Exiting..."
	else
		echo "[INFO] Decompressing file..."
		SHAPE_MODEL=$(echo $SHAPE_MODEL_URL | awk -F'/' {'print $NF'})
		bzip2 -d $SHAPE_MODEL
fi

echo "[INFO] Downloading ${FACE_MODEL_URL}"
wget $FACE_MODEL_URL > /dev/null 2>&1
if [[ $? > 0 ]]
	then
		echo "[ERROR] Failed to download ${FACE_MODEL_URL}. Exiting..."
	else
		echo "[INFO] Decompressing file..."
		FACE_MODEL=$(echo $FACE_MODEL_URL | awk -F'/' {'print $NF'})
		bzip2 -d  $FACE_MODEL
fi
