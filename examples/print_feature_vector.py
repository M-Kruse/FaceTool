
import sys
import dlib
sys.path.insert(1, '../')

from FaceTool import FaceTool 

shape_model = sys.argv[1] #"../models/shape_predictor_5_face_landmarks.dat"
face_model = sys.argv[2] #"../models/dlib_face_recognition_resnet_model_v1.dat"
source_images_folder = sys.argv[3] # /home/devel/Documents/test_images/sources/danny_devito

ft = FaceTool(shape_model, face_model, "FACESLURP", ["127.0.0.1"])
images = ft.get_source_images(source_images_folder)
for input_image in images:
    ft.extract_face_descriptors(input_image)
    for i, d in enumerate(zip(ft.processed_images, ft.face_descriptors)):
        #print(type(d))
        print("####################################################")

