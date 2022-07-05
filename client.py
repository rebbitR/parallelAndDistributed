import time
import tqdm
import socket
from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import askopenfile
import os


HOST = '192.168.8.107'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 10000 # send 10000 bytes each time step

ws = Tk()
ws.title('Drones detector')
ws.geometry('600x700')

def open_file():
    file_path = askopenfile(mode='r', filetypes=[('Image Files', '*png')])
    if file_path is not None:
        global img_path
        img_path = file_path.name
        global filesize
        filesize = os.path.getsize(img_path)
        pass

#
#
def upload_files():
    # show the image
    img = PhotoImage(file=img_path)
    mylabel = Label(
        ws,
        image=img
    )
    mylabel.grid(row=3, column=3)

    # progress
    pb1 = Progressbar(
        ws,
        orient=HORIZONTAL,
        length=300,
        mode='determinate'
    )
    pb1.grid(row=7, columnspan=1, pady=20)


    filename = img_path
    filesize = os.path.getsize(filename)

    # create the client socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((HOST, PORT))

    s.sendall(f"{filename}{SEPARATOR}{filesize}".encode())

    # progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)

    with open(filename, "rb") as f:
        # while True:
        bytes_read = f.read(BUFFER_SIZE)
        s.sendall(bytes_read)
            # if not bytes_read:
            #     break
            # progress.update(len(bytes_read))

    # start the progress pb1
    for i in range(9):
        ws.update_idletasks()
        pb1['value'] += 20
    pb1.destroy()

    data = s.recv(BUFFER_SIZE)
    Label(ws, text=data, foreground='red').grid(row=4, columnspan=3, pady=10)

    s.close()

# Create style Object
style = Style()


style.configure('W.TButton', font=
('calibri', 10, 'bold'),
                foreground='#007FFF')

style.configure('TButton', font=
('calibri', 10, 'bold'),
                foreground='red')

def showScreen():
    # shoe the logo
    img = PhotoImage(file='logo.png')
    mylabel = Label(
        ws,
        image=img
    )
    mylabel.grid(row=0, column=1)

    # the label that say to the client what to do
    chooseImgLbl = Label(
        ws,
        text='Upload image object in size 81/81 in png format '
    )
    chooseImgLbl.grid(row=4, column=1, padx=10)

    # botton 1 "choose image" that starts the function open_file()
    chooseImgBtn = Button(
        ws,
        text='Choose image',
        style='W.TButton',
        command=lambda: open_file()
    )
    chooseImgBtn.grid(row=5, column=1)

    # botton 2 "Upload and detect" that starts the function upload_files()
    upldBtn = Button(
        ws,
        text='Upload and detect',
        style='TButton',
        command=upload_files
    )
    upldBtn.grid(row=6, columnspan=1, pady=30)

    ws.mainloop()


showScreen()








