#!/usr/bin/python
#This is a python class for using dlib, and eventually other libraries, for various image/face processing tasks.

import sys
import os
from math import sqrt
import time
import functools
import urllib
from glob import glob

import dlib
import numpy

from selenium import webdriver

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
        self.image_types = ['*.jpeg', '*.jpg', '*.png']
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
                PRIMARY KEY (id))""".format(self.keyspace))
        self.session.execute("CREATE INDEX IF NOT EXISTS ON {0}.images (image_url)".format(keyspace))
        # The cqlsh tool for cassandra doesn't print out the full precision by default
        # https://stackoverflow.com/questions/53885281/how-to-store-6-digit-precision-double-float-decimal-number-in-cassandra
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS {0}.faces (
                id uuid,
                face_encoding frozen<list<float>>,
                source_img_uuid uuid,
                PRIMARY KEY (id))""".format(self.keyspace))
        #self.session.execute("CREATE INDEX IF NOT EXISTS ON FACETOOL.faces (face_encoding)")
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS {0}.identities (
                id uuid,
                source_encodings list<uuid>,
                last_name text,
                first_name text,
                note text,
                PRIMARY KEY (id))""".format(self.keyspace))
        self.session.execute("CREATE INDEX IF NOT EXISTS ON {0}.identities (source_encodings)".format(keyspace))
    
    def get_source_images(self, images_dir): 
        result = [] 
        for ext in self.image_types:
            result += glob(os.path.join(images_dir, ext))
        return result

    def extract_face_descriptors(self, image_path):
        face_img = dlib.load_rgb_image(image_path)
        face_detections = self.face_detector(face_img, 1)
        for k, d in enumerate(face_detections):
            face_shape = self.shape_predictor(face_img, d)
            #The face descriptor is the 128D vector that we want to store later
            face_descriptor = self.face_recognition.compute_face_descriptor(face_img, face_shape)
            #print(type(face_descriptor))
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

    def db_add_image(self, source, query_str, query_page_num, image_url, alt_text, storage_path):
        log_time = time.time()
        #I can't get this to work without using the old style string sub while the other function works with using "{}".format() ?????
        new_uuid = util.uuid_from_time(log_time)
        result = self.session.execute("INSERT INTO " + self.keyspace + ".images (id, source, query, query_page, image_url, alt_text, storage_path) VALUES (%s, %s, %s, %s, %s, %s, %s) IF NOT EXISTS", [new_uuid, source, query_str, query_page_num, image_url, alt_text, storage_path])
        new_row = result[0]['[applied]']
        if new_row:
            print("[INFO] Added image {} to DB".format(source))
            return True, new_uuid
        else:
            existing_uuid = result[0]['id']
            print("[INFO] add_image_to_db(): Image already exists in DB")
            return False, existing_uuid

    def db_add_face_descriptors(self, new_face_descriptor, source_img_uuid):
        log_time = time.time()
        new_uuid = util.uuid_from_time(log_time)
        query = self.session.prepare("""
            INSERT INTO {0}.faces (id, face_encoding, source_img_uuid)
            VALUES ({1}, {2}, {3}) IF NOT EXISTS""".format(self.keyspace, new_uuid, new_face_descriptor, source_img_uuid))
        try:
            result = self.session.execute(query)
            new_row = result[0]['[applied]']
            if new_row:
                print("[INFO] Added new face descriptor: {0}".format(new_uuid))
                return True, new_uuid
            else:
                existing_uuid = result[0]['id']
                print("[INFO] Face descriptor already exists at: {0}".format(existing_uuid))
                return False, existing_uuid
        except Exception as e:
            print("[ERROR] add_face_descriptors_to_db(): Failed to add face descriptors to database. Exception: {0}".format(e))
            return False, None

    def db_get_all_encodings(self):
        return self.session.execute("SELECT * FROM FACETOOL.faces")

    def db_search_face_encoding(self, face_encoding):
        #print(type(face_encoding))
        #To use this encoding saved as a list with dlib, you can typecast the list to vector with dlib.vector()
        query = "SELECT * FROM FACETOOL.faces WHERE face_encoding={0}".format(face_encoding)
        result = self.session.execute(query)
        if result:
            return True, result
        else:
            return False, None

    def db_search_source_img_by_uuid(self, source_uuid):
        query = "SELECT * FROM FACETOOL.images WHERE id={0}".format(source_uuid)
        result = self.session.execute(query)
        if result:
            return True, result
        else:
            return False, None
            
    def db_search_for_face(self, target_face_encoding):
        results = []
        for row in self.db_get_all_encodings():
            test_face = row['face_encoding']
            if self.compare_faces(target_face_encoding, test_face):
                results.append(row)
                #print("Match found: {0}".format(row))
        #print(results)
        return results

    def db_search_img_url(self, url):
        #Check if the url exists in the DB to avoid duplicates
        result = self.session.execute("SELECT * FROM FACETOOL.images WHERE image_url=%s", [url])
        if result:
            return True, result
        else:
            return False, None

    def is_portrait_image(self):
        #Detect if the image is a portrait
        pass

    def is_single_face_image(self, image_path):
        if len(self.face_detector(dlib.load_rgb_image(image_path), 1)) == 1:
            return True
        else:
            return False
        #Detect if the image has a single face
        pass
        
#Collect faces -> Cluster -> Create IDs for clusters -> Add Cluster ID to face records -> Serve page for labeling faces -> Save labels to identity table