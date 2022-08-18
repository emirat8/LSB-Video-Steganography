import cv2
from moviepy.editor import *
import os
import unicodedata
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import tkinter.font as font

def str_to_binary(msg):
    result= ''.join([ format(ord(i), "07b") for i in msg ])
    return result

def pixel_to_binary(msg):
    result= [ format(i, "07b") for i in msg ]
    return result

def vigenere(word, key, encrypt=True):
    result_encrypt = []
    result_decrypt = []
        
    if encrypt:
        print("\nEnkripsi")
        print("List Kata : ", word)
        for i in range(len(word)):
            kata = ''
            for j in range(len(word[i])):
                letter_n = ord(word[i][j])
                key_n = ord(key[j % len(key)])
        
                value = (letter_n + key_n) % 128
                print("Karakter ", chr(letter_n), "(", letter_n, ")", " dengan Key ", chr(key_n), "(", key_n, ")", " = ", chr(value), "(", value, ")")
        
                kata += chr(value)
            
            result_encrypt.append(kata)
        print("Hasil encrypt : ", result_encrypt)
        return result_encrypt

    else:
        print("\nDekripsi")
        print("List Ciphertext : ", word)
        for i in range(len(word)):
            kata = ''
            for j in range(len(word[i])):
                letter_n = ord(word[i][j])
                key_n = ord(key[j % len(key)])
        
                value = (letter_n - key_n) % 128
                print("Ciphertext ", chr(letter_n), "(", letter_n, ")", " dengan Key ", chr(key_n), "(", key_n, ")", " = ", chr(value), "(", value, ")")
        
                kata += chr(value)
            
            result_decrypt.append(kata)
        print("Hasil decrypt : ", result_decrypt)
        return result_decrypt
          

def encryption(text, key):
    return vigenere(word=text, key=key, encrypt=True)

def decryption(text, key):
    return vigenere(word=text, key=key, encrypt=False)

def lsb_hide(frame, data):
    print("Menyembunyikan ", data)
    binary_data=str_to_binary(data)
    print("Binary ",data," : ", binary_data)
    length_data = len(binary_data)
    
    index_data = 0

    for i in frame:
        for pixel in i:
            r, g, b = pixel_to_binary(pixel)
            if index_data < length_data:
                pixel[0] = int(r[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data < length_data:
                pixel[1] = int(g[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data < length_data:
                pixel[2] = int(b[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data >= length_data:
                break
  
    return frame

def hide(vid, n, data, key):
    vidcap = cv2.VideoCapture(vid)
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    frame_width = int(vidcap.get(3))
    frame_height = int(vidcap.get(4))
    size = (frame_width, frame_height)
    frame = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(vidcap.get(cv2.CAP_PROP_FPS))
    out = cv2.VideoWriter('stego_TEMP.avi', fourcc, fps=fps, frameSize=size)
    word_delimiter = "^*^"
    frame_delimiter = "^#^"
    data=unicodedata.normalize('NFKD', data).encode('ascii', 'ignore').decode('ascii')
    secret_message = data
    data = data.split(" ")

    stego_start = [str(n)]
    stego_start=encryption(stego_start, key)
    stego_start_str="".join(stego_start)
    stego_start_str+=word_delimiter
    
    print(data)
    data=encryption(data, key)
    print("\nTeks yang telah dienkripsi : ",data)

    for i in range (len(data)):
        if i==(len(data)-1):
            data[i] += frame_delimiter
        else:
            data[i] +=word_delimiter

    print("Setelah ditambahkan delimiter : ", data)
    print("Total ", len(data), " kata\n")
    
    frame_number = 0
    while(vidcap.isOpened()):
        frame_number += 1
        ret, frame = vidcap.read()
        if ret == False:
            break
        elif frame_number == 1:
            print("\nFrame ", frame_number)
            change_frame_with = lsb_hide(frame, stego_start_str)
            frame = change_frame_with
        elif (frame_number>=n) and (frame_number<n+len(data)):
            print("\nFrame ", frame_number)
            change_frame_with = lsb_hide(frame, data[frame_number-n])
            frame = change_frame_with
        out.write(frame)
    vidcap.release()
    out.release()
    cv2.destroyAllWindows()

    print("\nTeks telah berhasil disembunyikan")
    combine_video_audio(vid)
    return secret_message

def lsb_show(frame):
    word_delimiter = "^*^"
    frame_delimiter = "^#^"
    data_binary = ""
    show.data = ""
    
    for i in frame:
        for pixel in i:
            r, g, b = pixel_to_binary(pixel) 
            data_binary += r[-1]  
            data_binary += g[-1]  
            data_binary += b[-1]  
            total_bytes = [ data_binary[i: i+7] for i in range(0, len(data_binary), 7) ]
            decoded_data = ""
            for byte in total_bytes:
                decoded_data += chr(int(byte, 2))
                if decoded_data[-3:] == word_delimiter:
                    for i in range(0,len(decoded_data)-3):
                        show.data += decoded_data[i]
                    show.next = True
                    return
                elif decoded_data[-3:] == frame_delimiter:
                    for i in range(0,len(decoded_data)-3):
                        show.data += decoded_data[i]
                    show.next = False
                    return

def show(vid, key):
    print("Menampilkan pesan tersembunyi pada file : ", vid)
    print("Key : ", key)
    vidcap = cv2.VideoCapture(vid)
    frame = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("Jumlah frame pada video yang dipilih : ",frame)
    
    frame_number = 0
    result = []
    while(vidcap.isOpened()):
        frame_number += 1
        ret, frame = vidcap.read()
        if ret == False:
            break
        if frame_number == 1:
            print("\nFrame ", frame_number)
            lsb_show(frame)
            show.data = decryption([str(show.data)], key)
            n = int(show.data[0])
        elif frame_number >= n:
            print("\nFrame ", frame_number)
            lsb_show(frame)
            print (show.data)
            result.append(show.data)
            if show.next == False:
                secret_message = decryption(result, key)
                secret_message = " ".join(secret_message)
                print("\nPesan yang disembunyikan ialah : ", secret_message)
                break
    return secret_message

def combine_video_audio(vid):
    my_clip = VideoFileClip(vid)
    my_clip.audio.write_audiofile("audio_TEMP.mp3", verbose=False)
    videoclip = VideoFileClip("stego_TEMP.avi")
    audioclip = AudioFileClip("audio_TEMP.mp3")

    new_audioclip = CompositeAudioClip([audioclip])
    videoclip.audio = new_audioclip
    videoclip.write_videofile("video_steganography.avi", codec="ffv1", verbose=False)

    print("Video Steganografi tersimpan dengan nama file", "video_steganography.avi")
    os.remove("audio_TEMP.mp3")
    os.remove("stego_TEMP.avi")

def hide_gui(filename):
    window = Tk()
    if filename == "":
        window.destroy()
    else:   
        window.title('Hide Secret Message') 
        window.geometry("440x500")

        def hiding_secret_message(secret_message):
            msgbox = messagebox.showinfo("Secret Message",  "Secret message that have been successfully hidden:\n\n"+secret_message)
            if msgbox == "ok":
                window.destroy()
            
        vidcap = cv2.VideoCapture(filename)
        frame_width = int(vidcap.get(3))
        frame_height = int(vidcap.get(4))
        frame = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(vidcap.get(cv2.CAP_PROP_FPS))
        label_file_explorer = Label(window, text="Directory: "+filename)
        label_video_resolution = Label(window, text="Video resolution: "+str(frame_width)+"x"+str(frame_height))
        label_video_frame = Label(window, text="Total frame: "+str(frame))
        label_video_fps = Label(window, text="Frame per second: "+str(fps))

        scrollbar = Scrollbar(window)
        spinbox = Spinbox(window, from_= 2, to=frame, wrap=True, width=6)
        input_pesan = Text(window, height = 5, width = 50, yscrollcommand=scrollbar.set)
        scrollbar.config(command=input_pesan.yview)
        input_key = Text(window, height = 1, width = 50)
        button_hide = Button(window, text = "Hide", font=("Helvetica", 16), width=20, height=2, command =lambda: hiding_secret_message(hide(filename, int(spinbox.get()), str(input_pesan.get("1.0",'end-1c')), str(input_key.get("1.0",'end-1c')))))

        label_title = Label(window, text = "Hide Secret Message", font=("Helvetica", 20)).grid(row=1, column=1, pady=16)
        label_file_explorer.grid(row=2, column=1)
        label_video_resolution.grid(row=3, column=1)
        label_video_frame.grid(row=4, column=1)
        label_video_fps.grid(row=5, column=1)
        label_title_spinbox = Label(window, text = "First Frame to Hide Message").grid(row=6, column=1, pady=(15,0), padx=15, sticky='w')
        spinbox.grid(row=7, column=1, padx=15, sticky='w')
        label_title_pesan = Label(window, text = "Message").grid(row=8, column=1, padx=15, pady=(10,0), sticky='w')
        input_pesan.grid(row=9, column=1, padx=15, sticky='w')
        scrollbar.grid(row=9, column=1, columnspan=2, sticky='NSE')
        label_title_key = Label(window, text = "Key").grid(row=10, column=1, padx=15, pady=(10,0), sticky='w')
        input_key.grid(row=11, column=1, padx=15, sticky='w')
        button_hide.grid(row=12, column=1, padx=15, pady=(15,0))

        window.mainloop()
    

def browse_files():
    filename = filedialog.askopenfilename(initialdir = "C:/Users/Komandan3/Skripsion",
                                          title = "Select a Video",
                                          filetypes = (("Video files",
                                                        "*.avi*"),
                                                       ("All files",
                                                        "*.*")))
    return filename

def show_gui(filename):        
    window = Tk()
    if filename == "":
        window.destroy()
    else:
        window.title('Show Secret Message') 
        window.geometry("440x300")
        
        def showing_secret_message(secret_message):
            msgbox = messagebox.showinfo("Secret Message",  "Secret message that have been successfully obtained:\n\n"+secret_message)
            if msgbox == "ok":
                window.destroy()
            
        vidcap = cv2.VideoCapture(filename)
        frame_width = int(vidcap.get(3))
        frame_height = int(vidcap.get(4))
        frame = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(vidcap.get(cv2.CAP_PROP_FPS))
        label_file_explorer = Label(window, text="Directory: "+filename)
        label_video_resolution = Label(window, text="Video resolution: "+str(frame_width)+"x"+str(frame_height))
        label_video_frame = Label(window, text="Total frame: "+str(frame))
        label_video_fps = Label(window, text="Frame per second: "+str(fps))

        input_key = Text(window, height = 1, width = 50)
        button_show = Button(window, text = "Show", font=("Helvetica", 16), width=20, height=2, command =lambda: showing_secret_message(show(filename, str(input_key.get("1.0",'end-1c')))))

        label_title = Label(window, text = "Show Secret Message", font=("Helvetica", 20)).grid(row=1, column=1, pady=16)
        label_file_explorer.grid(row=2, column=1, padx=15)
        label_video_resolution.grid(row=3, column=1)
        label_video_frame.grid(row=4, column=1)
        label_video_fps.grid(row=5, column=1)
        label_title_key = Label(window, text = "Key").grid(row=6, column=1, padx=15, pady=(10,0), sticky='w')
        input_key.grid(row=7, column=1, padx=15, sticky='w')
        button_show.grid(row=8, column=1, padx=15, pady=(15,0))
        
        window.mainloop()

def gui():
    window = Tk()
    window.title('Video Steganography')
    window.geometry("300x300")
    label_title = Label(window, text = "Video Steganography", font=("Helvetica", 20)).pack(pady=16)
    button_hide_gui = Button(window, text = "Hide Secret Message", font=("Helvetica", 16), command = lambda: [hide_gui(browse_files())], width=20, height=3).pack(pady=8)
    button_show_gui = Button(window, text = "Show Secret Message", font=("Helvetica", 16), command = lambda: [show_gui(browse_files())], width=20, height=3).pack(pady=8)
    window.mainloop()

if __name__ == "__main__":
    gui()
