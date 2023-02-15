import cv2 as cv
import numpy as np
from pytesseract import pytesseract
import requests
import json

# Thresholds
green_thresh = 70
blue_thresh = 75
red_thresh = 80
black_thresh = 75


def empty(x):
    pass

def read_titlebox(image):
    # Threshold the image to 5 threshold values
    thresholds = [65, 75, 80, 85, 90]
    for thresh in thresholds:
        t, threshold_image = cv.threshold(image, thresh, 255, cv.THRESH_BINARY) # Get the threshold
        # Get reading from pytesseract
        characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ- '"
        parsed_words = ''
        detected_words = pytesseract.image_to_string(threshold_image)
        for char in detected_words:
            if char in characters:
                parsed_words += char
        # Next Threshold if we don't get any parsed characters
        if parsed_words == '':
            continue
        # Look up on scryfall API to find the closest card
        payload = {'q':parsed_words}
        card_autocomplete = requests.get('https://api.scryfall.com/cards/autocomplete', params=payload)
        card_json = json.loads(card_autocomplete.text)
        predicted_cards = card_json['data']
        if len(predicted_cards) >= 1:
            return predicted_cards[0]
        else:
            continue
    return None

def get_titlebox(edges, frame):
    ''' Gets the image of the titlebox if one is detected '''
    # Get contours and minimum areas from edges
    conts, h = cv.findContours(edges, mode=cv.RETR_EXTERNAL, method=cv.CHAIN_APPROX_NONE)
    minArea = 16000
    # Draw Contours
    mask = np.zeros(frame.shape[:2], dtype='uint8')
    masked_grayscale = None
    for cnt in conts:
        # Filter by area and perimeter
        if cv.contourArea(cnt) >= minArea:
            if cv.arcLength(cnt, closed=True) > 1000:
                # Mask the image with the contour
                cv.drawContours(mask, [cnt], contourIdx=-1, color=255, thickness=-1)
                cv.drawContours(frame, [cnt], contourIdx=-1, color=(255,0,255), thickness=2)
                masked_image = cv.bitwise_and(frame, frame, mask=mask)
                # grayscale the image
                masked_grayscale = cv.cvtColor(masked_image, code=cv.COLOR_BGR2GRAY)
    return masked_grayscale

# Establish pytesseract
t_path = r'C:\Users\gamer\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
pytesseract.tesseract_cmd = t_path

if __name__ == '__main__':
    # Get videofeed from webcam
    video = cv.VideoCapture(0)

    cv.namedWindow('Masked Image')
    cv.createTrackbar('ThresholdVal', 'Masked Image', 88, 255, empty)

    scanned_cards = []
    waiting = False
    wait_cycle = 0
    attempts = 0
    while True:
        isTrue, frame = video.read()
        if waiting:
            # Add a targeting rectangle
            cv.rectangle(frame, pt1=(20,frame.shape[0]//2 - 30), pt2=(frame.shape[1] - 50,frame.shape[0]//2 + 30), thickness=1, color=(0,0,255))
            cv.putText(frame, text='Waiting...', org=(20,frame.shape[0]//2 - 40), fontFace=cv.FONT_HERSHEY_COMPLEX,
                       fontScale=0.5, color=(0,0,255), thickness=1)
            # Show image
            cv.imshow('Frame', frame)
            # Leave Wait Cycle Condition
            wait_cycle += 1
            if wait_cycle >= 100:
                wait_cycle = 0
                waiting = False
        else:
            blur = cv.GaussianBlur(frame, ksize=(5,5), sigmaX=2)
            # Use thresholds (alter with cv.getTrackbarpos)
            t1 = 31
            t2 = 40
            # Get the contours cut out the title box
            canny = cv.Canny(blur, threshold1=t1, threshold2=t2)
            masked_image = get_titlebox(canny, frame)
            # Add a targeting rectangle
            cv.rectangle(frame, pt1=(20,frame.shape[0]//2 - 30), pt2=(frame.shape[1] - 50,frame.shape[0]//2 + 30), thickness=1, color=(0,0,0))
            cv.putText(frame, text='Place Card Title Box Here', org=(20,frame.shape[0]//2 - 40), fontFace=cv.FONT_HERSHEY_COMPLEX,
                       fontScale=0.5, color=(0,0,0), thickness=1)
            # Show the UI image
            cv.imshow('Frame', frame)
            # If we have a masked image, try to read it
            try:
                cv.imshow('Masked Image', masked_image)
                attempts += 1
                predicted_word = read_titlebox(masked_image)
                if predicted_word:
                    if predicted_word not in scanned_cards:
                        scanned_cards.append(predicted_word) # Add the card if not already added
                        waiting = True
                        print(f'Added Card: {predicted_word}')
                    else:
                        waiting = True
                        print('Card already scanned!')

                elif attempts >= 60:
                    attempts = 0
                    waiting = True
                    print('Could not scan card')
            except:
                pass

        if cv.waitKey(1) & 0xFF==ord('d'):
            break

    video.release()
    cv.destroyAllWindows()