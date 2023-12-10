# From https://dtm.uk/gif-steganography/

# Python program implementing GIF steganography

import struct
from PIL import Image
import numpy as np
from collections import deque
import os



def read_logical_screen_descriptor(file_path):
	print(f'\n[ READING LOGICAL SCREEN DESCRIPTOR ]')

	with open(file_path, 'rb') as f:
		# Skip the GIF header (6 bytes: GIF87a or GIF89a)
		f.read(6)

		# Read logical screen descriptor
		screen_width = int.from_bytes(f.read(2), 'little')
		screen_height = int.from_bytes(f.read(2), 'little')

		packed_fields = int.from_bytes(f.read(1), 'little')
		gct_flag = (packed_fields & 0b10000000) >> 7
		color_res = (packed_fields & 0b01110000) >> 4
		sort_flag = (packed_fields & 0b00001000) >> 3
		gct_size = packed_fields & 0b00000111

		bg_color_index = int.from_bytes(f.read(1), 'little')
		pixel_aspect_ratio = int.from_bytes(f.read(1), 'little')
		
		print(f'Logical Screen Width: {screen_width}')
		print(f'Logical Screen Height: {screen_height}')
		print(f'Global Color Table Flag: {gct_flag}')
		print(f'Color Resolution: {color_res}')
		print(f'Sort Flag: {sort_flag}')
		print(f'Size of Global Color Table: {gct_size}')
		print(f'Background Color Index: {bg_color_index}')
		print(f'Pixel Aspect Ratio: {pixel_aspect_ratio}')



def read_global_color_table(file_path):
	newdir = file_path.split(".")[0]
	filename = newdir + "/" + file_path[:-4] + '_gct_data.txt'

	print(f'\n[ READING GLOBAL COLOR TABLE ]')

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
			open(filename, 'w').write(f'Global Color Table Size: {gct_size} colors\n')

			# Read Global Color Table
			gct_data = f.read(3 * gct_size) # Each color is 3 bytes (RGB)

			# Create a list of RGB triplets
			gct_colors = [(gct_data[i], gct_data[i + 1], gct_data[i + 2]) for i in range(0, len(gct_data), 3)]

			# Print or use Global Color Table as needed
			for i, color in enumerate(gct_colors):
				print(f'Color {i}: R={color[0]} G={color[1]} B={color[2]}')
				open(filename, 'a').write(f'Color {i}: R={color[0]} G={color[1]} B={color[2]}\n')

			print(f'Global Color Table data written to: ./{filename}')

			return gct_colors

		else:
			print('No Global Color Table present.')
			open(filename, 'w').write(f'No Global Color Table present.\n')
			print(f'Global Color Table data written to: ./{filename}')

			return []



# helper function for generate_color_table_html
def rgb_to_hex(r, g, b):
	return '#{:02x}{:02x}{:02x}'.format(r, g, b)



def generate_color_table_html(filepath, colors):
	read_choice = input('Create an html file of the gif\'s color table? (y\\n): ')
	newdir = filepath.split(".")[0]

	if (read_choice.lower() == 'y') or (read_choice.lower() == 'yes'):

		filename = newdir + "/" + filepath[:-4] + '_colortable.html'

		print(f'\n[ GENERATING COLOR TABLE HTML FILE: ./{filename} ]')

		with open(filename, 'w') as fh:
			i = 0
			fh.write('<div style=\"width: 512px; word-wrap: break-word\">')
			for color in colors:
				html_code = rgb_to_hex(color[0], color[1], color[2])
				fh.write(f'<font color={html_code}><b>{i}</b></font>&nbsp;')
				i += 1
			fh.write('</div>')



def read_application_extension(file_path):
	print(f'\n[ READING APPLICATION EXTENSION ]')

	with open(file_path, 'rb') as f:
		# Skip the GIF header (6 bytes: GIF87a or GIF89a)
		f.read(6)

		# Read Logical Screen Descriptor (7 bytes)
		f.read(4) # Skip screen width and height
		packed_fields = int.from_bytes(f.read(1), 'little')
		gct_flag = (packed_fields & 0x80) >> 7
		gct_size = packed_fields & 0x07
		f.read(2) # Skip background color index and pixel aspect ratio

		# Skip Global COlor Table if it exists
		if gct_flag:
			gct_length = 3 * (2 ** (gct_size + 1))
			f.read(gct_length)

		# Loop through the blocks to find the first Application Extension
		while True:
			block_type = f.read(1)

			if not block_type:
				print(f'Reached end of file without finding an Application Extension.')
				quit()

			if block_type == b'\x21': # Extension introducer
				next_byte = f.read(1)

				if next_byte == b'\xFF': # Application Extension Label
					# Process Application Extension
					block_size = int.from_bytes(f.read(1), 'little')

					if block_size == 11: # Typically 11 for Application Extension
						app_identifier = f.read(8).decode('ascii')
						app_auth_code = f.read(3).hex()

						print(f'Block Size: {block_size}')
						print(f'Application Identifier: {app_identifier}')
						print(f'Application Authentication Code: {app_auth_code}')

						# Reading and displaying sub-blocks
						while True:
							sub_block_size = int.from_bytes(f.read(1), 'little')
							if sub_block_size == 0:
								break
							else:
								sub_block_data = f.read(sub_block_size)
								print(f'Sub-block Size: {sub_block_size}')
								print(f'Sub-block Data: {sub_block_data.hex()}')
						break
				else:
					extension_length = int.from_bytes(f.read(1), 'little')
					f.read(extension_length)



def read_gif_image_descriptor(file_path):
	print(f'\n[ READING GIF IMAGE DESCRIPTOR ]')

	with open(file_path, 'rb') as f:
		# Skip the GIF header (6 bytes: GIF87a or GIF89a)
		f.read(6)

		# Read Logical Screen Descriptor (7 bytes)
		f.read(4) # Skip screen width and height
		packed_fields = int.from_bytes(f.read(1), 'little')
		gct_flag = (packed_fields & 0x80) >> 7
		gct_size = packed_fields & 0x07
		f.read(2) # Skip background color index and pixel aspect ratio

		# Skip Global Color Table if it exists
		if gct_flag:
			gct_length = 3 * (2 ** (gct_size + 1)) # 3 bytes for color
			f.read(gct_length)
		
		# Loop through the blocks to find the first Image Descriptor
		while True:
			block_type = f.read(1)
			if not block_type:
				print(f'Reached end of file without finding an Application Extension.')
				quit()

			if block_type == b'\x2C':
				# Read and process Image Descriptor (9 bytes)
				left_position = int.from_bytes(f.read(2), 'little')
				top_position = int.from_bytes(f.read(2), 'little')
				width = int.from_bytes(f.read(2), 'little')
				height = int .from_bytes(f.read(2), 'little')
				packed_field = int.from_bytes(f.read(2), 'little')
				
				local_color_table_flag = (packed_field & 0x80) >> 7
				interlace_flag = (packed_field & 0x40) >> 6
				sort_flag = (packed_field & 0x20) >> 5
				reserved = (packed_field & 0x18) >> 3
				local_color_table_size = packed_field & 0x07

				print(f'Left Position: {left_position}')
				print(f'Top Position: {top_position}')
				print(f'Image Width: {width}')
				print(f'Image Height: {height}')
				print(f'Local Color Table Flag: {local_color_table_flag}')
				print(f'Interlace Flag: {interlace_flag}')
				print(f'Sort Flag: {sort_flag}')
				print(f'Reserved: {reserved}')
				print(f'Size of Local Color Table: {local_color_table_size}')

				break



def read_graphics_control_extension(file_path):
	print(f'\n[ READING GRAPHICS CONTROL EXTENSION ]')

	with open(file_path, 'rb') as f:
		# Skip the GIF header (6 bytes: GIF87a or GIF89a)
		f.read(6)
		
		# Read Logical Screen Descriptor
		f.read(4) # Skip screen width and height
		packed_fields = int.from_bytes(f.read(1), 'little')
		gct_flag = (packed_fields & 0x80) >> 7
		gct_size = packed_fields & 0x07
		f.read(2) # Skip background color index and pixel aspect ratio

		# Skip Global Color Table if it exists
		if gct_flag:
			gct_length = 3 * (2 ** (gct_size + 1))
			f.read(gct_length)

		# Loop through the blocks to find the first Graphics Control Extension
		while True:
			block_type = f.read(1)
			if not block_type:
				print(f'Reached end of file without finding an Application Extension.')
				quit()
			
			if block_type == b'\x21': # Extension Introducer
				next_byte = f.read(1)
				if next_byte == b'\xF9': # Graphic Control Label
					# Process Graphics Control Extension
					block_size = int.from_bytes(f.read(1), 'little')
					packed_fields = int.from_bytes(f.read(1), 'little')
					disposal_method = (packed_fields & 0b00011100) >> 2
					user_input_flag = (packed_fields & 0b00000010) >> 1
					transparent_color_flag = packed_fields & 0b00000001
					delay_time = int.from_bytes(f.read(2), 'little')
					transparent_color_index = int.from_bytes(f.read(1), 'little')
					block_terminator = int.from_bytes(f.read(1), 'little')

					print(f'Block Size: {block_size}')
					print(f'Disposal Method: {disposal_method}')
					print(f'User Input Flag: {user_input_flag}')
					print(f'Transparent Color Flag: {transparent_color_flag}')
					print(f'Delay Time: {delay_time}')
					print(f'Transparent Color Index: {transparent_color_index}')
					print(f'Block Terminator: {block_terminator}')

					break

			else: # Skip other types of extensions
				extension_length = int.from_bytes(f.read(1), 'little')
				f.read(extension_length)



def read_image_data(file_path):
	print(f'\n[ READING IMAGE DATA ]')
	newdir = file_path.split(".")[0]
	read_choice = input('Read the GIF\'s image data to stdout? (this will produce a lot of output to stdout!) (y\\n): ')

	filename = newdir + "/" + file_path[:-4] + '_image_data.txt'

	with open(file_path, 'rb') as f:
		# Skip the GIF header (6 bytes: GIF87a or GIF89a)
		f.read(6)

		# Read Logical Screen Descriptor (7 bytes)
		f.read(4) # Skip screen width and height
		packed_fields = int.from_bytes(f.read(1), 'little')
		gct_flag = (packed_fields & 0x80) >> 7
		gct_size = packed_fields & 0x07
		f.read(2) # Skip the background color index and pixel aspect ratio

		# Skip Global Color Table if it exists
		if gct_flag:
			gct_length = 3 * (2 ** (gct_size + 1))
			f.read(gct_length)

		# Loop through the blocks to find the first Image Descriptor
		while True:
			block_type = f.read(1)
			
			if not block_type:
				print(f'Reached end of file without finding an Application Extension.')
				open(filename, 'w').write('Reached end of file without finding an Application Extension.\n')
				quit()

			if block_type == b'\x2C': # Image Descriptor
				# Skip the Image Descriptor and focus on Image Data
				f.read(9) # Skip the next 9 bytes

				# Read the LZW Minimum Code Size
				LZW_min_code_size = int.from_bytes(f.read(1), 'little')
				print(f'LZW Minimum Code Size: {LZW_min_code_size}')
				# for first open, write so old version is overwritten
				open(filename, 'w').write(f'LZW Minimum Code Size: {LZW_min_code_size}\n')

				# Reading and displaying sub-blocks
				while True:
					sub_block_size = int.from_bytes(f.read(1), 'little')
					if sub_block_size == 0:
						break
					else:
						sub_block_data = f.read(sub_block_size)
						if (read_choice.lower() == 'y') or (read_choice.lower() == 'yes'):
							print(f'Sub-block Size: {sub_block_size}')
						open(filename, 'a').write(f'Sub-block Size: {sub_block_size}\n')

						if (read_choice.lower() == 'y') or (read_choice.lower() == 'yes'):
							print(f'Sub-block Data: {sub_block_data.hex()}')
						open(filename, 'a').write(f'Sub-block Data: {sub_block_data.hex()}\n')

				break

			elif block_type == b'\21': # Extension Introducer
				# Skip other types of extensions
				f.read(1) # Read the label
				extension_length = int.from_bytes(f.read(1), 'little')
				f.read(extension_length)
				while True:
					sub_block_size = int.from_bytes(f.read(1), 'little')
					if sub_block_size == 0:
						break
					else:
						f.read(sub_block_size)

		print(f'Image data written to: ./{filename}')



# helper function for read_and_dump_frames
def lzw_decode(min_code_size, compressed):
	clear_code = 1 << min_code_size
	eoi_code = clear_code + 1
	next_code = eoi_code + 1
	current_code_size = min_code_size + 1

	dictionary = {i: [i] for i in range(clear_code)}
	dictionary[clear_code] = []
	dictionary[eoi_code] = None

	def read_bits(bit_count, bit_pos, data):
		value = 0
		for i in range(bit_count):
			byte_pos = (bit_pos + i) // 8
			bit_offset = (bit_pos + i) % 8
			
			if data[byte_pos] & (1 << bit_offset):
				value |= 1 << i
		return value

	bit_pos = 0
	data_length = len(compressed) * 8
	output = deque()
	current_code = None

	while bit_pos + current_code_size <= data_length:
		code = read_bits(current_code_size, bit_pos, compressed)
		bit_pos += current_code_size

		if code == clear_code:
			current_code_size = min_code_size + 1
			next_code = eoi_code + 1
			dictionary = {i: [i] for i in range(clear_code)}
			dictionary[clear_code] = []
			dictionary[eoi_code] = None
			current_code = None
		
		elif code == eoi_code:
			break

		else:
			if code in dictionary:
				entry = dictionary[code]

			elif code == next_code:
				entry = dictionary[current_code] + [dictionary[current_code][0]]

			else:
				raise ValueError(f'Invalid code: {code}')

			output.extend(entry)

			if current_code is not None:
				dictionary[next_code] = dictionary[current_code] + [entry[0]]
				next_code += 1

				if next_code >= (1 << current_code_size):
					if current_code_size < 12:
						current_code_size += 1

			current_code = code

	return list(output)



def lzw_encode(self, min_code_size, data):
	# Initialization
	clear_code = 1 << min_code_size
	eoi_code = clear_code + 1
	next_code = eoi_code + 1
	current_code_size = min_code_size + 1

	dictionary = {chr(i): i for i in range(clear_code)}

	output = bytearray()
	buffer = 0
	buffer_length = 0
	current = ''

	def write_code_to_buffer(code, buffer, buffer_length, output):
		buffer |= code << buffer_length
		buffer_length += current_code_size
		while buffer_length >= 8:
			output.append(buffer & 0xFF)
			buffer >>= 8
			buffer_length -= 8
		return buffer, buffer_length

	# Write clear_code to buffer
	buffer, buffer_length = write_code_to_buffer(clear_code, buffer, buffer_length, output)

	for i in data:
		current += chr(i)
		if current not in dictionary:
			buffer, buffer_length = write_code_to_buffer(dictionary[current[:-1]], buffer, buffer_length, output)

			if next_code < (1 << current_code_size):
				dictionary[current] = next_code
				next_code += 1
				current_code_size += 1

			current = current[:-1]

	if current in dictionary:
		buffer, buffer_length = write_code_to_buffer(dictionary[current], buffer, buffer_length, output)
	buffer, buffer_length = write_code_to_buffer(eoi_code, buffer, buffer_length, output)

	if buffer_length > 0:
		output.append(buffer & 0xFF)

	return output

def read_and_dump_frames(file_path):
	print(f'\n[ READING AND DUMPING FRAMES ]')

	newdir = file_path.split(".")[0]

	read_choice = input(f'Read and dump the GIF\'s frames? (this will produce a lot of files in ./{newdir}!) (y\\n): ')

	if (read_choice.lower() == 'y') or (read_choice.lower() == 'yes'):
		
		frame_counter = 0
		global_frame_data = None # To hold the entire frame canvas

		with open(file_path, 'rb') as f:
			f.read(6) # Skip the GIF header

			global_width = int.from_bytes(f.read(2), 'little')
			global_height = int.from_bytes(f.read(2), 'little')

			packed_fields = int.from_bytes(f.read(1), 'little')
			gct_flag = (packed_fields & 0x80) >> 7
			gct_size = packed_fields & 0x07
			f.read(2) # Skip remaining fields

			if gct_flag:
				gct_length = 3 * (2 ** (gct_size + 1))
				global_color_table = np.array(list(f.read(gct_length))).reshape(-1, 3)

			# Initialize global_frame_data to zeroes
			global_frame_data = np.zeros((global_height, global_width, 3), dtype = np.uint8)

			while True:
				block_type = f.read(1)

				if not block_type:
					print("Reached end of file.")
					break

				if block_type == b'\x2C': # Image Descriptor
					left_position = int.from_bytes(f.read(2), 'little')
					top_position = int.from_bytes(f.read(2), 'little')
					width = int.from_bytes(f.read(2), 'little')
					height = int.from_bytes(f.read(2), 'little')
					packed_field = int.from_bytes(f.read(1), 'little')

					interlace_flag = (packed_field & 0x40) >> 6
					local_color_table_flag = (packed_field & 0x80) >> 7

					if local_color_table_flag:
						lct_size = packed_field & 0x07
						lct_length = 3 * (2 ** (lct_size + 1))
						local_color_table = np.array(list(f.read(lct_length))).reshape(-1, 3)

					else:
						local_color_table = global_color_table

					LZW_min_code_size = int.from_bytes(f.read(1), 'little')
					compressed_data = bytearray()
					
					while True:
						sub_block_size = int.from_bytes(f.read(1), 'little')
						if sub_block_size == 0:
							break
						compressed_data += f.read(sub_block_size)

					decoded_data = lzw_decode(LZW_min_code_size, compressed_data)
					frame_data = np.zeros((height, width, 3), dtype = np.uint8)

					if interlace_flag:
						interlace_order = []
						interlace_order.extend(range(0, height, 8))
						interlace_order.extend(range(4, height, 8))
						interlace_order.extend(range(2, height, 4))
						interlace_order.extend(range(1, height, 2))
						
						reordered_data = [None] * height

						for i, row in enumerate(interlace_order):
							start_index = row * width
							end_index = start_index + width
							reordered_data[row] = decoded_data[start_index:end_index]

						decoded_data = [pixel for row_data in reordered_data if row_data is not None for pixel in row_data]

					for i, pixel in enumerate(decoded_data):
						row = i // width
						col = i % width
						frame_data[row, col] = local_color_table[pixel]

					# Overlay the new frame_data onto the global frame
					global_frame_data[top_position:top_position + height, left_position:left_position + width] = frame_data

					frame_img = Image.fromarray(global_frame_data.astype('uint8'), 'RGB')
					frame_img.save(f'{newdir}/frame_{frame_counter}.png')

					frame_counter += 1

				elif block_type == b'\x21': # Extension
					f.read(1) # Extension function code
					extension_length = int.from_bytes(f.read(1), 'little')
					f.read(extension_length) # Skip extension data
					while True:
						sub_block_size = int.from_bytes(f.read(1), 'little')
						if sub_block_size == 0:
							break
						f.read(sub_block_size)



def main():
	filepath = input('File name (with extension): ')
	
	newdir = filepath.split(".")[0]
	print(f'[DEBUG] Making new directory: ./{newdir} to store generated files')
	
	try:
		os.mkdir(newdir)
	except OSError as e:
		print(f'./{newdir} already exists. Continuing. Error: {e}')

	read_logical_screen_descriptor(filepath)

	colors = read_global_color_table(filepath)
	
	# Comment out if you don't want to generate html files for the gif's color table
	generate_color_table_html(filepath, colors)

	read_application_extension(filepath)

	read_gif_image_descriptor(filepath)

	read_graphics_control_extension(filepath)

	read_image_data(filepath)
	read_and_dump_frames(filepath)



if __name__ == '__main__':
	main()
