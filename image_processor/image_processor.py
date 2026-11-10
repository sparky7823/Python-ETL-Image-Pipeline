import sys
from byuimage import Image


def validate_commands(lst, num_args_needed):
    """
    Validates the command-line argument count against the required number of parameters
    for a given operation flag. Returns a boolean indicating validity.
    """
    if (len(lst) - 1) == num_args_needed:
        return True
    else:
        return False


def darken(filename, percent):
    """
    Applies a darkening filter by scaling RGB pixel values by a specified percentage.
    Returns the modified image object.
    """
    image = Image(filename)
    lightness = 1 - percent
    for pixel in image:
        pixel.red = pixel.red * lightness
        pixel.green = pixel.green * lightness
        pixel.blue = pixel.blue * lightness
    return image


def sepia(filename):
    """
    Applies a sepia tone filter using standard RGB weighted transformations.
    Enforces a strict 255 upper bound on channel values to prevent integer overflow.
    Returns the modified image object.
    """
    image = Image(filename)
    for pixel in image:
        true_red = 0.393 * pixel.red + 0.769 * pixel.green + 0.189 * pixel.blue
        true_green = 0.349 * pixel.red + 0.686 * pixel.green + 0.168 * pixel.blue
        true_blue = 0.272 * pixel.red + 0.534 * pixel.green + 0.131 * pixel.blue
        if true_red > 255:
            pixel.red = 255
        else:
            pixel.red = true_red
        if true_green > 255:
            pixel.green = 255
        else:
            pixel.green = true_green
        if true_blue > 255:
            pixel.blue = 255
        else:
            pixel.blue = true_blue
    return image


def grayscale(filename):
    """
    Converts the image to grayscale by calculating the uniform average of the
    RGB channels for each pixel. Returns the modified image object.
    """
    image = Image(filename)
    for pixel in image:
        average = (pixel.red + pixel.green + pixel.blue) // 3
        pixel.color = (average, average, average)
    return image


def make_borders(filename, thickness, red, green, blue):
    """
    Generates a padded image canvas and maps the original image onto it,
    creating a solid border of specified thickness and RGB color.
    Returns the new composited image object.
    """
    image = Image(filename)
    new_image = Image.blank(image.width + 2 * thickness, image.height + 2 * thickness)
    for x in range(new_image.width):
        for y in range(new_image.height):
            pixel = new_image.get_pixel(x,y)
            if x < thickness or x >= (new_image.width - thickness) or y < thickness or y >= (new_image.height - thickness):
                pixel.color = (red, green, blue)
            else:
                pixel.color = image.get_pixel((x - thickness), (y - thickness)).color
    return new_image


def flipped(filename):
    """
    Applies a vertical axis transformation,
    reflecting the pixel matrix across the x-axis.
    Returns the new transformed image object.
    """
    image = Image(filename)
    new_image = Image.blank(image.width, image.height)
    for y in range(new_image.height):
        for x in range(new_image.width):
            pixel = new_image.get_pixel(x, y)
            flip_y = new_image.height - 1 - y
            pixel.color = image.get_pixel(x, flip_y).color
    return new_image


def mirror(filename):
    """
    Applies a horizontal axis transformation,
    reflecting the pixel matrix across the y-axis.
    Returns the new transformed image object.
    """
    image = Image(filename)
    new_image = Image.blank(image.width, image.height)
    for x in range(new_image.width):
        for y in range(new_image.height):
            pixel = new_image.get_pixel(x, y)
            flip_x = new_image.width - 1 - x
            pixel.color = image.get_pixel(flip_x, y).color
    return new_image


def collage(file1, file2, file3, file4, thickness):
    """
    Composites four images of equal dimensions into a 2x2 grid with a defined
    border thickness. Validates uniform dimensions before processing and returns
    the composited image object, or False if validation fails.
    """
    image1 = Image(file1)
    image2 = Image(file2)
    image3 = Image(file3)
    image4 = Image(file4)
    if image1.width == image2.width == image3.width == image4.width and image1.height == image2.height == image3.height == image4.height:
        new_width = (image1.width * 2) + (thickness * 3)
        new_height = (image1.height * 2) + (thickness * 3)
        new_image = Image.blank(new_width, new_height)

        for x in range(new_image.width):
            for y in range(new_image.height):
                pixel = new_image.get_pixel(x, y)
                if thickness <= x < (thickness + image1.width) and thickness <= y < (thickness + image1.height):
                    pixel.color = image1.get_pixel((x - thickness), (y - thickness)).color
                elif (2 * thickness + image1.width) <= x < (new_image.width - thickness) and thickness <= y < (thickness + image1.height):
                    pixel.color = image2.get_pixel((x - (2 * thickness + image1.width)), (y - thickness)).color
                elif thickness <= x < (thickness + image1.width) and (2 * thickness + image1.height) <= y < (new_image.height - thickness):
                    pixel.color = image3.get_pixel((x - thickness), (y - (2 * thickness + image1.height))).color
                elif (2 * thickness + image1.width) <= x < (new_image.width - thickness) and (2 * thickness + image1.height) <= y < (new_image.height - thickness):
                    pixel.color = image4.get_pixel(x - (2 * thickness + image1.width), (y - (2 * thickness + image1.height))).color
                else:
                    pixel.color = (0, 0, 0)
        return new_image
    else:
        return False


def detect_green(pixel, threshold, factor):
    """
    Evaluates a pixel's RGB values against dynamic threshold and factor parameters
    to determine if the green channel dominance meets chroma-key requirements.
    Returns a boolean.
    """
    average = (pixel.red + pixel.green + pixel.blue) / 3
    if pixel.green >= factor * average and pixel.green > threshold:
        return True
    else:
        return False


def green_screen(fg_file, bg_file, threshold, factor):
    """
    Performs chroma-key compositing (green screen replacement).
    Iterates through the foreground matrix and replaces qualifying pixels
    with corresponding pixels from the background matrix.
    Returns the composited image object.
    """
    fg = Image(fg_file)
    bg = Image(bg_file)
    new = Image.blank(fg.width, fg.height)
    for x in range(new.width):
        for y in range(new.height):
            pixel = new.get_pixel(x, y)
            fg_pixel = fg.get_pixel(x,y)
            if detect_green(fg_pixel, threshold, factor):
                pixel.color = bg.get_pixel(x, y).color
            else:
                pixel.color = fg.get_pixel(x, y).color
    return new


def main(argv):
    a = argv[1]
    lst = argv[1:]
    """
    CLI router.
    Parses sys.argv flags to validate input constraints and
    route arguments to the appropriate image processing function.
    """
    if a == '-d':
        # -d <image file>
        if validate_commands(lst, 1):
            image = Image(argv[2])
            image.show()
    elif a == '-k':
        # -k <input file> <output file> <percent>
        if validate_commands(lst, 3) and (float(argv[4]) < 1) and ('.png' in argv[3]):
            image = darken(argv[2], float(argv[4]))
            image.save(argv[3])
    elif a == '-s':
        # -s <input file> <output file>
        if validate_commands(lst, 2):
            image = sepia(argv[2])
            image.save(argv[3])
    elif a == '-g':
        # -g <input file> <output file>
        if validate_commands(lst, 2):
            image = grayscale(argv[2])
            image.save(argv[3])
    elif a == '-b':
        # -b <input file> <output file> <thickness> <red> <green> <blue>
        if validate_commands(lst, 6):
            image = make_borders(argv[2], int(argv[4]), int(argv[5]), int(argv[6]), int(argv[7]))
            image.save(argv[3])
    elif a == '-f':
        # -f <input file> <output file>
        if validate_commands(lst, 2):
            image = flipped(argv[2])
            image.save(argv[3])
    elif a == '-m':
        # -m <input file> <output file>
        if validate_commands(lst, 2):
            image = mirror(argv[2])
            image.save(argv[3])
    elif a == '-c':
        # -c <image 1> <image 2> <image 3> <image 4> <output image> <border thickness>
        if validate_commands(lst, 6):
            image = collage(argv[2], argv[3], argv[4], argv[5], int(argv[7]))
            #image.show()
            image.save(argv[6])
    elif a == '-y':
        # -y <foreground image> <background image> <output file> <threshold> <factor>
        if validate_commands(lst, 5):
            image = green_screen(argv[2], argv[3], int(argv[5]), float(argv[6]))
            image.save(argv[4])


if __name__ == "__main__":
    main(sys.argv)