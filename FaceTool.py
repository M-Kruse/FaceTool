#!/usr/bin/python
#This is a python class for using dlib, and eventually other libraries, for various image/face processing tasks.

import sys
import os
import dlib
import glob

class FaceTool(object):

    def __init__(self, shape_model, face_rec_model):
        super(FaceTool, self).__init__()
        self.face_detector = dlib.get_frontal_face_detector()
        self.shape_predictor = dlib.shape_predictor(shape_model)
        self.face_recognition = dlib.face_recognition_model_v1(face_rec_model)
        self.source_images = []
        self.face_descriptors = []
        self.processed_images = []
        self.labels = []

    def get_source_images(self, images_dir): 
        for f in glob.glob(os.path.join(images_dir, "*.jpeg")):
            self.source_images.append(f)
        return self.source_images

    def extract_face_descriptors(self, image_path):
        print("Processing file: {}".format(image_path))
        face_img = dlib.load_rgb_image(image_path)
        face_detections = self.face_detector(face_img, 1)
        for k, d in enumerate(face_detections):
            face_shape = self.shape_predictor(face_img, d)
            #The face descriptor is the 128D vector that we want to store later
            face_descriptor = self.face_recognition.compute_face_descriptor(face_img, face_shape)
            self.face_descriptors.append(face_descriptor)
            self.processed_images.append((face_img, face_shape))
        return self.processed_images, self.face_descriptors

    def cluster_face_descriptors(self, threshold=0.5):
        self.labels = dlib.chinese_whispers_clustering(self.face_descriptors, threshold)
        num_classes = len(set(self.labels))
        print("Total face images: {0}".format(str(len(self.images))))
        print("Estimated identities: {0}".format(num_classes))
        return self.labels

    def save_extracted_face_image(self, label):
        save_folder = output_folder_path + '/' + str(label)
        if not os.path.isdir(save_folder):
            os.makedirs(save_folder)
        img, shape = images[i]
        file_path = os.path.join(save_folder, "face_" + str(i))
        dlib.save_face_chip(img, shape, file_path, size=150, padding=0.25)

    def save_metadata_to_db(self):
        pass
