import time
import hashlib
import tempfile
from pyfingerprint.pyfingerprint import PyFingerprint
import RPi.GPIO as GPIO
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image, ImageDraw, ImageFont
from collections import OrderedDict
import threading

import board
import digitalio
import busio
import adafruit_rgb_display.st7735 as st7735

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
BUTTON_PINS = [5, 6, 13, 19]  # Example GPIO pins for buttons

for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# TFT setup
cs_pin = digitalio.DigitalInOut(board.CE0)  # Chip select of the display (BCM 8, Physical 24)
dc_pin = digitalio.DigitalInOut(board.D24)  # Data/command pin (BCM 24, Physical 18)
reset_pin = digitalio.DigitalInOut(board.D25)  # Reset pin (BCM 25, Physical 22)
led_pin = digitalio.DigitalInOut(board.D18)  # LED pin (BCM 18, Physical 12, optional)

# Set the LED pin to output and turn it on
led_pin.direction = digitalio.Direction.OUTPUT
led_pin.value = True

# Config for display baudrate (default max is 24mhz)
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = busio.SPI(board.SCLK, MOSI=board.MOSI, MISO=board.MISO)

# Create the ST7735 display:
disp = st7735.ST7735R(spi, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
width = disp.width
height = disp.height
image = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(image)

# Font setup
font = ImageFont.load_default()

def tft_init():
    disp.fill(0)  # Clear display

def tft_clear():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    disp.image(image)

def tft_message(message, line):
    tft_clear()
    y = 10 if line == 1 else 30
    draw.text((10, y), message, font=font, fill="WHITE")
    disp.image(image)

def tft_message_five_lines(message1, message2, message3, message4, message5):
    tft_clear()
    max_width = width - 20  # Adjust for margin
    y = 10
    for message in [message1, message2, message3, message4, message5]:
        lines = [message[i:i+20] for i in range(0, len(message), 20)]
        for line in lines:
            draw.text((10, y), line, font=font, fill="WHITE")
            y += 20
    disp.image(image)

def tft_message_four_lines(message1, message2, message3, message4):
    tft_clear()
    max_width = width - 20  # Adjust for margin
    y = 10
    for message in [message1, message2, message3, message4]:
        lines = [message[i:i+20] for i in range(0, len(message), 20)]
        for line in lines:
            draw.text((10, y), line, font=font, fill="WHITE")
            y += 20
    disp.image(image)

FINGERPRINT_CHARBUFFER1 = 0x01
FINGERPRINT_CHARBUFFER2 = 0x02

is_anti_spoof_enabled = False
stop_operation = False

def initialize_sensor():
    try:
        f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
        if not f.verifyPassword():
            raise ValueError('The given fingerprint sensor password is wrong!')
        return f
    except Exception as e:
        tft_message_four_lines('Sensor Init Failed!', str(e), '', '')
        print(f'Sensor Init Failed: {e}')
        exit(1)

def delete_finger():
    global stop_operation
    try:
        f = initialize_sensor()
        tft_message_four_lines('Used templates:', str(f.getTemplateCount()) + '/' + str(f.getStorageCapacity()), '', '')
        print(f'Used templates: {f.getTemplateCount()}/{f.getStorageCapacity()}')
        time.sleep(2)
        tft_message('Enter template pos:', 1)
        positionNumber = int(input('Please enter the template position you want to delete: '))

        if stop_operation:
            return

        if f.deleteTemplate(positionNumber):
            tft_message('Template deleted!', 1)
            print('Template deleted!')
        else:
            tft_message('Failed to delete!', 1)
            print('Failed to delete!')
    except Exception as e:
        tft_message_four_lines('Delete Failed!', str(e), '', '')
        print(f'Delete Failed: {e}')
        exit(1)

def enroll_finger():
    global stop_operation
    try:
        f = initialize_sensor()
        tft_message_four_lines('Used templates:', str(f.getTemplateCount()) + '/' + str(f.getStorageCapacity()), '', '')
        print(f'Used templates: {f.getTemplateCount()}/{f.getStorageCapacity()}')
        time.sleep(2)
        tft_message('Waiting for finger...', 1)

        # Capture the first fingerprint image
        while not f.readImage():
            if stop_operation:
                return

        f.convertImage(FINGERPRINT_CHARBUFFER1)
        result = f.searchTemplate()
        positionNumber = result[0]

        if positionNumber >= 0:
            tft_message_four_lines('Template exists', 'Pos #' + str(positionNumber), '', '')
            print(f'Template exists at position #{positionNumber}')
            return

        tft_message('Remove finger...', 1)
        time.sleep(2)
        tft_message_four_lines('Waiting for same', 'finger again...', '', '')

        # Add a small delay to allow the user to reposition their finger
        time.sleep(3)

        # Capture the second fingerprint image
        while not f.readImage():
            if stop_operation:
                return

        f.convertImage(FINGERPRINT_CHARBUFFER2)

        if f.compareCharacteristics() == 0:
            raise Exception('Fingers do not match')

        f.createTemplate()
        positionNumber = f.storeTemplate()
        tft_message_four_lines('Finger enrolled!', 'Pos #' + str(positionNumber), '', '')
        print(f'Finger enrolled at position #{positionNumber}')

    except Exception as e:
        tft_message_four_lines('Enroll Failed!', str(e), '', '')
        print(f'Enroll Failed: {e}')

def search_finger():
    global stop_operation
    f = initialize_sensor()
    while not f.readImage():
        if stop_operation:
            return

    timestamp = time.strftime("%Y%m%d%H%M%S")
    imageDestination = '/home/sanya22/Searched_Fingerprint_images/fingerprint_' + timestamp + '.bmp'
    f.downloadImage(imageDestination)
    time.sleep(2)

    fingerprint_data = Image.open(imageDestination)
    is_fake = spoof_detection_algorithm(fingerprint_data, is_anti_spoof_enabled)

    if is_fake:
        print("Spoof fingerprint detected")
        tft_message('Spoof Detected!', 1)
    else:
        normal_fingerprint_search()

    time.sleep(2)

def spoof_detection_algorithm(fingerprint_data, is_anti_spoof_enabled):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Replace with the path to your model weights
    weights_path = "/home/sanya22/myproject/Resnet18_scratch_CrossMatch.pt"

    # Load the model
    model = load_model(weights_path, device)

    # Preprocess the fingerprint image
    image_tensor = preprocess_image(fingerprint_data)

    # Predict the class (0: Fake, 1: Live)
    preds = predict(model, image_tensor, device)
    class_names = ["Fake", "Live"]

    if preds[0] == 0:
        return True  # Fingerprint is detected as fake
    else:
        return False  # Fingerprint is detected as live

# Define the model architecture
def load_model(weights_path, device):
    model = models.resnet18()
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(num_ftrs, 256),
        nn.ReLU(),
        nn.Dropout(0.4),
        nn.Linear(256, 2),
        nn.LogSoftmax(dim=1)
    )
    model = model.to(device)
    state_dict = torch.load(weights_path, map_location=device)

    # Create a new state dictionary without the 'module.' prefix
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        if k.startswith('module.'):
            new_state_dict[k[7:]] = v  # Strip the 'module.' prefix
        else:
            new_state_dict[k] = v

    # Load the new state dictionary into your model
    model.load_state_dict(new_state_dict)
    model.eval()
    return model

# Function to preprocess the image
def preprocess_image(fingerprint_data):
    preprocess = transforms.Compose([
        transforms.Resize((280, 280)),  # Resize to (280, 280)
        transforms.TenCrop(224),
        transforms.Lambda(lambda crops: torch.stack([transforms.ToTensor()(crop) for crop in crops])),
        transforms.ConvertImageDtype(torch.float),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    image = fingerprint_data.convert("RGB")
    image = preprocess(image)
    image = image.unsqueeze(0)
    return image

# Function to predict the class of the image
def predict(model, image_tensor, device):
    with torch.no_grad():
        bs, ncrops, c, h, w = image_tensor.size()
        image_tensor = image_tensor.view(-1, c, h, w).to(device)
        outputs = model(image_tensor)
        outputs = outputs.view(bs, ncrops, -1).mean(1)
        _, preds = torch.max(outputs, 1)
    return preds.cpu().numpy()

def spoof_guard():
    global is_anti_spoof_enabled
    is_anti_spoof_enabled = not is_anti_spoof_enabled
    tft_clear()
    if is_anti_spoof_enabled:
        tft_message('Anti-Spoof Enabled', 1)
    else:
        tft_message('Anti-Spoof Disabled', 1)
    time.sleep(2)

def normal_fingerprint_search():
    global stop_operation
    try:
        f = initialize_sensor()
        f.convertImage(FINGERPRINT_CHARBUFFER1)
        result = f.searchTemplate()
        positionNumber = result[0]

        if positionNumber >= 0:
            tft_message_four_lines('Template exists', 'Pos #' + str(positionNumber), '', '')
            print(f'Template exists at position #{positionNumber}')
        elif positionNumber == -1:
            tft_message('No match found', 1)
            print('No match found')

    except Exception as e:
        tft_message_four_lines('Search Failed!', str(e), '', '')
        print(f'Search Failed: {e}')
        
def main_menu():
    tft_message('Fingerprint System', 1)
    time.sleep(2)
    tft_message_five_lines('1: Enroll', '2: Delete', '3: Anti Spoof', '4: Back', 'Waiting for finger..')

def main():
    global stop_operation
    tft_init()
    main_menu()
    search_thread = None

    while True:
        if GPIO.input(BUTTON_PINS[0]) == GPIO.LOW:
            stop_operation = True
            if search_thread and search_thread.is_alive():
                search_thread.join()
            stop_operation = False
            tft_message('Enrolling Finger...', 1)
            enroll_finger()
            main_menu()
        elif GPIO.input(BUTTON_PINS[1]) == GPIO.LOW:
            stop_operation = True
            if search_thread and search_thread.is_alive():
                search_thread.join()
            stop_operation = False
            tft_message('Deleting Finger...', 1)
            delete_finger()
            main_menu()
        elif GPIO.input(BUTTON_PINS[2]) == GPIO.LOW:
            stop_operation = True
            if search_thread and search_thread.is_alive():
                search_thread.join()
            stop_operation = False
            tft_message('Toggling Spoof Guard...', 1)
            spoof_guard()
            main_menu()
        elif GPIO.input(BUTTON_PINS[3]) == GPIO.LOW:
            stop_operation = True
            if search_thread and search_thread.is_alive():
                search_thread.join()
            tft_message('Returning to Menu...', 1)
            time.sleep(2)
            main_menu()
        else:
            if search_thread is None or not search_thread.is_alive():
                search_thread = threading.Thread(target=search_finger)
                search_thread.start()

        time.sleep(0.2)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
