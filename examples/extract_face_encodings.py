
import sys
import dlib
sys.path.insert(1, '../')

from FaceTool import FaceTool 

shape_model = "shape_predictor_5_face_landmarks.dat"
face_model = "dlib_face_recognition_resnet_model_v1.dat"
ft = FaceTool(shape_model, face_model)
images = ft.get_source_images("/home/devel/Documents/test_images/sources/danny_devito", ["jpeg", "jpg"])
print(images)
for input_image in images:
    ft.extract_face_descriptors(input_image)
    for i, d in enumerate(zip(ft.processed_images, ft.face_descriptors)):
        print(d)
        feature_vectors = list(d[1])
        print(len(feature_vectors))
        print(dlib.vector(feature_vectors))
        print("####################################################")
