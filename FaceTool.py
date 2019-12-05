#!/usr/bin/python
#This is a python class for using dlib, and eventually other libraries, for various image/face processing tasks.

import sys
import os
import dlib
import glob
from math import sqrt
import time

from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from cassandra import ConsistencyLevel
from cassandra import util
from cassandra.query import dict_factory

class FaceTool(object):

    def __init__(self, shape_model, face_rec_model, keyspace, cluster_node_ip_list):
        super(FaceTool, self).__init__()
        self.face_detector = dlib.get_frontal_face_detector()
        self.shape_predictor = dlib.shape_predictor(shape_model)
        self.face_recognition = dlib.face_recognition_model_v1(face_rec_model)
        self.source_images = []
        self.face_descriptors = []
        self.processed_images = []
        self.labels = []
        self.keyspace = keyspace
        self.cluster = Cluster(cluster_node_ip_list)
        self.session = self.cluster.connect()
        self.session.row_factory = dict_factory
        #Make sure DB is initalized and tables exist
        self.session.execute("""
            CREATE KEYSPACE IF NOT EXISTS %s
            WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '1' } 
            """ % self.keyspace) #Single node right now so no node replication
        
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS {0}.images (
                id uuid,
                source text,
                query text,
                query_page text,
                image_url text,
                alt_text text,
                storage_path text,
                PRIMARY KEY (image_url))""".format(self.keyspace))
        
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS {0}.faces (
                id uuid,
                face_encoding frozen<list<float>>,
                source_img_uuid uuid,
                PRIMARY KEY (face_encoding))""".format(self.keyspace))

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
    
    def compare_faces(self, face_a_vectors, face_b_vectors, distance_threshold=0.6):
            #https://github.com/davisking/dlib/issues/950#issuecomment-353690061
            if sum((face_a_vectors[dim] - face_b_vectors[dim]) ** 2 for dim in range(len(face_a_vectors))) < distance_threshold:
                return True
            else:
                return False

    def add_image_to_db(self, source, query_str, query_page_num, image_url, alt_text, storage_path):
        log_time = time.time()
        #I can't get this to work without using the old style string sub while the other function works with using "{}".format() ?????
        new_uuid = util.uuid_from_time(log_time)
        result = self.session.execute("INSERT INTO " + self.keyspace + ".images (id, source, query, query_page, image_url, alt_text, storage_path) VALUES (%s, %s, %s, %s, %s, %s, %s) IF NOT EXISTS", [new_uuid, source, query_str, query_page_num, image_url, alt_text, storage_path])
        new_row = result[0]['[applied]']
        if new_row:
            print("Added image to DB")
            return True, new_uuid
        else:
            existing_uuid = result[0]['id']
            print("Image already exists in DB")
            return False, existing_uuid

    def add_face_descriptors_to_db(self, new_face_encoding, source_img_uuid):
        log_time = time.time()
        new_uuid = util.uuid_from_time(log_time)
        query = self.session.prepare("""
            INSERT INTO {0}.faces (id, face_encoding, source_img_uuid)
            VALUES ({1}, {2}, {3}) IF NOT EXISTS""".format(self.keyspace, new_uuid, new_face_encoding, source_img_uuid))
        try:
            result = self.session.execute(query)
            new_row = result[0]['[applied]']
            if new_row:
                print("Added new face descriptor: {0}".format(new_uuid))
                return True, new_uuid
            else:
                existing_uuid = result[0]['id']
                print("Face descriptor already exists at: {0}".format(existing_uuid))
                return False, existing_uuid
        except Exception as e:
            print("[ERROR] add_face_vectors_to_db(): Failed to add face vectors to database. Exception: {0}".format(e))
            return False, None

    def get_face_percentage(self):
        #Get the percentage of the image that is face
        pass

    def is_portrait_image(self):
        #Detect if the image is a portrait
        pass

    def is_single_face_image(self):
        #Detect if the image has a single face
        pass

    def save_metadata_to_db(self):
        pass