# #!/usr/bin/env python3
import tqdm
import time

import os
import socket
from datetime import datetime
from threading import Thread,Lock
from keras.preprocessing import image
import numpy as np
from keras.models import load_model

def print_current_time():
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print(current_time)
mutex=Lock()
global models
models={'category_vgg16':'model_vgg_categorical_s81.h5',
        'binary_vgg16':'model_vgg_s81.h5',
        'resnet_50':'pred_drone_5_classes_restnet_50_3.h5'}

def write_to_file(txt):
    f = open('./results_of_3models.txt', 'a')
    f.write(txt+"\n")
    f.close()


def get_data():
    with open('./results_of_3models.txt', 'r') as f:
        f_contents = f.read()
        return f_contents

def classification(path_img,size,model_type):
    classes = ['airplane', 'bird', 'drone', 'helicopter', 'other']
    if model_type == 'binary_vgg16':
        classes = ['yes', 'no']
    model=models[model_type]
    saved_model = load_model(model)
    img = image.load_img(path_img, target_size=(size, size))
    img = np.asarray(img)
    img = np.expand_dims(img, axis=0)
    output = saved_model.predict(img)
    i = np.argmax(output)
    # mutex for write in file:
    txt="-model: "+model_type+" -class: "+classes[i]+"\n"
    global mutex
    with mutex:
    # mutex.acquire()
        write_to_file(txt)
    # mutex.release()

HOST = '192.168.8.107'  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

BUFFER_SIZE = 10000
SEPARATOR = "<SEPARATOR>"

def detect_by_threads(file_path):
    t = []
    args = [ 'binary_vgg16', 'category_vgg16','resnet_50']
    for i in range(3):
        t.append(Thread(target=classification, args=(file_path, 81, args[i])))
        t[i].start()
    for i in range(3):
        t[i].join()

if __name__ == '__main__':
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            client_socket, address = s.accept()
            with client_socket:
                received = client_socket.recv(BUFFER_SIZE).decode()
                filename, filesize = received.split(SEPARATOR)
                filename = os.path.basename(filename)
                filesize = int(filesize)

                # progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)

                with open(filename, "wb") as f:
                    # while True:
                    bytes_read = client_socket.recv(BUFFER_SIZE)
                        # if not bytes_read:
                        #     break
                    f.write(bytes_read)
                        # progress.update(len(bytes_read))
                txt="\n"+"\n"+"image name: "+filename
                write_to_file(txt)
                # print_current_time()
                t1=time.time()
                detect_by_threads(filename)
                t2=time.time()
                # print_current_time()
                res = get_data()
                client_socket.sendall(res.encode())
                client_socket.close()
                s.close()

# def classification(path_img,size,model_type):
#     classes = ['airplane', 'bird', 'drone', 'helicopter', 'other']
#     if model_type == 'binary_vgg16':
#         classes = ['yes', 'no']
#     model=models[model_type]
#     saved_model = load_model(model)
#     img = image.load_img(path_img, target_size=(size, size))
#     img = np.asarray(img)
#     img = np.expand_dims(img, axis=0)
#     output = saved_model.predict(img)
#     i = np.argmax(output)
#     txt="-model: "+model_type+" -class: "+classes[i]+"\n"
#     write_to_file(txt)

# # # run classification
# # # print_current_time()
# t1=time.time()
# path_img='object_images/object.png'
# size=81
# classification(path_img,size,'category_vgg16')
# classification(path_img,size,'binary_vgg16')
# classification(path_img,size,'resnet_50')
# t2=time.time()
# # t1 = time.time()
# # detect_by_threads(path_img)
# # t2 = time.time()
# print('Runtime in the program is:'+str(t2-t1))
#
# # print_current_time()