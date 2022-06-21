import cv2
import mvsdk
import numpy as np
import scipy
from scipy import ndimage
from matplotlib import pyplot as plt
import time
import threading as th
import queue

plt.rcParams.update({'figure.max_open_warning': 0})

DO_BINARY_FILTER = True  # Выполнять Binary opening/closing или нет
TOTAL_CYCLES = 1  # Количество циклов картирования
MEAN_FRAME_NUM = 5  # Число кадров для получения усредненного базового
BINARY_FILTER_SIZE = 15  # Размер стороны квадрата для binary opening/closing
CAMERA_EXPOSITION = 25  # Экспозиция в мс

if not DO_BINARY_FILTER:
    BINARY_FILTER_SIZE = 0
appExit = False
mappingStart = False
# Очередь для хранения 5 последних обработнных кадров, она безопасна при работе с потоками, они встают в свою очередь на получение и наполнение
q = queue.Queue(5)
fig, (ax1, ax2) = plt.subplots(2)
fig.set_figwidth(10)
fig.set_figheight(10)
fig.set_dpi(150)
fig.subplots_adjust(hspace=0.2)
textToShow = "Press S to start mapping or Q to exit"


def main(condition):  # Основной цикл для OpenCV окна и управления
    global appExit, textToShow, mappingStart
    camera = th.Thread(target=camera_thread, name='camera_thread', daemon=True)
    mapping = th.Thread(target=mapping_thread, args=(condition,), name='mapping_thread', daemon=True)
    camera.start()  # Начало работы потока получения кадров из камеры
    mapping.start()  # Начало работы потока, осуществляющего обработку кадров
    while (cv2.waitKey(1) & 0xFF) != ord('q'):
        if (cv2.waitKey(1) & 0xFF) == ord('s') and not mappingStart:
            mappingStart = True
            with condition:
                condition.notify()  # Даём сигнал о начале процедуры обрабатывающему потоку
        if not q.empty():
            frame = q.get()
            interfaceFrame = cv2.copyMakeBorder(frame, 0, 400, 0, 0, cv2.BORDER_CONSTANT, value=0)
            interfaceFrame = cv2.resize(interfaceFrame, (800, 600), interpolation=cv2.INTER_LINEAR)
            interfaceFrame = cv2.putText(interfaceFrame, textToShow, (20, 550),
                                         cv2.FONT_ITALIC, 0.7, color=65408, thickness=1)
            cv2.imshow("Mapping", interfaceFrame)
    appExit = True
    if mapping.is_alive():
        with condition:
            condition.notify()  # Если поток ожидал сигнала, то даём его, чтобы он спокойно завершился
        mapping.join()
    camera.join()  # Дожидаемся завершения двух потоков
    plt.close()
    cv2.destroyAllWindows()


def mapping_thread(condition):  # Обрабатывающих кадры поток
    global appExit, textToShow, mappingStart
    labels = ('Thumb', 'Index finger', 'Middle finger', 'Ring finger', 'Pinky finger')
    colors = ('red', 'orange', 'yellow', 'green', 'blue')
    while not appExit:  # Внешний while, отвечающий за стартовую инициализацию, и выход из потока
        textToShow = "Press S to start mapping or Q to exit"
        mappingState = False
        with condition:
            condition.wait()  # Ожидание сигнала о начале процедуры картирования
        for i in range(TOTAL_CYCLES):
            fingerCounter = 0
            timeStart = time.time() + 10
            textToShow = "Cycle " + str(i + 1) + " will start in 10 seconds, get ready"
            while not appExit:  # Этот while ожидает 10 секунд до начала процедуры, в любой момент можно выйти
                if time.time() > timeStart:
                    contours = []
                    frame = q.get()  # Получили кадр и назначили его фоном для выходных графиков matplotlib
                    ax1.imshow(frame, cmap='gray')
                    ax2.imshow(frame, cmap='gray')
                    # Внутри while ниже происходит работа по получению кадров и контуров,
                    # ожидание 5 секунд между сгибом-разгибом, можно выйти в любой момент, промежуточные результаты цикла не сохраняются
                    while fingerCounter < 5 and not appExit:
                        if not mappingState and time.time() > timeStart:  # if для получения базового кадра
                            if MEAN_FRAME_NUM > 1:
                                frames = []
                                for j in range(MEAN_FRAME_NUM):
                                    frame = q.get() #Получаем кадр
                                    frame = frame.astype(np.single) #Переводим кадр во float, чтобы корректно работали все операции
                                    frames.append(frame) #Добавляем кадр в массив, чтобы ниже получить усредненный
                                baseFrame = np.mean(frames, axis=0).astype(np.single)
                            else:
                                baseFrame = q.get()
                                baseFrame = baseFrame.astype(np.single) #Переводим кадр во float, чтобы корректно работали все операции
                            baseFrame = scipy.ndimage.gaussian_filter(baseFrame, sigma=5, truncate=4) #Накладываем фильтр Гаусса, ядро 20
                            textToShow = "You have 5 seconds to bend your " + str(labels[fingerCounter])
                            timeStart = time.time() + 5
                            mappingState = True
                        if mappingState and time.time() > timeStart:
                            bendFrame = q.get() #Получаем кадр
                            bendFrame = bendFrame.astype(np.single) #Переводим кадр во float, чтобы корректно работали все операции
                            bendFrame = scipy.ndimage.gaussian_filter(bendFrame, sigma=5, truncate=4) #Накладываем фильтр Гаусса, ядро 20
                            if fingerCounter < 4:
                                textToShow = "You have 5 seconds to extend your finger back"
                                timeStart = time.time() + 5
                            else:
                                textToShow = "Cycle " + str(i + 1) + " is done, please wait"
                            bendFrame = np.subtract(bendFrame, baseFrame)
                            bendFrame = np.divide(bendFrame, baseFrame) #Получаем OS
                            minMask = (bendFrame < np.percentile(bendFrame, 5)).astype(np.single) #Получаем 5% самых маленьких чисел
                            maxMask = (bendFrame > np.percentile(bendFrame, 95)).astype(np.single) #Получаем 5% самых больших чисел
                            if DO_BINARY_FILTER:
                                minMask = scipy.ndimage.binary_opening(minMask,
                                                                       np.ones(
                                                                           (BINARY_FILTER_SIZE, BINARY_FILTER_SIZE)))
                                minMask = scipy.ndimage.binary_closing(minMask,
                                                                       np.ones(
                                                                           (BINARY_FILTER_SIZE, BINARY_FILTER_SIZE)))
                                maxMask = scipy.ndimage.binary_opening(maxMask,
                                                                       np.ones(
                                                                           (BINARY_FILTER_SIZE, BINARY_FILTER_SIZE)))
                                maxMask = scipy.ndimage.binary_closing(maxMask,
                                                                       np.ones(
                                                                           (BINARY_FILTER_SIZE, BINARY_FILTER_SIZE)))
                            c1 = ax1.contour(minMask, [0.5], colors=colors[fingerCounter])
                            ax2.contour(maxMask, [0.5], colors=colors[fingerCounter])
                            contours.append(c1)
                            fingerCounter += 1 #Всего 5 пальцев - 5 раз ходим внутри последнего while
                            mappingState = False
                    break #После окончания просто выходим из двух while'ов
            if appExit: #Если была нажата кнопка выхода, то выходим без сохранения результата
                break
            else:
                fig.suptitle(
                    "Cycle " + str(i + 1) + ", baseFrameMeanNum = " + str(
                        MEAN_FRAME_NUM) + ", binaryFilterSize = " + str(
                        BINARY_FILTER_SIZE))
                ax1.set_title('minMask')
                ax2.set_title('maxMask')
                proxy = [plt.Rectangle((0, 0), 1, 1, fc=contour.collections[0].get_edgecolor()) for contour in contours]
                ax1.legend(proxy, labels, bbox_to_anchor=[1.01, 1], loc='upper left')
                plt.savefig("result/cycle" + str(i + 1) + ".png") #Сохраняем результат цикла N по пути ПАПКА_С_ПРОЕКТОМ/result/cycleN.png
                ax1.clear()
                ax2.clear()
        mappingStart = False #Говорим потоку main, что завершили картирование, можно сохранить результаты и снова начать без перезапуска


def camera_thread(): #Поток для работы с камерой
    global appExit
    DevList = mvsdk.CameraEnumerateDevice()  # Формирование списка подключенных поддерживаемых камер
    nDev = len(DevList)
    if nDev != 1:
        raise RuntimeError('No or more cameras found!')
    try:
        hCamera = mvsdk.CameraInit(DevList[0], -1, -1)  # Инициализация камеры и получение её handler'а
    except mvsdk.CameraException as e:
        raise RuntimeError('CameraInit Failed({}): {}'.format(e.error_code, e.message))
    cap = mvsdk.CameraGetCapability(hCamera)  # Получение возможностей камеры
    mvsdk.CameraSetMediaType(hCamera, 1)  # Формат RAW-данных - 12 бит (Packed) - то есть 10 бит со странным расположением бит,
    # По алгоритму упаковки кадров информации нет, как и общего решения в интернете, у всех по-своему
    mvsdk.CameraSetIspOutFormat(hCamera, mvsdk.CAMERA_MEDIA_TYPE_MONO16)  # Формат пикселей в буфере после обработки
    mvsdk.CameraSetTriggerMode(hCamera, 0)  # Режим постоянной съемки (без стробирования)
    mvsdk.CameraSetAeState(hCamera, 0)  # Отключение автоматической экспозиции
    mvsdk.CameraSetExposureTime(hCamera, CAMERA_EXPOSITION * 1000)  # Установка экспозиции на заданное значение мс
    mvsdk.CameraPlay(hCamera)  # Запуск камеры
    # Выделяем место для буфера изображения - пикселей в ширину*пикселей в длину*количество байт для пикселя
    FrameBufferSize = cap.sResolutionRange.iWidthMax * cap.sResolutionRange.iHeightMax * 2
    pFrameBuffer = mvsdk.CameraAlignMalloc(FrameBufferSize, 16)  # Говорим камере, где буфер
    while not appExit:
        try:
            pRawData, FrameHead = mvsdk.CameraGetImageBuffer(hCamera, 200)  # Получение RAW-изображения
            mvsdk.CameraImageProcess(hCamera, pRawData, pFrameBuffer,
                                     FrameHead)  # Обработка RAW (Баланс белого, насыщенность цвета, яркость, шум и т.д.)
            mvsdk.CameraReleaseImageBuffer(hCamera, pRawData)  # Освобождение буфера с RAW-изображением

            mvsdk.CameraFlipFrameBuffer(pFrameBuffer, FrameHead,
                                        1)  # В Windows изображение нужно перевернуть, так как исходное отражено зеркально и перевернуто
            # Далее идет формирование необходимого numpy-массива из буфера-не-массива
            frame_data = (mvsdk.c_ubyte * FrameHead.uBytes).from_address(pFrameBuffer)
            frame = np.frombuffer(frame_data, dtype=np.uint16)
            frame = frame.reshape((FrameHead.iHeight, FrameHead.iWidth))
            q.put(frame) # Закидываем кадр в очередь, если она переполнена, то просто ждем
        except mvsdk.CameraException as e:
            if e.error_code != mvsdk.CAMERA_STATUS_TIME_OUT:
                print("CameraGetImageBuffer failed({}): {}".format(e.error_code, e.message))
    #При завершении работы деинициализируем камеру, иначе нельзя будет найти камеру (она считается занятой), освобождаем буфер
    mvsdk.CameraUnInit(hCamera)
    mvsdk.CameraAlignFree(pFrameBuffer)


condition = th.Condition() #создаем условие для того, чтобы запускать поток обработки в момент нажатия кнопки
main(condition)
