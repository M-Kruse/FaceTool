import sys
import dlib
sys.path.insert(1, '../')
from FaceTool import FaceTool 

shape_model = "../models/shape_predictor_5_face_landmarks.dat"
face_model = "../models/dlib_face_recognition_resnet_model_v1.dat"

test_face_encoding = [-0.03465554490685463, 0.14510095119476318, 0.136158749461174, -0.09110192954540253, -0.10112682729959488, 0.1020447313785553, -0.10387903451919556, -0.13143983483314514, 0.1086970865726471, -0.17367585003376007, 0.18214720487594604, 0.050411127507686615, -0.21027551591396332, 0.010360382497310638, -0.0109395831823349, 0.2008276879787445, -0.13857679069042206, -0.135528564453125, -0.08330675959587097, -0.06036229059100151, -0.04036779701709747, 0.0902884230017662, 0.055291857570409775, -0.007992714643478394, -0.14164993166923523, -0.267887681722641, -0.009832639247179031, 0.03180139139294624, 0.036568280309438705, -0.029163075610995293, -0.09214552491903305, 0.03936861455440521, -0.13565869629383087, 0.043565332889556885, 0.12359596788883209, 0.1275913417339325, -0.10181968659162521, -0.10889896750450134, 0.2522275745868683, 0.056838084012269974, -0.25556495785713196, -0.029768705368041992, 0.0626949593424797, 0.21168488264083862, 0.2170209437608719, -0.05776825174689293, 0.06578446924686432, -0.08552354574203491, 0.11941066384315491, -0.2859744131565094, 0.03620552271604538, 0.20555320382118225, 0.05040217936038971, 0.03142806142568588, 0.035597000271081924, -0.15787304937839508, -0.04970862343907356, 0.18971000611782074, -0.10425220429897308, -0.016781631857156754, 0.10354216396808624, -0.08202389627695084, -0.06525865197181702, -0.05649222061038017, 0.16343973577022552, 0.17520803213119507, -0.1668672114610672, -0.22506432235240936, 0.1807786524295807, -0.06289760023355484, -0.07668883353471756, 0.056632768362760544, -0.13746671378612518, -0.1674851030111313, -0.17042629420757294, -0.012199865654110909, 0.4268229901790619, 0.1598866730928421, -0.13614772260189056, 0.031107041984796524, -0.08597186952829361, -0.003216741606593132, 0.05669596046209335, 0.1408112496137619, -0.026347419247031212, -0.007998839020729065, 0.030268974602222443, 0.043969184160232544, 0.18374162912368774, -0.02593536302447319, -0.05290739983320236, 0.16067853569984436, 0.015407226979732513, 0.01898501254618168, 0.0002253558486700058, 0.06481222063302994, -0.10613072663545609, 0.037034161388874054, -0.17692984640598297, -0.06838527321815491, -0.022852610796689987, -0.026230882853269577, 0.10660919547080994, 0.20799612998962402, -0.19524377584457397, 0.21960224211215973, -0.028210030868649483, 0.009475229308009148, 0.11748120933771133, 0.06421801447868347, -0.05093170702457428, -0.05899197235703468, 0.1080809086561203, -0.2518065571784973, 0.1332518458366394, 0.18371106684207916, -0.02502678893506527, 0.10659199208021164, 0.1748678833246231, 0.11781208962202072, 0.12233332544565201, 0.011508889496326447, -0.17246462404727936, -0.13073799014091492, 0.0014475970529019833, -0.019475392997264862, 0.05283723026514053, 0.005746336653828621]

ft = FaceTool(shape_model, face_model, "FACESLURP", ["127.0.0.1"])
results = ft.db_search_for_face(test_face_encoding)
for row in results:
    ret, source = ft.get_source_img_by_uuid(row['source_img_uuid'])
    print("Face found in image: {0}".format(source[0]['storage_path']))