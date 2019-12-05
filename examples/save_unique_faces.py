
import sys
import dlib
sys.path.insert(1, '../')

from FaceTool import FaceTool 

shape_model = sys.argv[1] #"shape_predictor_5_face_landmarks.dat"
face_model = sys.argv[2] #"dlib_face_recognition_resnet_model_v1.dat"
source_images_folder = sys.argv[3] # /home/devel/Documents/test_images/sources/danny_devito

ft = FaceTool(shape_model, face_model, "FACESLURP", ["127.0.0.1"])
images = ft.get_source_images(source_images_folder)
for input_image in images:
    result, img_uuid = ft.add_image_to_db("getty", "danny_devito", "1", "https://gettyimages.com/fake/{0}".format(input_image), "danny devito", input_image)
    ft.extract_face_descriptors(input_image)
    for i, d in enumerate(zip(ft.processed_images, ft.face_descriptors)):
        feature_vector_as_list = list(d[1])
        print(d[1])
        ret, new_feature_uuid = ft.add_face_descriptors_to_db(feature_vector_as_list, img_uuid)
        print("####################################################")

