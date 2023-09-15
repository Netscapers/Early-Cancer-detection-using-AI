from PIL import Image

# Open the image
image = Image.open('uploads/B0001_rgb.jpg')

# Get the number of channels
num_channels = len(image.getbands())

print("Number of channels:", num_channels)
