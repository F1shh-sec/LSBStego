
# Base LSB forked from https://github.com/goelashwin36/image-steganography/tree/master

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
def modPix(group_three_pixels, secret_message):
    binary_data = asci_to_binary(secret_message)
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
        # data_from_image.__next__()[:3] pulls the last 3 bytes from 
        # that color channel the pixel Ex: (254, 255, 254)
        group_three_pixels = [value for value in data_from_image.__next__()[:3] +
                                data_from_image.__next__()[:3] +
                                data_from_image.__next__()[:3]]
        # we grabbed 3 pixels so now we need to add 3 to the total count
        pixel_number += 3

        # Pixels are assumed to not be transparent
        has_transparency = False
        for pixel_channel_value in group_three_pixels:
            #Then we check if the value is larger then 180
            if pixel_channel_value > 180:
                has_transparency=True
        if not has_transparency:
            print("Data Pixel Number " + str(pixel_number) + " Pre Encoded: " + str(group_three_pixels))
            
            # Pixel value should be made odd for 1 and even for 0
            for j in range(0, 8):
                if (binary_data[loop_counter][j] == '0' and group_three_pixels[j]% 2 != 0):
                    group_three_pixels[j] -= 1
    
                elif (binary_data[loop_counter][j] == '1' and group_three_pixels[j] % 2 == 0):
                    if(group_three_pixels[j] != 0):
                        group_three_pixels[j] -= 1
                    else:
                        group_three_pixels[j] += 1
    
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
            print("Data Pixel Number " + str(pixel_number) + " Encoded: " + str(group_three_pixels))
            print()
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
    for pixel in modPix(newimg.getdata(), data):
        # print()
        # Sets the current pixel to the 
        # print("pixel Number:", pixel[1])

        # Sets X to the pixel Number
        x = pixel[1]
        # print("image width:", image_width)
        if (x > image_width - 1):
            y = math.floor(x/image_width)
            x = x % (image_width)
            # print(y)
        else:
            x = pixel[1]
        
        # Uncomment the below like for writing real data    
        newimg.putpixel((x-1, y), pixel[0])
        # uncomment the below line to yellow test 
        # pixels to see where data is being written
        # newimg.putpixel((x-1, y), (245, 0, 0))
    return newimg
        

       
def enc_gif(file_name, secret_message):
	original = Image.open(file_name)

	new = []

	#print(f'gif_GCT = {gif_GCT}')

	for frame_num in range(original.n_frames):
		original.seek(frame_num)
		new_frame = Image.new('RGB', original.size)
		new_frame.paste(original)
		# only encode the message into the first frame
		if frame_num == 0:
			new_frame = encode_enc(new_frame, secret_message)			
		new.append(new_frame)
	new[0].save('output.gif', format = 'GIF', append_images = new[1:], save_all = True, duration = original.n_frames, loop = 0)

 
# Encode data into image
def encode():
    file_name = input("Enter image name(with extension) : ")
    # file_name = "giphy.gif"
    image = Image.open(file_name, 'r')
    secret_message = input("Enter data to be encoded : ") + "!ENDOFMESSAGE!"
    # secret_message =  "!ENDOFMESSAGE!"
    if (len(secret_message) == 0):
        raise ValueError('Data is empty')
    if file_name[-3:].lower() == 'gif':
        enc_gif(file_name, secret_message)
        return
    # if file_name[-3:].lower() == 'gif':
    #     stego_file = new_frame.copy()
    # else:
    stego_file = image.copy()
    encode_enc(stego_file, secret_message)
 
    stego_file_name = input("Enter the name of new image(with extension) : ")
    # First Param Filename, second param is the extension
    stego_file.save(stego_file_name, str(stego_file_name.split(".")[1].upper()))
 

# # Decode the data in the image
def decode():
    stego_file_name = input("Enter image name(with extension) : ")
    # stego_file_name = "output.gif"
    stego_file = Image.open(stego_file_name, 'r')
    pixel_number = 0
    plain_text = ''
    imgdata = iter(stego_file.getdata())
    
    if stego_file_name[-3:].lower() == 'gif':
        original = Image.open(stego_file_name, 'r')
        original.seek(0)
        new_frame = Image.new('RGB', original.size)
        new_frame.paste(original)

        new_frame.save('test.png')

        imgdata = iter(new_frame.getdata())
          
    while (True):
        group_three_pixels = [value for value in imgdata.__next__()[:3] +
                                imgdata.__next__()[:3] +
                                imgdata.__next__()[:3]]
        binstr = ''
        pixel_number +=3
        has_transparent = False
        for channel_values in group_three_pixels:
            if channel_values > 180:
                has_transparent = True
        if not has_transparent:
           
                for channel_values in group_three_pixels[:8]:
                        # Odd = 1, even = 0.
                        if (channel_values % 2 == 0):
                            binstr += '0'
                        else:
                            binstr += '1'
        
                plain_text += chr(int(binstr, 2))
                # if (group_three_pixels[-1] % 2 != 0):
                if "!ENDOFMESSAGE!" in plain_text:
                    print("Decode last Piexl #:" + str(pixel_number) + ": "+ str(group_three_pixels))
                    return plain_text.split("!ENDOFMESSAGE!")[0]
                else:
                    print("Decode last Piexl #:" + str(pixel_number) + ": "+ str(group_three_pixels))


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