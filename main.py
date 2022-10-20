from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from numpy import matmul as mult, array

from PyQt5.QtGui import QPixmap
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt

import sys

from math import cos, sin, pi


class Point:
    def __init__(self, coordinates, color="#bF311A"):
        self.coordinates = coordinates
        self.color = color

    def __getitem__(self, key):
        return self.coordinates[key]

    def crds(self):
        return self.coordinates

    def set_color(self, color):
        self.color = color


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('geoVisualiser.ui', self)

        self.points = {}
        self.field = Image.new('RGB', (700, 700), (255, 255, 255))
        self.connectionsText = {self.pointOne: '',
                                self.pointTwo: ''}
        self.connected_points = []

        self.pointPressed = ''
        self.systemPoints = [Point([0, 0, 0]),

                             Point([0, 0, -300]),  # Ось Z
                             Point([0, 0, 300]),

                             Point([0, 300, 0]),  # Ось Y
                             Point([0, -300, 0]),

                             Point([300, 0, 0]),  # Ось X
                             Point([-300, 0, 0]),

                             Point([320, 0, 0]),  # X
                             Point([0, 320, 0]),  # Y
                             Point([0, 0, 320])]  # Z
        self.lastAxis = 'x'
        self.redraw()

        self.set_img(self.field)

        self.addButton.clicked.connect(self.add_point_to_list)
        self.connectPoints.clicked.connect(self.add_connected_points)
        self.disconnectPoints.clicked.connect(self.del_connected_points)
        self.delButton.clicked.connect(self.del_point_from_list)
        self.pointList.itemPressed.connect(self.item_pressed)
        self.xRotate.valueChanged.connect(self.redraw)
        self.yRotate.valueChanged.connect(self.redraw)
        self.zRotate.valueChanged.connect(self.redraw)

        self.pointOne.currentTextChanged.connect(self.current_text_changed)
        self.pointTwo.currentTextChanged.connect(self.current_text_changed)

    def add_point_to_list(self):
        if self.pointInput.text() != '':
            try:
                self.points[self.pointInput.text().split()[0]] = self.pointInput.text().split()[1]
            except IndexError:
                self.pointInput.setText('ОШИБКА ВВОДА')
                return
            literal = list(self.points.keys())[-1]

            self.pointList.addItem(literal + ' ' + (self.points[literal]))
            self.pointOne.addItem(literal)
            self.pointTwo.addItem(literal)

            self.points[literal] = Point(list(map(int, self.points[literal].strip('()').split(','))))

            self.pointInput.setText('')

        self.redraw()

    def del_point_from_list(self):
        try:
            if self.pointPressed != '':
                self.pointList.takeItem(self.pointList.row(self.pointPressed))
                self.points.pop(self.pointPressed.text().split()[0])
                self.pointOne.clear()
                self.pointTwo.clear()
                try:
                    i = 0
                    while i < len(self.connected_points):
                        if self.pointPressed.text().split()[0] in self.connected_points[i]:
                            del self.connected_points[i]
                            i -= 1
                        i += 1
                except ValueError:
                    pass
                for i in self.points:
                    self.pointOne.addItem(i[0])
                    self.pointTwo.addItem(i[0])
        except KeyError:
            pass

        self.redraw()

    def add_connected_points(self):
        if tuple([min(self.connectionsText[self.pointOne], self.connectionsText[self.pointTwo]),
                  max(self.connectionsText[self.pointOne],
                      self.connectionsText[self.pointTwo])]) not in self.connected_points:
            self.connected_points.append(
                tuple([min(self.connectionsText[self.pointOne], self.connectionsText[self.pointTwo]),
                       max(self.connectionsText[self.pointOne], self.connectionsText[self.pointTwo])]))
        self.redraw()

    def del_connected_points(self):
        try:
            del self.connected_points[self.connected_points.index(
                tuple([min(self.connectionsText[self.pointOne], self.connectionsText[self.pointTwo]),
                       max(self.connectionsText[self.pointOne], self.connectionsText[self.pointTwo])]))]
        except ValueError:
            pass
        self.redraw()

    def draw_line(self, p1, p2, line='common', color='#bF311A'):
        drawer = ImageDraw.Draw(self.field)
        point1 = p1.crds()
        point2 = p2.crds()

        if line == 'common':
            drawer.line(((self.convert_system(point1)), self.convert_system(point2)), color, width=3)
        elif line == 'splited':
            start = point1
            add = list(map(lambda x: x // 10, self.vector(point1, point2)))
            add2 = list(map(lambda x: x // 20, self.vector(point1, point2)))
            while self.vector_lenth(start, point1) < self.vector_lenth(start, point2):
                drawer.line((self.convert_system(point1),
                             (point1[0] - int(0.5 * point1[2]) + 350 + (add2[0] - int(0.5 * add2[2])),
                              350 - (point1[1] - int(0.5 * point1[2])) - (add2[1] - int(0.5 * add2[2])))),
                            color, width=1)
                point1 = [point1[0] + add[0], point1[1] + add[1], point1[2] + add[2]]
        self.set_img(self.field)

    def current_text_changed(self, text):
        self.connectionsText[self.sender()] = text

    def item_pressed(self, item):
        point = self.newPoints[item.text().split()[0]]
        self.pointPressed = item
        color = self.points[item.text().split()[0]].color
        self.points[item.text().split()[0]].set_color('#50AAAA')
        self.redraw()

        def func(a1, a2, a3, p1, p2, p3):
            self.draw_line(Point([a1, a2, a3]),
                           Point([p1, p2, p3]), line='splited', color='#50AAAA')

        if point[0] and point[1] and point[2]:
            func(point[0], point[1], point[2], point[0], point[1], 0)
            func(point[0], point[1], 0, point[0], 0, 0)
            func(point[0], point[1], 0, 0, point[1], 0)

            func(point[0], point[1], point[2], point[0], 0, point[2])
            func(point[0], 0, point[2], point[0], 0, 0)
            func(point[0], 0, point[2], 0, 0, point[2])

            func(point[0], point[1], point[2], 0, point[1], point[2])
            func(0, point[1], point[2], 0, 0, point[2])
            func(0, point[1], point[2], 0, point[1], 0)
        elif point[0] and point[1] and not point[2]:
            func(point[0], point[1], 0, point[0], 0, 0)
            func(point[0], point[1], 0, 0, point[1], 0)
        elif point[0] and not point[1] and point[2]:
            func(point[0], point[1], point[2], 0, 0, point[2])
            func(point[0], point[1], point[2], point[0], 0, 0)
        elif not point[0] and point[1] and point[2]:
            func(point[0], point[1], point[2], 0, 0, point[2])
            func(point[0], point[1], point[2], 0, point[1], 0)
        self.points[item.text().split()[0]].set_color(color)

    def rotate(self, point, x, y, z):
        angleX, angleY, angleZ = (x / 180 * pi), (y / 180 * pi), (z / 180 * pi)
        newPoint = self.multiply([[1, 0, 0],
                                  [0, cos(angleX), -sin(angleX)],
                                  [0, sin(angleX), cos(angleX)]],
                                 [[cos(angleZ), sin(angleZ), 0],
                                  [-sin(angleZ), cos(angleZ), 0],
                                  [0, 0, 1]])
        newPoint = self.multiply(newPoint,
                                 [[cos(angleY), 0, sin(angleY)],
                                  [0, 1, 0],
                                  [-sin(angleY), 0, cos(angleY)]])
        newPoint = Point(self.multiply(newPoint, point.crds()))
        return newPoint

    def redraw(self):
        try:
            drawer = ImageDraw.Draw(self.field)
            drawer.polygon(((0, 0), (0, 700), (700, 700), (700, 0)), "#FFFFFF")
            self.newPoints = {}
            self.newSystem = []
            for i in self.points.keys():
                self.newPoints[i] = self.rotate(self.points[i], self.xRotate.value(), self.zRotate.value(),
                                                self.yRotate.value())
                self.newPoints[i].set_color(self.points[i].color)
            for point in self.systemPoints:
                self.newSystem.append(self.rotate(point, self.xRotate.value(), self.zRotate.value(), self.yRotate.value()))
            if self.freezeSystem.isChecked():
                self.newSystem = self.systemPoints
            self.draw_system()
            for points in self.connected_points:
                self.draw_line(self.newPoints[points[0]], self.newPoints[points[1]])
            for point in self.newPoints.keys():
                color = self.newPoints[point].color
                point = self.newPoints[point].crds()
                drawer.ellipse(
                    ((point[0] - int(0.5 * point[2]) - 3 + 350, 350 - (point[1] - int(0.5 * point[2])) - 3),
                     (point[0] - int(0.5 * point[2]) + 3 + 350, 350 - (point[1] - int(0.5 * point[2])) + 3)),
                    color)
            self.set_img(self.field)
        except KeyError:
            pass

    def set_img(self, img):
        self.pic = ImageQt(img)
        self.pixmap = QPixmap.fromImage(self.pic)
        self.picOutput.setPixmap(self.pixmap)

    def draw_system(self):
        drawer = ImageDraw.Draw(self.field)
        point2 = (0, 0, 0)
        for point1 in self.newSystem[1:7]:
            point1 = point1.crds()
            drawer.line(((point1[0] - int(0.5 * point1[2]) + 350, 350 - (point1[1] - int(0.5 * point1[2]))),
                         (point2[0] - int(0.5 * point2[2]) + 350, 350 - (point2[1] - int(0.5 * point2[2])))),
                        "#000000", width=3)
        drawer.text((self.convert_system(self.newSystem[7].crds())), 'X', "#000000")
        drawer.text((self.convert_system(self.newSystem[8].crds())), 'Y', "#000000")
        drawer.text((self.convert_system(self.newSystem[9].crds())), 'Z', "#000000")

    def convert_system(self, point):
        return point[0] - int(0.5 * point[2]) + 350, 350 - (point[1] - int(0.5 * point[2]))

    def vector_lenth(self, p1, p2):
        return (((p2[0] - p1[0]) ** 2) + ((p2[1] - p1[1]) ** 2) + ((p2[2] - p1[2]) ** 2)) ** 0.5

    def vector(self, p1, p2):
        return [int(p2[0]) - int(p1[0]), int(p2[1]) - int(p1[1]), int(p2[2]) - int(p1[2])]

    def multiply(self, a, b):
        a = array(a)
        b = array(b)
        res = mult(a, b)
        resList = []
        try:
            for i in range(len(res)):
                resList.append([])
                for g in range(len(res[i])):
                    resList[i].append(res[i][g])
        except TypeError:
            for i in range(len(res)):
                resList.append(res[i])
            resList = resList[1:]

        return resList


if __name__ == '__main__':
    ex = QApplication(sys.argv)
    app = App()
    app.show()
    ex.exit(ex.exec())
