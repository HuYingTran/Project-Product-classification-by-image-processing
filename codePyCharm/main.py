from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
import sys
import os
# -------------------------------- thu vien xu ly anh
import cv2
import numpy as np
from pyzbar.pyzbar import decode
# -------------------------------- thu vien giao tiep arduino
import serial
import time

arduino = serial.Serial(port='COM4', baudrate=9600, timeout=.1)

import openpyxl
import datetime

# ----------------------------------------------------------------------------------------------------
min_mau_r1 = np.array([0, 70, 70])  # red1
max_mau_r1 = np.array([10, 255, 255])

min_mau_r2 = np.array([160, 70, 70])  # red2
max_mau_r2 = np.array([179, 255, 255])

min_mau_g = np.array([30, 70, 50])  # green
max_mau_g = np.array([70, 255, 198])

min_mau_y = np.array([20, 50, 50])  # yellow
max_mau_y = np.array([30, 255, 255])

radius = 100
# -------------------------------------- tao class cho file .ui


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('fileGui.ui', self)
        # ----------------------------------- code hien thi webcam
        self.cameraBtn.clicked.connect(self.activeCam)  # ----------------> camera Btn
        self.startBtn.clicked.connect(self.capture_image)#self.startPow)  # ------------------> start Btn
        self.stopBtn.clicked.connect(self.stopPow)  # --------------------> stop Btn
        self.lightBtn.clicked.connect(self.lightProgram)  # ------------------> light Btn
        self.capture = None
        self.timer = QtCore.QTimer(self, interval=5)  # su dung timer de lien tuc tai video len lable
        self.timer.timeout.connect(self.update_frame)
        # ------------------------------------
        self.show()

    # ---------------------------------------------------------------------------------------------- camera Btn
    # function xu ly anh
    def activeCam(self):
        value = self.cameraBtn.text()
        if value == 'OFF':
            self.cameraBtn.setText('ON')
            self.cameraBtn.setStyleSheet("background-color: rgb(0, 255, 0)")
            self.start_webcam()
        else:
            self.cameraBtn.setText('OFF')
            self.cameraBtn.setStyleSheet("background-color : red")
            self.stopVideo()

    # ------------------------------------------------------------ bat camera
    @QtCore.pyqtSlot()
    def start_webcam(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
        self.timer.start()

    # ------------------------------------------------------------ up date video lien tuc theo timer
    @QtCore.pyqtSlot()
    def update_frame(self):
        self.giveData()  # -------------------------------> goi lenh nhan du lieu lien tuc
        ret, image = self.capture.read()
        # image = self.drawing(image, 100)
        # -------------------------------------- hien thi video len lable
        simage = cv2.flip(image, 1)
        qformat = QtGui.QImage.Format_Indexed8
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                qformat = QtGui.QImage.Format_RGBA8888
            else:
                qformat = QtGui.QImage.Format_RGB888
        outImage = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0], qformat)
        outImage = outImage.rgbSwapped()
        if window:
            self.videoLable.setPixmap(QtGui.QPixmap.fromImage(outImage))

    def stopVideo(self):
        self.timer.stop()

    def drawing(self, img, value):
        image = cv2.blur(img, (5, 5))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, thresh_binary = cv2.threshold(gray, value, 255, cv2.THRESH_BINARY)
        canny = cv2.Canny(thresh_binary, 30, 30)
        # cv2.imshow("duongBao", canny)
        cnts, _ = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        shape = image.copy()
        cv2.drawContours(shape, cnts, 0, (0, 255, 0), 2)
        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            center = (int(x), int(y))
            radius = int(radius)
            img = cv2.circle(img, center, radius, (255, 0, 0), 3)
            return img

    def xuLyAnh(self):
        radius = 100
        img = cv2.imread("./my_image.jpg")
        # --------------------------------------------------------<tao mat na>
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask_r1 = cv2.inRange(hsv, min_mau_r1, max_mau_r1)
        mask_r2 = cv2.inRange(hsv, min_mau_r2, max_mau_r2)
        mask_r = cv2.bitwise_or(mask_r1, mask_r2)
        mask_g = cv2.inRange(hsv, min_mau_g, max_mau_g)
        mask_y = cv2.inRange(hsv, min_mau_y, max_mau_y)

        # ---------------------------------------------------red
        image = cv2.bitwise_and(img, img, mask=mask_r)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, thresh_binary = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)

        # thu phong , loc nhieu
        kernel = np.ones((5, 5), np.uint8)
        erosion = cv2.erode(thresh_binary, kernel, iterations=5)
        dilation = cv2.dilate(erosion, kernel, iterations=10)
        erosion = cv2.erode(dilation, kernel, iterations=5)

        canny = cv2.Canny(erosion, 30, 30)
        cnts, _ = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        shape = image.copy()
        cv2.drawContours(shape, cnts, 0, (0, 255, 0), 2)
        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            if int(radius) > 100:
                img = cv2.circle(img, (int(x), int(y)), int(radius), (255, 0, 0), 3)
                print("1")
                self.type1()
                return img

        # ---------------------------------------------------green
        image = cv2.bitwise_and(img, img, mask=mask_g)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, thresh_binary = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)

        # thu phong , loc nhieu
        kernel = np.ones((5, 5), np.uint8)
        erosion = cv2.erode(thresh_binary, kernel, iterations=5)
        dilation = cv2.dilate(erosion, kernel, iterations=10)
        erosion = cv2.erode(dilation, kernel, iterations=5)

        canny = cv2.Canny(erosion, 30, 30)
        cnts, _ = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        shape = image.copy()
        cv2.drawContours(shape, cnts, 0, (0, 255, 0), 2)
        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            if int(radius) > 100:
                img = cv2.circle(img, (int(x), int(y)), int(radius), (255, 0, 0), 3)
                print("2")
                self.type2()
                return img

        # ---------------------------------------------------yellow
        image = cv2.bitwise_and(img, img, mask=mask_y)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, thresh_binary = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)

        # thu phong , loc nhieu
        kernel = np.ones((5, 5), np.uint8)
        erosion = cv2.erode(thresh_binary, kernel, iterations=5)
        dilation = cv2.dilate(erosion, kernel, iterations=10)
        erosion = cv2.erode(dilation, kernel, iterations=5)

        canny = cv2.Canny(erosion, 30, 30)
        cnts, _ = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        shape = image.copy()
        cv2.drawContours(shape, cnts, 0, (0, 255, 0), 2)
        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            if int(radius) > 100:
                img = cv2.circle(img, (int(x), int(y)), int(radius), (255, 0, 0), 3)
                print("3")
                self.type3()
                return img
        print("4")
        self.type4()
        return img


    # ------------------------------------------------------------ code trich xuat anh va hien thi
    @QtCore.pyqtSlot()
    def capture_image(self):
        flag, frame = self.capture.read()
        path = r'G:\My Drive\BTLXuLyAnh\codePyCharm'
        QtWidgets.QApplication.beep()
        img = "my_image.jpg"
        cv2.imwrite(os.path.join(path, img), frame)
        self.image = cv2.imread("./my_image.jpg")
        self.image = self.xuLyAnh()  # ---------------------------------------------------------goi ham < xuLyAnh >
        self.image = QtGui.QImage(self.image.data, self.image.shape[1], self.image.shape[0],
                                  QtGui.QImage.Format_RGB888).rgbSwapped()
        self.imageLable.setPixmap(QtGui.QPixmap.fromImage(self.image))

    # -------------------------------------------------------------------------------------------------------------
    # end code xu ly anh

    # ------------------------------------------------------- nhan du lieu
    def giveData(self):
        data = arduino.readline().decode('utf-8').rstrip()
        if data == "sensor0_on":
            self.capture_image()
            print("phat hien")
        if data == "sensor1_on":
            inputData = str(self.typeLable.text())
            arduino.write(inputData.encode())
            print("robot")

    # ---------------------------------------------------------- xu ly du lieu ( hien thi den bao )
    def type1(self):
        self.typeLable.setText('RED')
        self.sum1.setText(str(int(self.sum1.text()) + 1))
        self.sum.setText(str(int(self.sum.text()) + 1))

    def type2(self):
        self.typeLable.setText("GREEN")
        self.sum2.setText(str(int(self.sum2.text()) + 1))
        self.sum.setText(str(int(self.sum.text()) + 1))

    def type3(self):
        self.typeLable.setText("YELLOW")
        self.sum3.setText(str(int(self.sum3.text()) + 1))
        self.sum.setText(str(int(self.sum.text()) + 1))

    def type4(self):
        self.typeLable.setText("DEFECT")
        print("loai bo")
        self.sum4.setText(str(int(self.sum4.text()) + 1))
        self.sum.setText(str(int(self.sum.text()) + 1))

    # ------------------------------------------------------------

    # ------------------------------------------------------------> pow
    def startPow(self):
        self.img = QPixmap("./icon/denXanh.jpg")
        self.powLable.setPixmap(self.img)
        s = str("startPow")
        arduino.write(s.encode())

    def stopPow(self):
        self.img = QPixmap("./icon/denDo.jpg")
        self.powLable.setPixmap(self.img)
        s = "stopPow"
        arduino.write(bytes(s, 'utf-8'))
        # arduino.write(s.encode())
        # -------------------------------- ghi du lieu vao excel
        wb = openpyxl.load_workbook('./Book1.xlsx')
        sheet_copy = wb.copy_worksheet(wb['Sheet1'])
        dt = datetime.datetime.now()
        print(dt)
        sheet = wb['Sheet1 Copy']
        sheet['C4'] = int(self.sum1.text())
        sheet['C5'] = int(self.sum2.text())
        sheet['C6'] = int(self.sum3.text())
        sheet['C7'] = int(self.sum4.text())
        sheet['B3'] = str(dt)
        wb.save('./Book1.xlsx')

    def lightProgram(self):
        value = self.lightBtn.text()
        if value == "OFF":
            self.lightBtn.setText('ON')
            self.lightBtn.setStyleSheet("background-color: rgb(0, 255, 0)")
            s = str("startLight")
            arduino.write(s.encode())
        if value == "ON":
            self.lightBtn.setText('OFF')
            self.lightBtn.setStyleSheet("background-color: red")
            s = str("stopLight")
            arduino.write(s.encode())


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec()
