# https://docs.opencv.org/3.4/da/d7f/tutorial_back_projection.html
# https://docs.opencv.org/3.4/d7/d00/tutorial_meanshift.html
import cv2
import numpy as np
cropping = False
x_start, y_start, x_end, y_end = 0, 0, 0, 0
# 10: iteration of algorithm, 1: how many points is going to move
term_criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

video = cv2.VideoCapture(0)
roi_hist = [] 
def mouse_crop(event, x, y, flags, param):
    # Define las variables globales para que el evento las sobre-escriba
    global x_start, y_start, x_end, y_end, cropping, roi_hist
    # Al dar clic con el mouse, obtener las coordenadas.
    # (x, y) El recorte empieza con el clic
    if event == cv2.EVENT_LBUTTONDOWN:
        x_start, y_start, x_end, y_end = x, y, x, y
        cropping = True
    # El recorte se comienza a mover, capturando continuamente
    elif event == cv2.EVENT_MOUSEMOVE:
        if cropping == True:
            x_end, y_end = x, y
    # Al liberar el botón derecho del mouse, calculamos la imágen recortada
    elif event == cv2.EVENT_LBUTTONUP:
        # (x, y) Coordenadas finales
        x_end, y_end = x, y
        cropping = False # Bandera de recorte finalizado
        refPoint = [(x_start, y_start), (x_end, y_end)]
        if len(refPoint) == 2: #Tupla con ambas coordenadas
            roi = oriframe[refPoint[0][1]:refPoint[1][1], refPoint[0][0]:refPoint[1][0]]
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            cv2.imshow("Cropped", roi)
            roi_hist = cv2.calcHist([hsv_roi], [0], None, [180], [0, 180])
            #Si imprimimos el histograma podemos ver los máximos, queremos que el máximo sea 255
            # print(roi_hist)
            # Entonces normalizamos los datos de 0-255
            roi_hist = cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)
            # print(roi_hist)
            
cv2.namedWindow("frame")
cv2.setMouseCallback("frame", mouse_crop)

while True:
    _, frame = video.read()
    if not cropping:
        cv2.imshow("frame", frame)
        
        # Checar si ya hay algo recortado
        if len(roi_hist) > 1:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
            # En esta mascara, la parte blanca es donde el histograma más coincide
            
            '''
            En este punto, el algorítmo meanshift encontrará el área de máxima concentración de puntos blancos
            que obtuvimos con la mascara
            Problemas con el algorítmo. Da por hecho un tamaño constante.
            Toma la última posición para detectar la concentración de white points, falla si lo mueves rápido hasta que regreses
            el objeto.
            '''
            #obtener la posición con mayor concentración de blanco meanshift
            _ , track_window = cv2.meanShift(mask, (x_start, y_start, x_end - x_start, y_end - y_start), term_criteria)
            print(track_window)
            x, y, w, h = track_window
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0),3)
            
            cv2.imshow("mask", mask)
            cv2.imshow("frame", frame)
            
    elif cropping:
        i = frame.copy()
        oriframe = i
        cv2.rectangle(i, (x_start, y_start), (x_end, y_end), (255, 0, 0), 2)
        cv2.imshow("frame", i)
        
    key = cv2.waitKey(200)
    # Esc Key para salir
    if key == 27:
        break
# close all open windows
video.release()
cv2.destroyAllWindows()