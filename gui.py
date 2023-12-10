
# From https://www.geeksforgeeks.org/image-based-steganography-using-python/

# Python program implementing Image Steganography

# PIL module is used to extract
# pixels of image and modify it



from asyncore import loop
from operator import truediv
from PIL import Image
import math
import tkinter as tk
from tkinter import Toplevel, filedialog, messagebox
from tkinter import font as tkFont
import os



# Convert encoding data into 8-bit binary form using ASCII value of characters
def ascii_to_binary(secret_message):
        # Converts each ascii letter into binary data that can be appended to the message.
        binary_data = []
        for character in secret_message:
            binary_data.append(format(ord(character), '08b'))
        return binary_data



# Pixels are modified according to the 8-bit binary data and finally returned
def modPix(group_three_pixels, secret_message):
    binary_data = ascii_to_binary(secret_message)
    data_length = len(binary_data)
    data_from_image = iter(group_three_pixels)

    # Counts how many chunks of 3 pixels we ran through
    i = 1

    # counts how many non transparent pixels we stored info to
    loop_counter = 0
    # Counts how many pixels we passed. Used for calculating where to put the pixels
    pixel_number = 0
    # SO the issue is that we run through the image datalength before hitting a non transparent pixel
    while loop_counter < data_length:
        # Extracting 3 pixels at a time
        # data_from_image.__next__()[:3] pulls the last 3 bytes from that color channel the pixel Ex: (254, 255, 254)
        group_three_pixels = [value for value in data_from_image.__next__()[:3] +
                                data_from_image.__next__()[:3] +
                                data_from_image.__next__()[:3]]
        # we grabbed 3 pixels so now we need to add 3 to the total count
        pixel_number += 3

        # Pixels are assumed to not be transparent
        has_transparency = False
        for pixel_channel_value in group_three_pixels:
            #Then we check if the value is larger then 254
            if pixel_channel_value > 180:
                has_transparency=True
        if not has_transparency:
            print("Data " + str(i) + " Pre Encoded: " + str(group_three_pixels))
            
            # Pixel value should be made odd for 1 and even for 0
            for j in range(0, 8):
                if (binary_data[loop_counter][j] == '0' and group_three_pixels[j]% 2 != 0):
                    group_three_pixels[j] -= 1
    
                elif (binary_data[loop_counter][j] == '1' and group_three_pixels[j] % 2 == 0):
                    if(group_three_pixels[j] != 0):
                        group_three_pixels[j] -= 1
                    else:
                        group_three_pixels[j] += 1
                    # pix[j] -= 1
    
            # Eighth pixel of every set tells whether to stop ot read further. 0 means keep reading; 1 means the message is over.
            if (i == data_length - 1):
                if (group_three_pixels[-1] % 2 == 0):
                    if(group_three_pixels[-1] != 0):
                        group_three_pixels[-1] -= 1
                    else:
                        group_three_pixels[-1] += 1
    
            else:
                if (group_three_pixels[-1] % 2 != 0):
                    group_three_pixels[-1] -= 1
    
            group_three_pixels = tuple(group_three_pixels)
            print("Data " + str(i) + " Encoded: " + str(group_three_pixels))
            # yeald is like return for generators.
            # remember we increment pixel_number by 3, so we need to decrement it here to get the right pixel number
            yield (group_three_pixels[0:3], pixel_number-2)
            yield (group_three_pixels[3:6], pixel_number-1)
            yield (group_three_pixels[6:9], pixel_number)

            # only increment the loop counter when we hit a non transparent pixel.
            loop_counter = loop_counter + 1
        
        i = i + 1 



def encode_enc(newimg, data):
    image_width = newimg.size[0]
    (x, y) = (0, 0)
    # data_from_image = iter(newimg.getdata())

    # Counts where we are in the current image (i dont think we need this because of the new param)
    # pixel_counter = 0
    
    for pixel in modPix(newimg.getdata(), data):
        print()
        # Sets the current pixel to the 
        # x = pixel[1] + pixel_counter
        print("pixel Number:", pixel[1])

        # Sets X to the pixel Number
        x = pixel[1]
        print("image width:", image_width)
        if (x > image_width - 1):
            y = math.floor(x/image_width)
            x = x % (image_width)
            print(y)
        else:
            # x = pixel[1] + pixel_counter
            x = pixel[1]
        # Uncomment the below like for writing real data
        newimg.putpixel((x-1, y), pixel[0])
        # uncomment the below line to yellow test pixels to see where data is being written
        # newimg.putpixel((x, y), (245, 245, 0))
        # pixel_counter += 1
        # if pixel_counter == 3:
        #     pixel_counter = 0



def upload_file():
    file_path = filedialog.askopenfilename()
        
    if file_path:
        file_name = os.path.abspath(file_path)
        #file_label.config(text=f"Selected File: {file_path}")
        return file_name



# Encode data into image
def encode():
    top = Toplevel()
    top.title("encode")
    top.geometry("400x500")
    top.configure(bg="sky blue")
    helv36 = tkFont.Font(family='Helvetica', size=15, weight=tkFont.BOLD)
    
    fileIn = tk.StringVar()
    labelFile = tk.Label(top, text = 'Enter image name (with extension):').pack()
    filename = tk.Entry(top, textvariable = fileIn).pack()
    
    messageIn = tk.StringVar()
    labelf = tk.Label(top, text = 'Enter data to be encoded:').pack()
    fname = tk.Entry(top, textvariable = messageIn).pack()
    
    fileOut = tk.StringVar()
    labelOut = tk.Label(top, text = 'Enter the name of the new image (with extension):').pack()
    outname = tk.Entry(top, textvariable = fileOut).pack()

    encoButton = tk.Button(top, text="Encode", command=lambda: [top.destroy(), startEnc(fileIn.get(), fileOut.get(), messageIn.get())])
    encoButton.pack()



def startEnc(selected_file_name, output_file_name, message):
	print(selected_file_name)
	print(output_file_name)
	print(message)
	image = Image.open(selected_file_name, 'r')
	stego_file = image.copy()
	message = message + "!ENDOFMESSAGE!"
	encode_enc(stego_file, message)
	saveFun(stego_file, output_file_name)



def saveFun(saveImg, output_file_name):
    #splitName  = selected_file_name.split('.')
    #stego_file_name = splitName[0] + "_hidden." + splitName[1]
    #stegoFileName = "File is saved to: " + splitName[0] + "_hidden." + splitName[1]
    stegoFileName = "File is saved to: " + output_file_name
    messagebox.showinfo("Done!", stegoFileName)
    saveImg.save(output_file_name, str(output_file_name.split(".")[1].upper()))



def decodePage():
    deco = Toplevel()
    deco.title("Decode")
    deco.geometry("400x500")
    deco.configure(bg="sky blue")
    helv36 = tkFont.Font(family='Helvetica', size=15, weight=tkFont.BOLD)
    fileDecode = tk.StringVar()
    labelFile = tk.Label(deco, text = 'Enter The File Name (Include the path): ').pack()
    filename = tk.Entry(deco, textvariable = fileDecode).pack()
    decoButton = tk.Button(deco, text="Decode", command=lambda: [deco.destroy(), decode(fileDecode.get())])
    decoButton.pack()



# # Decode the data in the image
def decode(stego_file_name):
    stego_file = Image.open(stego_file_name, 'r')
    pixel_number = 0
    plain_text = ''
    imgdata = iter(stego_file.getdata())
    fullout = "Output:"
    
    while (True):
        group_three_pixels = [value for value in imgdata.__next__()[:3] +
                                imgdata.__next__()[:3] +
                                imgdata.__next__()[:3]]
        binstr = ''
        pixel_number +=3
        has_transparent = False
        for channel_values in group_three_pixels:
            # has_transparency = False
            if channel_values > 180:
                has_transparent = True
        if not has_transparent:
                # Odd = 1, even = 0.
                
                for channel_values in group_three_pixels[:8]:
                        
                        if (channel_values % 2 == 0):
                            binstr += '0'
                        else:
                            binstr += '1'
        
                plain_text += chr(int(binstr, 2))
                if (group_three_pixels[-1] % 2 != 0):
                    plain_text_filtered = plain_text.split("!ENDOFMESSAGE!")[0]
                    #fullout += "Decode last Pixel #:" + str(pixel_number) + "\n"
                    #fullout += "last Data to be decoded: " + str(group_three_pixels) + "\n"
                    messagebox.showinfo("Output:", plain_text_filtered)

                    return plain_text_filtered

                else:
                    #fullout += "Decode Piexl #:" + str(pixel_number) + "\n"
                    fullout += "Data to be decoded: " + str(group_three_pixels) + "\n"



# Main Function
def main():
    window = tk.Tk()
    window.title("StegoImage")
    window.geometry("700x500")
    window.configure(bg="sky blue")
    helv36 = tkFont.Font(family='Helvetica', size=15, weight=tkFont.BOLD)
    labelFile = tk.Label(window, font=helv36, text = 'Please Choose an Option:').pack()
    encrypt_button = tk.Button(window, text="Encrypt", height= 20, width=25, font=helv36, command=encode)
    encrypt_button.pack(side = tk.LEFT)

    decrypt_button = tk.Button(window, text="Decrypt", height= 20, width=25, font=helv36, command=decodePage)
    decrypt_button.pack(side = tk.RIGHT)
    window.mainloop()



# Driver Code
if __name__ == '__main__' :
 
    # Calling main function
    main()
