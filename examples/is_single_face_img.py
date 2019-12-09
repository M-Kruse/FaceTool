
import sys
import dlib
sys.path.insert(1, '../')
from FaceTool import FaceTool 

shape_model = "../models/shape_predictor_5_face_landmarks.dat"
face_model = "../models/dlib_face_recognition_resnet_model_v1.dat"
img = sys.argv[1]

ft = FaceTool(shape_model, face_model, "FACESLURP", ["127.0.0.1"])
print(ft.is_single_face_image(img))