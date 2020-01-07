import os
import sys
import dlib
sys.path.insert(1, '../')

from FaceTool import FaceTool 

shape_model = sys.argv[1] #"shape_predictor_5_face_landmarks.dat"
face_model = sys.argv[2] #"dlib_face_recognition_resnet_model_v1.dat"
source_images_folder = sys.argv[3] # /home/devel/Documents/test_images/sources/danny_devito

if not os.path.isdir(source_images_folder):
    print("[ERROR] Source image folder path was not found: {0}".format(source_images_folder))
    exit()


ft = FaceTool(shape_model, face_model, "FACETOOL", ["127.0.0.1"])
images = ft.get_source_images(source_images_folder)

if not images:
    print("[ERROR] Source image folder is empty...")
    exit()

for input_image in images:
    print('[INFO] Processing image - {0}'.format(input_image))
    #Fake placeholder data from scraping
    test_url = "https://example.com/{0}".format(input_image)
    ret, src = ft.db_search_img_url(test_url)
    if not ret:
        result, img_uuid = ft.db_add_image("getty", "danny_devito", "1", test_url, "danny devito", input_image)
        ft.extract_face_descriptors(input_image)
        for i, d in enumerate(zip(ft.processed_images, ft.face_descriptors)):
            feature_vector_as_list = list(d[1])
            print(feature_vector_as_list)
            if not ft.db_search_for_face(feature_vector_as_list):
                 ret, feature_uuid = ft.db_add_face_descriptors(feature_vector_as_list, img_uuid)
                 #print("[INFO] Added new face descriptor - {0}::{1}".format(input_image.split("/")[-1], feature_uuid))
            else:
                 print("[INFO] Face descriptor already exists, skipping...")
    else:
        print("[INFO] Image already processed, skipping...")