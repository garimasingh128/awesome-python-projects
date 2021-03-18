import PIL.Image

SIZE = 100
WIDTHRATIO = 0.6
path = None
SAVE_NAME = "ascii_image.txt"

# ASCII chars used to build the output text
ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

# resize image
def resize_image(image, new_width=SIZE):
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio * WIDTHRATIO)
    resized_image = image.resize((new_width, new_height))
    return(resized_image)

# convert grayscale
def grayify(image):
    grayscale_image = image.convert("L")
    return(grayscale_image)

# pixels to ASCII chars
def pixels_to_ascii(image):
    pixels = image.getdata()
    characters = "".join([ASCII_CHARS[pixel//25] for pixel in pixels])
    return(characters)

def setSize(size_multi : int):
    if size_multi < 50:
        size_multi = 50

    elif size_multi > 1000:
        size_multi = 1000

    return(size_multi)

def setWidth(ratio_multi : float):
    if ratio_multi < 0.2:
        ratio_multi = 0.2
    
    elif ratio_multi > 1:
        ratio_multi = 1

    return(ratio_multi)

def main(new_width = None, WIDTHRAT = None):
    if WIDTHRAT != None:
        WIDTHRATIO = WIDTHRAT
    if new_width != None:
        SIZE = new_width
    else:
        new_width = SIZE

    try:
        image = PIL.Image.open(path)
    except:
        print(path, "is not a valid pathname to an image.")

    # image to ascii
    new_image_data = pixels_to_ascii(grayify(resize_image(image, new_width)))

    # format
    pixel_count = len(new_image_data)
    ascii_image = "\n".join(new_image_data[i:(i+new_width)] for i in range(0, pixel_count, new_width))

    # print
    #print(ascii_image)

    # save results
    with open(SAVE_NAME, "w") as f:
        f.write(ascii_image)
