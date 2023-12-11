# From https://www.geeksforgeeks.org/image-based-steganography-using-python/

# Python program implementing Image Steganography

# PIL module is used to extract
# pixels of image and modify it



from asyncore import loop
from operator import truediv
from PIL import Image
import numpy as np
import math
import struct



# Convert encoding data into 8-bit binary form using ASCII value of characters
def ascii_to_binary(secret_message):
        # Converts each ascii letter into binary data that can be appended to the message.
        binary_data = []
        for character in secret_message:
            binary_data.append(format(ord(character), '08b'))
        return binary_data



# Pixels are modified according to the 8-bit binary data and finally returned
def modPix(group_three_pixels, secret_message, using_gif):
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
                has_transparency = True

        if (not has_transparency) or (has_transparency and using_gif):
            print("Data " + str(i) + " Pre Encoded: " + str(group_three_pixels))
            
            # Pixel value should be made odd for 1 and even for 0
            for j in range(0, 8):
                if (binary_data[loop_counter][j] == '0' and group_three_pixels[j] % 2 != 0):
                    group_three_pixels[j] -= 1
    
                elif (binary_data[loop_counter][j] == '1' and group_three_pixels[j] % 2 == 0):
                    if(group_three_pixels[j] != 0):
                        group_three_pixels[j] -= 1

                    else:
                        group_three_pixels[j] += 1
                    # pix[j] -= 1
    
            # Eighth pixel of every set tells whether to stop to read further. 0 means keep reading; 1 means the message is over.
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
            # yield is like return for generators.
            # remember we increment pixel_number by 3, so we need to decrement it here to get the right pixel number
            yield (group_three_pixels[0:3], pixel_number-2)
            yield (group_three_pixels[3:6], pixel_number-1)
            yield (group_three_pixels[6:9], pixel_number)

            # only increment the loop counter when we hit a non transparent pixel.
            loop_counter = loop_counter + 1
        
        i = i + 1 



def encode_enc(newimg, data, using_gif):
	image_width = newimg.size[0]
	(x, y) = (0, 0)
    # data_from_image = iter(newimg.getdata())

    # Counts where we are in the current image (i dont think we need this because of the new param)
    # pixel_counter = 0
	
	if using_gif:
		for pixel in modPix(newimg.getdata(), data, True):
			print("pixel number: ", pixel[1])

			x = pixel[1]

			if (x > image_width - 1):
				y = math.floor(x / image_width)
				x = x % (image_width)
				print(y)
			else:
				x = pixel[1]

			# Uncomment the below like for writing real data    
			#newimg.putpixel((x-1, y), pixel[0])
			# uncomment the below line to yellow test pixels to see where data is being written
			newimg.putpixel((x, y), (245, 245, 0))

	else:
		for pixel in modPix(newimg.getdata(), data, False):
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
			#newimg.putpixel((x, y), (245, 245, 0))
			# pixel_counter += 1
			# if pixel_counter == 3:
			#     pixel_counter = 0

    # need to return newimg for GIF encoding
	return newimg



def get_gif_size(file_name):
	gif_size = []
	with open(file_name, 'rb') as f:
		# Skip the GIF header (6 bytes: GIF87a or GIF89a)
		f.read(6)

		# Read logical screen descriptor
		screen_width = int.from_bytes(f.read(2), 'little')
		gif_size.append(screen_width)
		screen_height = int.from_bytes(f.read(2), 'little')
		gif_size.append(screen_height)

	return gif_size



# helper function for enc_gif()
def get_gif_GCT_size(file_name):
	with open(file_name, 'rb') as f:
		# Skip GIF header (6 bytes: GIF87a or GIF89a)
		f.read(6)

		# Read logical screen descriptor
		screen_width, screen_height = struct.unpack('<HH', f.read(4))
		packed_fields = struct.unpack('<B', f.read(1))[0]
		bg_color_index = struct.unpack('<B', f.read(1))[0]
		pixel_aspect_ratio = struct.unpack('<B', f.read(1))[0]

		# Check if Global Color Table exists (bit 7 of packed_fields)
		gct_flag = (packed_fields & 0b10000000) >> 7

		if gct_flag:
			# Determine the size of the Global Color Table
			gct_size_bits = packed_fields & 0b00000111
			gct_size = 2 ** (gct_size_bits + 1)
			return gct_size

		else:
			raise ValueError('Gif\'s global color table could not be found.')



def get_gif_GCT(file_path):
	with open(file_path, 'rb') as f:
		# Skip GIF header (6 bytes: GIF87a or GIF89a)
		f.read(6)

		# Read logical screen descriptor
		screen_width, screen_height = struct.unpack('<HH', f.read(4))
		packed_fields = struct.unpack('<B', f.read(1))[0]
		bg_color_index = struct.unpack('<B', f.read(1))[0]
		pixel_aspect_ratio = struct.unpack('<B', f.read(1))[0]

		# Check if Global Color Table exists (bit 7 of packed_fields)
		gct_flag = (packed_fields & 0b10000000) >> 7

		if gct_flag:
			# Determine the size of the Global Color Table
			gct_size_bits = packed_fields & 0b00000111
			gct_size = 2 ** (gct_size_bits + 1)

			print(f'Global Color Table Size: {gct_size} colors')

			# Read Global Color Table
			gct_data = f.read(3 * gct_size) # Each color is 3 bytes (RGB)

			# Create a list of RGB triplets
			gct_colors = [(gct_data[i], gct_data[i + 1], gct_data[i + 2]) for i in range(0, len(gct_data), 3)]

			#gct_colors = []
			#for i in range(0, len(gct_data), 3):
				#gct_colors.append(gct_data[i])
				#gct_colors.append(gct_data[i + 1])
				#gct_colors.append(gct_data[i + 2])

			# Print or use Global Color Table as needed
			#for i, color in enumerate(gct_colors):
				#print(f'Color {i}: R={color[0]} G={color[1]} B={color[2]}')

			return gct_colors

		else:
			print('No Global Color Table present.')
			return []




def enc_gif(file_name, secret_message):
	original = Image.open(file_name)

	new = []

	# get gif size
	gif_size = get_gif_size(file_name)

	# get gif color table size
	gif_GCT_size = get_gif_GCT_size(file_name)

	# get gif color table values
	gif_GCT = get_gif_GCT(file_name)

	#print(f'gif_GCT = {gif_GCT}')

	for frame_num in range(original.n_frames):
		original.seek(frame_num)

		new_frame = Image.new('RGBA', original.size)
		new_frame.paste(original)

		# only encode the message into the first frame
		if frame_num == 0:
			new_frame = encode_enc(new_frame, secret_message, True)			
			#new_frame.thumbnail((gif_size[0], gif_size[1])) # resize to the size of the gif
			#new_frame = new_frame.convert(Image.ADAPTIVE, palette = gif_GCT, colors = gif_GCT_size)
			new.append(new_frame)

		else:
			#new_frame.thumbnail((gif_size[0], gif_size[1])) # resize to the size of the gif
			#new_frame = new_frame.convert(Image.ADAPTIVE, palette = gif_GCT, colors = gif_GCT_size)
			new.append(new_frame)
	
	new[0].save('output.gif', format = 'GIF', append_images = new[1:], save_all = True, duration = original.n_frames, loop = 0)

# Encode data into image
def encode():
	file_name = input("Enter image name (with extension): ")
	image = Image.open(file_name, 'r')

	secret_message = input("Enter data to be encoded: ")
	#secret_message = "Hello! Hello! Hello! Hello! Hello! Hello! Hello! Hello!"
	#secret_message = secret_message + secret_message[-1]+ secret_message + secret_message[-1]+ secret_message+ secret_message[-1]
	if (len(secret_message) == 0):
		raise ValueError('Data is empty')

	if file_name[-3:].lower() == 'gif':
		secret_message = secret_message + "!ENDOFMESSAGE!"
		enc_gif(file_name, secret_message)

	else:
		stego_file = image.copy()
		secret_message = secret_message + "!ENDOFMESSAGE!"
		encode_enc(stego_file, secret_message, False)  
		stego_file_name = input("Enter the name of the new image (with extension): ")
		# First Param Filename, second param is the extension
		stego_file.save(stego_file_name, str(stego_file_name.split(".")[1].upper()))
 


# # Decode the data in the image
def decode():
	pixel_number = 0
	plain_text = ''
	dec_gif = False

	stego_file_name = input("Enter image name (with extension): ")

	if stego_file_name[-3:].lower() == 'gif':
		dec_gif = True
		original = Image.open(stego_file_name)

		original.seek(0)

		new_frame = Image.new('RGBA', original.size)
		new_frame.paste(original)

		new_frame.save('test.png')

		imgdata = iter(new_frame.getdata())

		while (True):
			group_three_pixels = [value for value in imgdata.__next__()[:3] + imgdata.__next__()[:3] + imgdata.__next__()[:3]]
			binstr = ''
			pixel_number += 3
			for channel_values in group_three_pixels[:8]:

				if (channel_values % 2 == 0):
					binstr += '0'
				else:
					binstr += '1'

			plain_text += chr(int(binstr, 2))

			#if (group_three_pixels[-1] % 2 != 0):
			if "!ENDOFMESSAGE!" in plain_text:
				print("Decode last Pixel #:", pixel_number)
				print("last Data to be decoded: " + str(group_three_pixels))

				#print("plain_text hex: ", plain_text.encode("utf-8").hex())
				plain_text_filtered = plain_text.split("!ENDOFMESSAGE!")[0]
				return plain_text_filtered

			else:
				print("Decode Pixel #:", pixel_number)
				print("Data to be decoded: " + str(group_three_pixels))

	else:
		stego_file = Image.open(stego_file_name, 'r')
		imgdata = iter(stego_file.getdata())

		while (True):
			group_three_pixels = [value for value in imgdata.__next__()[:3] +
									imgdata.__next__()[:3] +
									imgdata.__next__()[:3]]
			binstr = ''
			pixel_number += 3
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
				#if "!ENDOFMESSAGE!" in plain_text:
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
