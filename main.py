# From https://www.geeksforgeeks.org/image-based-steganography-using-python/

# Python program implementing Image Steganography

# PIL module is used to extract
# pixels of image and modify it



from asyncore import loop
from operator import truediv
from PIL import Image
import math



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
        
        
 
# Encode data into image
def encode():
    file_name = input("Enter image name (with extension): ")
    #file_name = "cat.png"
    image = Image.open(file_name, 'r')
 
    secret_message = input("Enter data to be encoded: ")
    #secret_message = "Hello! Hello! Hello! Hello! Hello! Hello! Hello! Hello!"
    #secret_message = secret_message + secret_message[-1]+ secret_message + secret_message[-1]+ secret_message+ secret_message[-1]
    if (len(secret_message) == 0):
        raise ValueError('Data is empty')
 
    stego_file = image.copy()
    secret_message = secret_message + "!ENDOFMESSAGE!"
    encode_enc(stego_file, secret_message)  
    stego_file_name = input("Enter the name of the new image (with extension): ")
    # First Param Filename, second param is the extension
    stego_file.save(stego_file_name, str(stego_file_name.split(".")[1].upper()))
 


# # Decode the data in the image
def decode():
    stego_file_name = input("Enter image name (with extension): ")
    stego_file = Image.open(stego_file_name, 'r')
    pixel_number = 0
    plain_text = ''
    imgdata = iter(stego_file.getdata())
    
    
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
                    print("Decode last Pixel #:", pixel_number)
                    print("last Data to be decoded: " + str(group_three_pixels))

                    #print("plain_text hex: ", plain_text.encode("utf-8").hex())
                    plain_text_filtered = plain_text.split("!ENDOFMESSAGE!")[0]
                    return plain_text_filtered

                else:
                    print("Decode Pixel #:", pixel_number)
                    print("Data to be decoded: " + str(group_three_pixels))



# Main Function
def main():
    a = int(input(":: Welcome to Steganography ::\n"
                        "1. Encode\n2. Decode\n"))
    if (a == 1):
        encode()
 
    elif (a == 2):
        print(f"Decoded Word: \"{decode()}\"")
    else:
        raise Exception("Enter correct input")
 


# Driver Code
if __name__ == '__main__' :
 
    # Calling main function
    main()
