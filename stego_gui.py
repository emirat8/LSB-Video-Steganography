#Import required libraries
import cv2
import os
import unicodedata
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip

def str_to_binary(msg):
    #Convert string to binary 7 digit
    result= ''.join(format(ord(i), "07b") for i in msg)
    return result

def pixel_to_binary(msg):
    #Convert pixel to binary 8 digit
    result= [format(i, "08b") for i in msg]
    return result

def vigenere(words, key, encrypt=True):
    result_encrypt = []
    result_decrypt = []
        
    if encrypt:
        print("\nEnkripsi")
        print("List Kata : ", words)
        #Loop through all word index
        for i in range(len(words)):
            word = ''
            #Loop through each word character
            for j in range(len(words[i])):
                #Convert character to ASCII value
                letter_n = ord(words[i][j])
                #Convert key character to ASCII value
                key_n = ord(key[j % len(key)])

                #Vigenere Cipher Encryption
                value = (letter_n + key_n) % 128
                print("Karakter ", chr(letter_n), "(", letter_n, ")", " dengan Key ", chr(key_n), "(", key_n, ")", " = ", chr(value), "(", value, ")")

                #Convert ASCII value back to character and add character to ciphertext
                word += chr(value)

            #Add ciphertext to ciphertext list
            result_encrypt.append(word)
            
        print("Hasil encrypt : ", result_encrypt)
        return result_encrypt

    else:
        print("\nDekripsi")
        print("List Ciphertext : ", words)
        #Loop through all ciphertext index
        for i in range(len(words)):
            word = ''
            #Loop through each ciphertext character
            for j in range(len(words[i])):
                #Convert ciphertext character to ASCII value
                letter_n = ord(words[i][j])
                #Convert key character to ASCII value
                key_n = ord(key[j % len(key)])

                #Vigenere Cipher Decryption
                value = (letter_n - key_n) % 128
                print("Ciphertext ", chr(letter_n), "(", letter_n, ")", " dengan Key ", chr(key_n), "(", key_n, ")", " = ", chr(value), "(", value, ")")

                #Convert ASCII value back to character and add character to word
                word += chr(value)

            #Add word to word list
            result_decrypt.append(word)
            
        print("Hasil decrypt : ", result_decrypt)
        return result_decrypt
          

def encryption(text, key):
    return vigenere(words=text, key=key, encrypt=True)

def decryption(text, key):
    return vigenere(words=text, key=key, encrypt=False)

def lsb_hide(frame, data):
    print("Menyembunyikan ", data)

    #Convert word to binary
    binary_data=str_to_binary(data)

    print("Binary ",data," : ", binary_data)
    length_data = len(binary_data)
    
    index_data = 0

    #Looping through each row in frame
    for row in frame:
        #Looping through each pixel in frame row
        for pixel in row:
            #Convert pixel to binary
            b, g, r = pixel_to_binary(pixel)
            if index_data < length_data:
                #Substitute B last bit binary with 1 bit character binary from word
                pixel[0] = int(b[:-1] + binary_data[index_data], 2)
                index_data += 1
            if index_data < length_data:
                #Substitute G last bit binary with 1 bit character binary from word
                pixel[1] = int(g[:-1] + binary_data[index_data], 2)
                index_data += 1
            if index_data < length_data:
                #Substitute R last bit binary with 1 bit character binary from word
                pixel[2] = int(r[:-1] + binary_data[index_data], 2)
                index_data += 1
            #If all bit in character binary from word has been substituted, then stop
            if index_data >= length_data:
                break
  
    return frame

def hide(vid, n, data, key):
    print("Memulai proses menyembunyikan pesan rahasia...")

    #Initialize video capture
    vidcap = cv2.VideoCapture(vid)
    
    #Initialize video codec
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    
    frame_width = int(vidcap.get(3))
    frame_height = int(vidcap.get(4))
    size = (frame_width, frame_height)
    fps = int(vidcap.get(cv2.CAP_PROP_FPS))
    
    #Initialize video writer
    out = cv2.VideoWriter('stego_TEMP.avi', fourcc, fps=fps, frameSize=size)

    #Delimiter to help reveal secret message
    first_delimiter = "^$^"
    word_delimiter = "^*^"
    frame_delimiter = "^#^"

    #Normalize message to ASCII
    data=unicodedata.normalize('NFKD', data).encode('ascii', 'ignore').decode('ascii')

    #For pop-up information display
    secret_message = data

    #Separate messages by word
    data = data.split()

    #Declare metadata
    stego_start = [str(n)]
    #Encrypt metadata
    stego_start=encryption(stego_start, key)
    stego_start_str="".join(stego_start)
    #Add delimiter to encrypted metadata
    stego_start_str=first_delimiter+stego_start_str+word_delimiter
    
    print(data)

    #Encrypt message that have been separated by word
    data=encryption(data, key)
    
    print("\nTeks yang telah dienkripsi : ",data)

    #Add delimiter to encrypted message
    for i in range (len(data)):
        if i==(len(data)-1):
            data[i] += frame_delimiter
        else:
            data[i] +=word_delimiter

    print("Setelah ditambahkan delimiter : ", data)
    print("Total ", len(data), " kata\n")

    frame_number = 0
    #Looping through all video input frame
    while(vidcap.isOpened()):
        frame_number += 1
        #Read frame data
        ret, frame = vidcap.read()
        #If video capture cant get frame, then stop
        if ret == False:
            break
        #If frame 1 is found, then hide metadata
        elif frame_number == 1:
            print("\nFrame ", frame_number)
            change_frame_with = lsb_hide(frame, stego_start_str)
            frame = change_frame_with
        #If frame that already specified as the first frame to hide the message is found (metadata), then hide word
        elif (frame_number>=n) and (frame_number<n+len(data)):
            print("\nFrame ", frame_number)
            change_frame_with = lsb_hide(frame, data[frame_number-n])
            frame = change_frame_with
        #Write frame to new video (steganography video)
        out.write(frame)

    #Stop process
    cv2.destroyAllWindows()
    vidcap.release()
    out.release()

    print("\nPesan telah berhasil disembunyikan")
    
    #Insert audio into steganography video
    combine_video_audio(vid)
    
    return secret_message

def lsb_show(frame):

    #Delimiter
    word_delimiter = "^*^"
    frame_delimiter = "^#^"
    
    data_binary = ""
    data = ""

    #Looping through each row in frame
    for row in frame:
        #Looping through each pixel in frame row
        for pixel in row:
            #Convert pixel to binary
            b, g, r = pixel_to_binary(pixel)

            #Get last bit binary from B, G, and R
            data_binary += b[-1]
            data_binary += g[-1]
            data_binary += r[-1]

            #Separate all binary that has been obtained to 7 digit each index list
            total_bytes = [data_binary[i: i+7] for i in range(0, len(data_binary), 7)]
            
            decoded_data = ""
            #Looping through each index
            for byte in total_bytes:
                #Convert index to character
                decoded_data += chr(int(byte, 2))
                #If last 3 character contain word delimiter, then tell the system to find word in next frame and return index without the delimiter
                if decoded_data[-3:] == word_delimiter:
                    for i in range(0,len(decoded_data)-3):
                        data += decoded_data[i]
                    show.next = True
                    return data
                #If last 3 character contain frame delimiter, then tell the system to stop finding word and return index without the delimiter
                elif decoded_data[-3:] == frame_delimiter:
                    for i in range(0,len(decoded_data)-3):
                        data += decoded_data[i]
                    show.next = False
                    return data

def lsb_show_first_frame(frame):

    #Delimiter
    first_delimiter = "^$^"
    word_delimiter = "^*^"
    
    data_binary = ""
    data = ""

    #Looping through each row in frame
    for row in frame:
        #Looping through each pixel in frame row
        for pixel in row:
            #Convert pixel to binary
            b, g, r = pixel_to_binary(pixel)

            #Get last bit binary from B, G, and R
            data_binary += b[-1]
            data_binary += g[-1]
            data_binary += r[-1]

            #Separate all binary that has been obtained to 7 digit each index list
            total_bytes = [data_binary[i: i+7] for i in range(0, len(data_binary), 7)]
            
            decoded_data = ""
            #Looping through each index
            for byte in total_bytes:
                #Convert index to character
                decoded_data += chr(int(byte, 2))
                if len(decoded_data) > 3:
                    #If first 3 character contain first delimiter, then it's a steganography video and there's secret message hidden
                    if decoded_data[:3] == first_delimiter:
                        #If last 3 character contain word delimiter, then return index without the delimiter
                        if decoded_data[-3:] == word_delimiter:
                            for i in range(0,len(decoded_data)-6):
                                data += decoded_data[i+3]
                            return data
                    #If first 3 character didn't contain first delimiter, then it's not a steganography video and there's no secret message hidden
                    else:
                        return False
    return False

def show(vid, key):
    print("Menampilkan pesan tersembunyi pada file : ", vid)
    print("Key : ", key)

    #Initialize video capture
    vidcap = cv2.VideoCapture(vid)
    
    frame_number = 0
    result = []
    #Looping through all steganography video frame
    while(vidcap.isOpened()):
        frame_number += 1
        #Read frame data
        ret, frame = vidcap.read()
        #If video capture cant get frame, then stop
        if ret == False:
            break
        #If frame 1 is found, get encrypted metadata
        if frame_number == 1:
            print("\nFrame ", frame_number)
            #Decrypt metadata
            data = decryption([str(lsb_show_first_frame(frame))], key)
            if str(data[0]).isdigit() == True:
                n = int(data[0])
            else:
                return ("-")
        #If frame number metadata found, get ciphertext
        elif frame_number >= n:
            print("\nFrame ", frame_number)
            result.append(lsb_show(frame))
            print(result[-1])
            #If frame delimiter found, then stop
            if show.next == False:
                #Decrypt ciphertext
                secret_message = decryption(result, key)
                #Join all word to string
                secret_message = " ".join(secret_message)
                print("\nPesan yang disembunyikan ialah : ", secret_message)
                break

    #Stop process
    cv2.destroyAllWindows()
    vidcap.release()
    
    return secret_message

def combine_video_audio(vid):
    print("Memulai proses menggabungkan audio...")
    my_clip = VideoFileClip(vid)

    #Get audio from input video
    my_clip.audio.write_audiofile("audio_TEMP.mp3", logger=None)

    #Define new audio
    audioclip = AudioFileClip("audio_TEMP.mp3")

    #Define steganography video
    videoclip = VideoFileClip("stego_TEMP.avi")

    #Combine new audio and steganography video
    new_audioclip = CompositeAudioClip([audioclip])
    videoclip.audio = new_audioclip

    #Write new video with audio from input video and video from steganography video
    videoclip.write_videofile("video_steganography.avi", codec="ffv1", logger=None)

    #Remove temporary file
    os.remove("audio_TEMP.mp3")
    os.remove("stego_TEMP.avi")
    
    print("Semua proses telah selesai")
    print("Video Steganografi tersimpan dengan nama file", "video_steganography.avi")

def hide_gui(filename):
    #Initialize window
    window = Tk()
    if filename == "":
        window.destroy()
    else:   
        window.title('Hide Secret Message') 
        window.geometry("440x500")

        #Pop up if message succesfully hidden
        def hiding_secret_message(secret_message):
            msgbox = messagebox.showinfo("Secret Message",  "Secret message that have been successfully hidden:\n\n"+secret_message)
            if msgbox == "ok":
                window.destroy()

        #Check metadata field    
        def only_numbers(inStr,acttyp):
            if acttyp == '1':
                if not inStr.isdigit():
                    return False
                elif inStr == '0':
                    return False
                elif int(inStr) > frames:
                    return False
            return True

        #Check max secret message words
        def max_words(inStr,acttype):
            if acttyp == '1':
                if len(inStr.split()) > frames-int(spinbox.get()):
                    return False
            return True

        #Field validation
        def general_validate(filename, spinbox, input_pesan, input_key, frames):
            if len (filename) == 0:
                msgbox = messagebox.showerror("Error",  "Please input all required data.")
            elif len (spinbox) == 0:
                msgbox = messagebox.showerror("Error",  "Please input all required data.")
            elif len (input_pesan) == 0:
                msgbox = messagebox.showerror("Error",  "Please input all required data.")
            elif len (input_key) == 0:
                msgbox = messagebox.showerror("Error",  "Please input all required data.")
            elif spinbox == '1':
                msgbox = messagebox.showerror("Error",  "Cannot select frame 1 as the first frame to hide the message.\n\nPlease select another frame.")
            elif len(input_pesan.split()) > (frames-int(spinbox)+1):
                msgbox = messagebox.showerror("Error",  "The maximum limit of words that can be hidden exceeds the limit.\n\nNumber of Words: "+str(len(input_pesan.split()))+"\nMaximum Limit Number of Words: "+str(frames-int(spinbox)+1))
            else:
                hiding_secret_message(hide(filename, int(spinbox), str(input_pesan), str(input_key)))
                
        vidcap = cv2.VideoCapture(filename)
        frame_width = int(vidcap.get(3))
        frame_height = int(vidcap.get(4))
        fps = int(vidcap.get(cv2.CAP_PROP_FPS))

        #Calculate total frame
        frames=0
        while(vidcap.isOpened()):
            ret, frame = vidcap.read()
            if ret == False:
                break
            frames+=1
        cv2.destroyAllWindows()
        vidcap.release()

        #Initialize widget
        label_file_explorer = Label(window, text="Directory: "+filename)
        label_video_resolution = Label(window, text="Video resolution: "+str(frame_width)+"x"+str(frame_height))
        label_video_frames = Label(window, text="Total frame: "+str(frames))
        label_video_fps = Label(window, text="Frame per second: "+str(fps))
        scrollbar = Scrollbar(window)
        validation_only_numbers = window.register(only_numbers)
        spinbox = Spinbox(window, from_= 2, to=frames, wrap=True, width=6, validate="key", validatecommand=(validation_only_numbers, '%P','%d'))
        input_pesan = Text(window, height = 5, width = 50, yscrollcommand=scrollbar.set)
        scrollbar.config(command=input_pesan.yview)
        input_key = Text(window, height = 1, width = 50)
        button_hide = Button(window, text = "Hide", font=("Helvetica", 16), width=20, height=2, command =lambda: general_validate(filename, spinbox.get(), input_pesan.get("1.0",'end-1c'), input_key.get("1.0",'end-1c'), frames))

        #Show widget
        label_title = Label(window, text = "Hide Secret Message", font=("Helvetica", 20)).grid(row=1, column=1, pady=16)
        label_file_explorer.grid(row=2, column=1)
        label_video_resolution.grid(row=3, column=1)
        label_video_frames.grid(row=4, column=1)
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

def show_gui(filename):
    #Initialize window
    window = Tk()
    if filename == "":
        window.destroy()
    else:
        window.title('Show Secret Message') 
        window.geometry("440x300")

        #Pop up if message succesfully obtained
        def showing_secret_message(secret_message):
            msgbox = messagebox.showinfo("Secret Message",  "Secret message that have been successfully obtained:\n\n"+secret_message)
            if msgbox == "ok":
                window.destroy()

        #Field validation
        def general_validate(filename, input_key, frames):
            if len (filename) == 0:
                msgbox = messagebox.showerror("Error",  "Please input all required data.")
            elif len (input_key) == 0:
                msgbox = messagebox.showerror("Error",  "Please input all required data.")
            else:
                showing_secret_message(show(filename, str(input_key)))
            
        vidcap = cv2.VideoCapture(filename)
        frame_width = int(vidcap.get(3))
        frame_height = int(vidcap.get(4))
        fps = int(vidcap.get(cv2.CAP_PROP_FPS))

        #Calculate total frame
        frames=0
        while(vidcap.isOpened()):
            ret, frame = vidcap.read()
            if ret == False:
                break
            frames+=1
        cv2.destroyAllWindows()
        vidcap.release()

        #Initialize widget
        label_file_explorer = Label(window, text="Directory: "+filename)
        label_video_resolution = Label(window, text="Video resolution: "+str(frame_width)+"x"+str(frame_height))
        label_video_frames = Label(window, text="Total frame: "+str(frames))
        label_video_fps = Label(window, text="Frame per second: "+str(fps))
        input_key = Text(window, height = 1, width = 50)
        button_show = Button(window, text = "Show", font=("Helvetica", 16), width=20, height=2, command =lambda: general_validate(filename, input_key.get("1.0",'end-1c'), frames))

        #Show widget
        label_title = Label(window, text = "Show Secret Message", font=("Helvetica", 20)).grid(row=1, column=1, pady=16)
        label_file_explorer.grid(row=2, column=1, padx=15)
        label_video_resolution.grid(row=3, column=1)
        label_video_frames.grid(row=4, column=1)
        label_video_fps.grid(row=5, column=1)
        label_title_key = Label(window, text = "Key").grid(row=6, column=1, padx=15, pady=(10,0), sticky='w')
        input_key.grid(row=7, column=1, padx=15, sticky='w')
        button_show.grid(row=8, column=1, padx=15, pady=(15,0))
        
        window.mainloop()

def browse_file(hide=True):
    #Show open input video file window
    if hide:
        filename = filedialog.askopenfilename(initialdir = "C:/Users/Komandan3/Skripsion",
                                          title = "Select an Input Video",
                                          filetypes=[("Video file", ".avi .mp4")])

    #Show open steganography video file window
    else:
        filename = filedialog.askopenfilename(initialdir = "C:/Users/Komandan3/Skripsion",
                                          title = "Select a Steganography Video",
                                          filetypes=[("Video file", ".avi")])
    return filename

def hide_file():
    #If function called in hide secret message button
    return browse_file(hide=True)

def show_file():
    #If function called in show secret message button
    return browse_file(hide=False)

def gui():
    #Initialize window
    window = Tk()
    window.title('Video Steganography')
    window.geometry("300x300")
    
    label_title = Label(window, text = "Video Steganography", font=("Helvetica", 20)).pack(pady=16)

    #Hide secret message button
    button_hide_gui = Button(window, text = "Hide Secret Message", font=("Helvetica", 16), command = lambda: [hide_gui(hide_file())], width=20, height=3).pack(pady=8)

    #Show secret message button
    button_show_gui = Button(window, text = "Show Secret Message", font=("Helvetica", 16), command = lambda: [show_gui(show_file())], width=20, height=3).pack(pady=8)
    
    window.mainloop()

#Main function
if __name__ == "__main__":
    gui()
