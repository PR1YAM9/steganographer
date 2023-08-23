from PIL import Image
import numpy as np
import os

def encrypt_message(image_path, message, password):
    # Open the image file
    img = Image.open(image_path)

    # Convert the image to RGBA mode
    img = img.convert("RGBA")

    # Getting the dimensions of the image
    width, height = img.size

    # Getting a 2D array of the shape (height * width, 4)
    # Each row represents a pixel, and each column represents a color channel (RGBA)
    array = np.array(list(img.getdata()))
    
    array = array.astype(np.uint8)

    color_channels = 3

    total_pixels = array.shape[0] 

    bit_message = ''.join([format(ord(i), "08b") for i in message])
    bit_password = ''.join([format(ord(char), '08b') for char in password])
    
    #getting password length for embedding
    password_length = len(password)
    print("length of password is "+ str(password_length))
    
    binPasswordLen = format(password_length,'08b')
    
    # embedding the message then a delimiter then the length of string password and finally the password itself
    binary_message = bit_message + '00000000' + binPasswordLen + bit_password
    print(binary_message)
    print("before mnauplation")
    print(array)
  
    # Each pixel has 4 color channels (RGBA), and we can modify the last 2 bits of each RGB channel,
    total_bits = len(binary_message)
    req_channels =  total_bits // 2

    if len(binary_message) % 2 != 0:
        req_channels += 1

    if req_channels > total_pixels * color_channels:
        print("ERROR: Need a larger file size")
        return
    else:
        index = 0
        for p in range(total_pixels):
            if index >= len(binary_message):
              break
            # Get the current pixel value
            pixel = array[p]

            # Modify the last 2 bits of each RGB channel using the message
            for c in range(color_channels):
                # 0b11111100 is a bit mask that when '&' is performed clears the last 2 bits of the pixel
                pixel[c] = (pixel[c] & 0b11111100) | int(binary_message[index:index+2], 2)

                # Increment the index pointer to track the next 2 bits of the message
                index = (index + 2) 

                # Update the pixel value in the image array
                array[p] = pixel
        
    # Convert the pixel values to the appropriate data type
    array = array.astype(np.uint8)

    # Reshape the 2D array back to the original image dimensions
    array = array.reshape(height, width, 4)  # 4 channels (RGBA)
    print("after manuplation")
    print(array)

    # Convert the modified array back into an image
    modified_img = Image.fromarray(array, "RGBA")

    # Get the original image's name without the extension
    modified_image_name = os.path.splitext(os.path.basename(image_path))[0]

    # Append "_enc" to the image name
    new_image_name = modified_image_name + "_enc"

    # Save the image as PNG with the modified name
    new_image_path = new_image_name + ".png"
    modified_img.save(new_image_path, "PNG")
    print("Image is encoded and saved successfully")
    
    return new_image_path


def decrypt_image(image_path, password):
    img = Image.open(image_path)

    # Convert the image to RGBA mode
    img = img.convert("RGBA")

    array = np.array(img)
    
    array = array.astype(np.uint8) 
     
    print(array)
    last_two_bits = np.bitwise_and(array[..., :3], 0b00000011)  # Extract last two bits of RGB channels

    binary_message = last_two_bits.reshape(-1, 3)  # Reshape to (total_pixels, color_channels)
    binary_message = ''.join(format(pixel, '02b') for pixel in binary_message.flatten())  # Convert to string
    print(binary_message)

    delimiter = '00000000'  # Delimiter bit pattern

    # Convert the password to its binary representation
    binary_password = ''.join(format(ord(char), '08b') for char in password)

    delimiter_start_index = binary_message.find(delimiter)  # Find the first occurrence of the delimiter
       
    #checks if there is a delimiter present or not (for non encoded images)
    if delimiter_start_index != -1:
        # because each character is 8 bit so delimiter will start from a multiple of 8 only
        remainder = 8- (delimiter_start_index % 8)
        
        if delimiter_start_index % 8 != 0:
            delimiter_start_index+= remainder
            
        delimiter_end_index = delimiter_start_index + len(delimiter)
        
        #testing 
        print("delimiter start index is: " + str(delimiter_start_index))
        print("delimiter end index is: " + str(delimiter_end_index))
        
         # Extract the password length (8 bits after the delimiter)
        password_length_start = delimiter_end_index
        password_length_end = password_length_start + 8 #8 bits for password
        password_length_bin = binary_message[password_length_start:password_length_end]
        
        # Convert the binary password length to an integer
        password_length = int(password_length_bin, 2)
        
        password_start = password_length_end
        password_end = password_start + (password_length*8) # Calculate the end index based on binary_password
        extractedBin_password = binary_message[password_start:password_end]
        
        extracted_password = ''.join(chr(int(extractedBin_password[i:i+8],2)) for i in range (0,len(extractedBin_password), 8))
        
        #testing
        print("extracted password is " + extracted_password)
        print("password is " + password)


        if extracted_password == password:
            print("password is correct")
        else: 
            print("incorrect password")
            return 
    else:
        print("Error 404 password not found!")
        return

   
    
# Example usage
def Stego():
    print("--Welcome to $t3g0--")
    print("1: Encode")
    print("2: Decode")

    func = input()
    image_path ="C:\\Users\\Surface Pro\\Desktop\\manan\\random_image.jpg"
    image_path2 ="C:\\Users\\Surface Pro\\Desktop\\manan\\random_image_enc.png"

    if func == '1': 
        print("Enter Source Image Path")
        src = input()
        print("Enter Message to Hide")
        message = input()
        print("Enter password")
        password =  input()
        converted_image_path = encrypt_message(image_path, message, password)
        print("Converted image saved as:", converted_image_path)
        
    elif func == '2':
        print("Enter the image path")
        path = input()
        print("enter the password")
        password = input()
        decrypted_message = decrypt_image(image_path2, password)
        if decrypted_message:
            print("Decrypted Message:")
            print(decrypted_message)

Stego()
