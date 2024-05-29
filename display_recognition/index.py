# import the necessary packages # https://www.pyimagesearch.com/2017/02/13/recognizing-digits-with-opencv-and-python/
from imutils.perspective import four_point_transform
from imutils import contours
import imutils
import cv2
import boto3
import numpy as np
import urllib
import numpy
import base64
import json

def url_to_image(url):
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    return image

def base64_to_image(path_image):
    with open(path_image) as file:
        base64_content = file.readlines()

    encoded_data = base64_content[0].split(',')[1]
    
    nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    return img

def final_result(result_list, qty_decimal_digit):
    integer_digits = result_list[:-qty_decimal_digit] #Pegando apenas os inteiros
    decimal_digits = result_list[-qty_decimal_digit:] #Pegando apenas os decimais

    integer_digits_str = ''.join(str(e) for e in integer_digits)
    decimal_digits_str = ''.join(str(e) for e in decimal_digits)

    return f"{integer_digits_str}.{decimal_digits_str}"

def brightness_and_contrast(image, clip_hist_percent=1): #https://stackoverflow.com/questions/57030125/automatically-adjusting-brightness-of-image-with-opencv #https://stackoverflow.com/questions/56905592/automatic-contrast-and-brightness-adjustment-of-a-color-photo-of-a-sheet-of-pape
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    hist = cv2.calcHist([gray],[0],None,[256],[0,256]) # Calculate grayscale histogram
    hist_size = len(hist)

    accumulator = [] # Calculate cumulative distribution from the histogram
    accumulator.append(float(hist[0]))
    for index in range(1, hist_size):
        accumulator.append(accumulator[index -1] + float(hist[index]))

    maximum = accumulator[-1] # Locate points to clip
    clip_hist_percent *= (maximum/100.0)
    clip_hist_percent /= 2.0

    minimum_gray = 0 # Locate left cut
    while accumulator[minimum_gray] < clip_hist_percent:
        minimum_gray += 1

    maximum_gray = hist_size -1 # Locate right cut
    while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
        maximum_gray -= 1

    # Calculate alpha and beta values #alpha e o contraste, beta e o brilho da imagem
    alpha = 255/(maximum_gray - minimum_gray)
    beta = -minimum_gray*alpha
    
    auto_result = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta) #O pixel que tinha o menor valor de cinza se tranforma em 0 e o que tinha maior se transforma em 255
    
    return auto_result, minimum_gray, maximum_gray

def display_outline_coordinates(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200, 255)

    cv2.imwrite("result/edged_image.jpg", edged) #salvando a imagem para visualizar as bordas criadas

    # find contours in the edge map, then sort them by their # size in descending order
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    displayCnt = None

    # loop over the contours
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # if the contour has four vertices, then we have found
        # the thermostat display
        if len(approx) == 4:
            displayCnt = approx
            break

    return displayCnt

def apply_threshold(image):
    warped_with_brightness, minimum_gray, maximum_gray = brightness_and_contrast(image)
    cv2.imwrite("result/warped_with_brightness.jpg", warped_with_brightness) #salvando a imagem para visualizar o threshold
    warped_with_blur = cv2.medianBlur(warped_with_brightness,7) #Aplicando um Blur para misturar os pixels

    avg_color_per_row = numpy.average(warped_with_blur, axis=0) #tirando a media dos pixels de cada linha da imagem
    avg_color = numpy.average(avg_color_per_row, axis=0) #tirando a media de todas as medias das linhas (media de todos os pixels juntos)

    print(f"avg_color {avg_color}")
    print(f"((minimum_gray+maximum_gray)/2) {((minimum_gray+maximum_gray)/2)}")
    print(f"minimum_gray {minimum_gray}")
    print(f"maximum_gray {maximum_gray}")

    if avg_color > 127: #se a media de pixels for maior que 127 o fundo do display e claro e os numeros escuros
        thresh = cv2.threshold(warped_with_blur, 127, 255, cv2.THRESH_BINARY_INV)[1] # ((minimum_gray+maximum_gray)/2)
    else: #se a media de pixels for menor que 127 o fundo do display e escuro e os numeros sao claros
        thresh = cv2.threshold(warped_with_blur, 127, 255, cv2.THRESH_BINARY)[1]
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5)) #https://docs.opencv.org/4.5.2/d9/d61/tutorial_py_morphological_ops.html

    opening  = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel) #Limpando pixels brancos fora dos numeros
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel) #Limpando pixels preto dentro dos numeros
    dilation = cv2.dilate(closing, kernel, iterations=5) #Aumentando a densidade do segmento para facilitar no reconhecimento

    return dilation

def check_numbers_on_display(thresh, output):

    DIGITS_LOOKUP = { #Posicao dos segmentos
        (1, 1, 1, 0, 1, 1, 1): 0,
        (0, 0, 1, 0, 0, 1, 0): 1,
        (1, 0, 1, 1, 1, 0, 1): 2,
        (1, 0, 1, 1, 0, 1, 1): 3,
        (0, 1, 1, 1, 0, 1, 0): 4,
        (1, 1, 0, 1, 0, 1, 1): 5,
        (1, 1, 0, 1, 1, 1, 1): 6,
        (1, 0, 1, 0, 0, 1, 0): 7,
        (1, 1, 1, 1, 1, 1, 1): 8,
        (1, 1, 1, 1, 0, 1, 1): 9,
    }

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #Encontra os contornos da imagem com o threshold aplicado
    cnts = imutils.grab_contours(cnts)
    digitCnts = []

    height, width = thresh.shape #pegando a altura (h) e largura (w) do thresh
    
    for c in cnts: # loop over the digit area candidates
        (x, y, w, h) = cv2.boundingRect(c) # compute the bounding box of the contour

        if w >= 25 and (h >= height/2 and h <= height): #if the contour is sufficiently large, it must be a digi
            digitCnts.append(c)

    # sort the contours from left-to-right, then initialize the actual digits themselves
    digitCnts = contours.sort_contours(digitCnts, method="left-to-right")[0]
    digits = []

    for c in digitCnts: # loop over each of the digits
        (x, y, w, h) = cv2.boundingRect(c)

        if w <= h//4: #Se a proporcao for menor que 2x1 provavelmente e o numero 1
            x = x - int((h-w)/2) #Faz com que x comece atras do numero ser printado
            w = int((h-w)/2) + w #Coloca no w o valor da nova largura
            roi = thresh[y:y+h, x:x+w] #cortando o numero para fazer a analise
        else:
            roi = thresh[y:y+h, x:x+w] #cortando o numero para fazer a analise

        (roiH, roiW) = roi.shape #pegando a altura (roiH) e largura (roiW) do roi

        # calculam a largura e altura aproximadas de cada segmento com base nas dimensões
        (dW, dH) = (int(roiW * 0.25), int(roiH * 0.15))
        dHC = int(roiH * 0.05) #pegando o meio do roi

        # Define os segmentos de acordo com a altura e largura do numero
        segments = [
            ((0, 0), (w, dH)),	# top
            ((0, 0), (dW, h // 2)),	# top-left
            ((w - dW, 0), (w, h // 2)),	# top-right
            ((0, (h // 2) - dHC) , (w, (h // 2) + dHC)), # center
            ((0, h // 2), (dW, h)),	# bottom-left
            ((w - dW, h // 2), (w, h)),	# bottom-right
            ((0, h - dH), (w, h))	# bottom
        ]
        on = [0] * len(segments)

        # loop over the segments
        for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
            # extract the segment ROI, count the total number of thresholded pixels in the segment, and then compute the area of the segment
            
            segROI = roi[yA:yB, xA:xB]
            total = cv2.countNonZero(segROI)
            area = (xB - xA) * (yB - yA)
            # if the total number of non-zero pixels is greater than 50% of the area, mark the segment as "on"
            if area != 0:
                if total / float(area) > 0.5:
                    on[i]= 1

        # lookup the digit and draw it on the image
        digit = DIGITS_LOOKUP[tuple(on)] if DIGITS_LOOKUP.get(tuple(on)) else 0
            
        digits.append(digit)
        cv2.rectangle(output, (x, y), (x + w, y + h), (255, 0, 255), 3)
        cv2.putText(output, str(digit), (x + w + 10, y + h), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 100, 0), 3)

    return digits

def handler(event, context):
    print(f'received event: {event}')

    path_image = event.get('img')
    qty_decimal_digit = event.get('decimalQty')
    source = event.get('source')

   #Fazendo o load da imagem
    if source == "base64":
        image = base64_to_image(path_image)
    elif source == "s3":
        image = s3_to_image(path_image=path_image, key=path_image)

    image = imutils.resize(image, height=500) #Aplicando um redicionamento para deixar a imagem plana

    displayCnt = display_outline_coordinates(image)

    output = four_point_transform(image, displayCnt.reshape(4, 2)) #Cortando a imagem para trabalhar apenas com o display da balanca

    thresh = apply_threshold(output) #Aplicando o threshold
    cv2.imwrite("result/apply_threshold.jpg", thresh) #salvando a imagem para visualizar o threshold

    digits = check_numbers_on_display(thresh, output)

    final_result = final_result(digits, qty_decimal_digit)

    response = {
        'statusCode': 200,
        'data': {digits: 2.22},
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps('Hello from your new Amplify Python lambda!')
    }
    return response


event = { "source": "s3", "decimalQty": 3, "img": "h94h4t4gikj0xp7dts5r1xkhg1tq"}
context = "blblbalbla"

handler(event, context)