
# From https://www.geeksforgeeks.org/image-based-steganography-using-python/

# Python program implementing Image Steganography
 
# PIL module is used to extract
# pixels of image and modify it
from asyncore import loop
from operator import truediv
from PIL import Image
import math
# Convert encoding data into 8-bit binary form using ASCII value of characters
def asci_to_binary(secret_message):
        # Converts each ascii letter into binary data that can be appended to the message.
        binary_data = []
        for character in secret_message:
            binary_data.append(format(ord(character), '08b'))
        return binary_data
 
# Pixels are modified according to the 8-bit binary data and finally returned
def modPix(picture, secret_message):
    binary_data = asci_to_binary(secret_message)
    data_length = len(binary_data)
    data_from_image = iter(picture)
    i = 1
    loop_counter = 0
    pixel_number = 0
    # SO the issue is that we run through the image datalength before hitting a non transparent pixel
    while loop_counter < data_length:
        # Extracting 3 pixels at a time
        # data_from_image.__next__()[:3] pulls the last 3 bytes from that color channel the pixel Ex: (254, 255, 254)
        picture = [value for value in data_from_image.__next__()[:3] +
                                data_from_image.__next__()[:3] +
                                data_from_image.__next__()[:3]]
        pixel_number += 3
        # Pixel value should be made odd for 1 and even for 0
        has_transparency = False
        for i in picture:
            if i > 250:
                has_transparency=True
        if not has_transparency:
            print("Data " + str(i) + " Pre Encoded: " + str(picture))
            for j in range(0, 8):
                if (binary_data[loop_counter][j] == '0' and picture[j]% 2 != 0):
                    picture[j] -= 1
    
                elif (binary_data[loop_counter][j] == '1' and picture[j] % 2 == 0):
                    if(picture[j] != 0):
                        picture[j] -= 1
                    else:
                        picture[j] += 1
                    # pix[j] -= 1
    
            # Eighth pixel of every set tells whether to stop ot read further. 0 means keep reading; 1 means the message is over.
            if (i == data_length - 1):
                if (picture[-1] % 2 == 0):
                    if(picture[-1] != 0):
                        picture[-1] -= 1
                    else:
                        picture[-1] += 1
    
            else:
                if (picture[-1] % 2 != 0):
                    picture[-1] -= 1
    
            picture = tuple(picture)
            print("Data " + str(i) + " Encoded: " + str(picture))
            yield (picture[0:3], pixel_number)
            yield (picture[3:6], pixel_number)
            yield (picture[6:9], pixel_number)
            loop_counter = loop_counter + 1
        i = i + 1 
 
def encode_enc(newimg, data):
    image_width = newimg.size[0]
    (x, y) = (0, 0)
    # data_from_image = iter(newimg.getdata())
    pixel_counter = 0
    for pixel in modPix(newimg.getdata(), data):
        x = pixel[1] + pixel_counter
        print("pixel Number:", pixel[1])
        print("image width:", image_width)
        if (x > image_width - 1):
            y = math.floor(x/image_width)
            x = x % (image_width)
            print(y)
        else:
            x = pixel[1] + pixel_counter
        # newimg.putpixel((x, y), pixel[0])
        newimg.putpixel((x, y), (255, 0, 0))
        pixel_counter += 1
        if pixel_counter == 3:
            pixel_counter = 0
        
        
 
# Encode data into image
def encode():
    # file_name = input("Enter image name(with extension) : ")
    file_name = "cat.png"
    image = Image.open(file_name, 'r')
 
    # secret_message = input("Enter data to be encoded : ")
    secret_message = "Hello there!"
    secret_message = secret_message + secret_message[-1]+ secret_message + secret_message[-1]+ secret_message+ secret_message[-1]
    if (len(secret_message) == 0):
        raise ValueError('Data is empty')
 
    stego_file = image.copy()
    encode_enc(stego_file, secret_message)
 
    stego_file_name = input("Enter the name of new image(with extension) : ")
    # First Param Filename, second param is the extension
    stego_file.save(stego_file_name, str(stego_file_name.split(".")[1].upper()))
 

# # Decode the data in the image
def decode():
    stego_file_name = input("Enter image name(with extension) : ")
    stego_file = Image.open(stego_file_name, 'r')
 
    plain_text = ''
    imgdata = iter(stego_file.getdata())
    
    # skip_three = False
    while (True):
        pixels = [value for value in imgdata.__next__()[:3] +
                                imgdata.__next__()[:3] +
                                imgdata.__next__()[:3]]
        if skip_three:
            skip_three = False
            continue
        skip_three = True
        # string of binary data
        binstr = ''
        has_transparency = False
        for i in pixels:
            if i > 250:
                has_transparency=True
            if not has_transparency:
                # Odd = 1, even = 0.
                for i in pixels[:8]:
                    if (i % 2 == 0):
                        binstr += '0'
                    else:
                        binstr += '1'
        
                plain_text += chr(int(binstr, 2))
                if (pixels[-1] % 2 != 0):
                    return plain_text[:-2]

# def decode():
#     stego_file_name = input("Enter image name(with extension) : ")
#     stego_file = Image.open(stego_file_name, 'r')
 
#     plain_text = ''
#     imgdata = iter(stego_file.getdata())
 
#     while (True):
#         pixels = [value for value in imgdata.__next__()[:3] +
#                                 imgdata.__next__()[:3] +
#                                 imgdata.__next__()[:3]]
        
#         # string of binary data
#         binstr = ''
#         # Odd = 1, even = 0.
#         for i in pixels[:8]:
#             if (i % 2 == 0):
#                 binstr += '0'
#             else:
#                 binstr += '1'
 
#         plain_text += chr(int(binstr, 2))
#         if (pixels[-1] % 2 != 0):
#             return plain_text
        

# Main Function
def main():
    a = int(input(":: Welcome to Steganography ::\n"
                        "1. Encode\n2. Decode\n"))
    if (a == 1):
        encode()
 
    elif (a == 2):
        print("Decoded Word :  " + decode())
    else:
        raise Exception("Enter correct input")
 
# Driver Code
if __name__ == '__main__' :
 
    # Calling main function
    main()