from tkinter import *
from pygame import mixer
from random import random, choice
from math import sin, cos, acos, sqrt, pi, exp
from numpy import sign, array, dot, cross, linalg

CENTER_X, CENTER_Y = 400, 300
TEXT_X, TEXT_Y = 900, 400

class Lightning:
    def __init__(self, strength, conductivity, linearity, branch_tendency, x, y, slant=0, branch=True, loc=None, master=None):
        self.master = master
        self.path = [[x, y]]

        for i in range(1, 500):

            radius = 4 * random() + 0.2 * conductivity ** 2
            deviation = - 30 * (linearity - 2.5)
            angle = (((120 + deviation) * random() - (60 + 0.5 * deviation)) + slant)

            x_new, y_new = self.rotate_segment(self.path[i - 1][0], self.path[i - 1][1], radius, angle)
            self.path.append([x_new, y_new])

            if branch:
                branch_slant = choice([-30, -20, 20, 30])
                if strength >= 1:
                    if (500 + 150 * (2.5 - branch_tendency)) * random() < len(self.path):
                        Lightning(strength - strength / (5 + branch_tendency),
                                  conductivity, linearity, branch_tendency,
                                  x_new, y_new, slant - branch_slant, True, loc, self.master)
                        Lightning(strength - strength / 2,
                                  conductivity, linearity, branch_tendency,
                                  x_new, y_new, slant + branch_slant, True, loc, self.master)
                        break
                    elif random() < 0.025:
                        strength -= strength / 5
                elif 1000 * random() < 4 * len(self.path):
                    break

            if not branch:
                distance = sqrt((x_new - CENTER_X) ** 2 + (y_new - CENTER_Y) ** 2)
                if distance > loc.distance:
                    angle = sign(cross([x_new - CENTER_X, y_new - CENTER_Y], [loc.x - CENTER_X, loc.y - CENTER_Y])) * get_angle(x_new, y_new, loc.x, loc.y)
                    self.path = [self.rotate_line(point, angle) for point in self.path]
                    break

            if y_new < 0 or y_new > 700 or x_new < 0 or x_new > 1400:
                break

        self.alpha = abs(-(exp(-strength) - 1))
        self.bolt = self.master.create_line(self.path, fill=transparency(self.master, self.alpha), width=strength, smooth=True, tags=("lightning", "main"))
        self.master.tag_raise(self.bolt)
        self.master.tag_lower(self.bolt, "light")
        self.master.after(50, lambda: self.fade(self.alpha - 0.3 / (strength + 1)))

    def fade(self, alpha):
        if alpha <= 0.1:
            self.master.delete(self.bolt)
            return
        self.master.itemconfig(self.bolt, fill=transparency(self.master, alpha))
        self.master.after(75, lambda: self.fade(alpha))
        alpha = 0.75 * alpha

    def rotate_segment(self, x, y, radius, angle):
        x_prime = - radius * sin(angle * pi / 180)
        y_prime = radius * cos(angle * pi / 180)
        return x + x_prime, y + y_prime

    def rotate_line(self, point, angle):
        x_new = (point[0] - CENTER_X) * cos(angle * pi / CENTER_Y) - (point[1] - CENTER_Y) * sin(angle * pi / 180)
        y_new = (point[0] - CENTER_X) * sin(angle * pi / CENTER_Y) + (point[1] - CENTER_Y) * cos(angle * pi / 180)
        return [x_new + CENTER_X, y_new + CENTER_Y]


class Scale:
    def __init__(self, pos, value, master=None):
        self.master = master
        self.pos = pos
        self.value = value
        text_dictionary = ["Branch tendency", "Conductivity", "Linearity", "Frequency", "Intensity"]
        self.title = self.master.create_text(TEXT_X + 30, TEXT_Y - 20 - 40 * self.pos, text=text_dictionary[self.pos], fill="white", font=('Corbel', 12, 'bold'), anchor="w", tags="words")

        self.up_button = self.master.create_text(TEXT_X + 220, TEXT_Y + 4 - 40 * self.pos, text="+", fill="white", font=("Arial", 20, "bold"), tags=("button", "words"))
        self.down_button = self.master.create_text(TEXT_X - 20, TEXT_Y - 9 - 40 * self.pos, text="_", fill="white", font=("Arial", 20, "bold"), tags=("button", "words"))
        self.master.tag_bind(self.up_button, "<ButtonPress-1>", lambda event: self.adjust(0.5))
        self.master.tag_bind(self.down_button, "<ButtonPress-1>", lambda event: self.adjust(-0.5))

        self.background = self.master.create_rectangle((TEXT_X, TEXT_Y - 40 * self.pos), (TEXT_X + 200, TEXT_Y + 5 - 40 * self.pos), fill="gray25", width=0, tags="words")
        self.foreground = self.master.create_rectangle((TEXT_X, TEXT_Y - 40 * self.pos), (TEXT_X + self.value * 40, TEXT_Y + 5 - 40 * self.pos), fill="white", width=0, tags="words")

    def adjust(self, change):
        self.value += change
        if self.value > 5 or self.value < 0:
            self.value -= change
            return
        self.master.delete(self.foreground)
        self.foreground = self.master.create_rectangle((TEXT_X, TEXT_Y - 40 * self.pos), (TEXT_X + self.value * 40, TEXT_Y + 5 - 40 * self.pos), fill="gray100", width=0, tags="words")


class Position:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.angle = 0
        self.distance = 0
        self.status = False
        self.arcing = False


def transparency(c, alpha):
    background = int(c['background'].strip('gray')) / 100
    opacity = int((alpha + (1 - alpha) * background) * 100)
    opacity_string = 'gray' + str(opacity)
    return opacity_string


def locate(event, loc):
    x, y = event.x, event.y
    loc.x, loc.y = x, y
    loc.distance = sqrt((x - CENTER_X) ** 2 + (y - CENTER_Y) ** 2)
    if loc.x < CENTER_X:
        loc.angle = get_angle(u1=x, u2=y)
    else:
        loc.angle = 360 - get_angle(u1=x, u2=y)


def get_angle(u1, u2, v1=CENTER_X, v2=CENTER_Y + 1):
    arr1 = array([u1 - CENTER_X, CENTER_Y - u2])
    arr2 = array([v1 - CENTER_X, CENTER_Y - v2])
    theta = acos(dot(arr1, arr2) / (linalg.norm(arr1) * linalg.norm(arr2))) * 180 / pi
    return theta


def main():

    def sparks(loc):

        intensity = scale_dictionary['intensity'].value
        frequency = scale_dictionary['frequency'].value
        conductivity = scale_dictionary['conductivity'].value
        linearity = scale_dictionary['linearity'].value
        branch_tendency = scale_dictionary['branch_tendency'].value

        sound.set_volume(0.06 + 0.02 * (intensity - 2.5))
        brightness = int(2 * intensity)
        light = canvas.create_image(CENTER_X + 2, CENTER_Y, image=light_list[brightness], tags="light")

        if loc.status and loc.arcing:
            intensity *= loc.distance / CENTER_X
            frequency *= loc.distance / CENTER_X
            conductivity *= 0.75 * loc.distance / CENTER_X

        if intensity != 0:
            Lightning(strength=intensity,
                      conductivity=conductivity,
                      linearity=linearity,
                      branch_tendency=branch_tendency,
                      x=CENTER_X, y=CENTER_Y,
                      slant=int(300 * random() + 30),
                      branch=True,
                      loc=loc,
                      master=canvas)

        if loc.status:
            if loc.arcing:
                cursor_light = canvas.create_image(loc.x, loc.y, image=light_list[int(brightness / 2)], tags="light")
            else:
                cursor_light = canvas.create_image(loc.x, loc.y, image=light_list[0], tags="light")
            canvas.tag_lower(cursor_light, "button")
            root.after(int(500 / exp(2 * frequency / 3)),
                       lambda: (sparks(loc), canvas.delete(light, cursor_light)))
        else:
            root.after(int(500 / exp(2 * frequency / 3)),
                       lambda: (sparks(loc), canvas.delete(light)))

    def arc(loc):
        arcing_interval = 600
        if loc.status:
            intensity = scale_dictionary['intensity'].value
            frequency = scale_dictionary['frequency'].value
            conductivity = scale_dictionary['conductivity'].value
            linearity = scale_dictionary['linearity'].value
            branch_tendency = scale_dictionary['branch_tendency'].value

            intensity = intensity * (1 + ((300 - loc.distance + 30 * conductivity) / 300))
            arcing_interval = int(max(150, (loc.distance ** 2) / ((intensity ** 2 + 1) * (conductivity ** 2 + 1) * frequency + 1)))
            arcing_coefficient = 100 * frequency / loc.distance
            arc_no = min(2 + int(random() * arcing_coefficient), 7)

            if intensity != 0 and arcing_interval < 600:
                loc.arcing = True
                for i in range(1, arc_no):
                    Lightning(strength=intensity / i,
                              conductivity=conductivity,
                              linearity=linearity,
                              branch_tendency=branch_tendency,
                              x=CENTER_X, y=CENTER_Y,
                              slant=loc.angle,
                              branch=False,
                              loc=loc,
                              master=canvas)
            else:
                loc.arcing = False
        root.after(min(500, arcing_interval), lambda: arc(loc))

    def switch(event):
        if loc.x < 850 or not 200 < loc.y < 500:
            loc.status = not loc.status
            loc.arcing = loc.status

    root = Tk()
    base = Frame(root)
    canvas = Canvas(base)

    root.title("Interactive Tesla Coil Simulator")
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry('+%d+%d' % (sw / 2 - 660, sh / 2 - 375))
    base.pack(fill="none", expand=True)
    canvas.configure(bg="gray0", width=1300, height=650)
    canvas.pack()

    instructions = canvas.create_text(TEXT_X + 90, TEXT_Y + 50, text="Click near the tesla coil to\n make it arc to the cursor.",
                                      fill="white", font=('Corbel', 12, 'bold'), tags="words")
    light_list = [PhotoImage(file="Files/" + "light" + str(i) + ".png") for i in range(1, 12)]
    rod_image = PhotoImage(file="Files/source.png")
    rod = canvas.create_image(CENTER_X + 5, CENTER_Y + 130, image=rod_image, tags="rod")

    mixer.init()
    sound = mixer.Sound("Files/sound.wav")
    sound.set_volume(0.05)
    sound.play(-1)

    loc = Position()
    canvas.bind("<Motion>", lambda event: locate(event, loc))
    canvas.bind("<Button-1>", switch)
    scale_dictionary = {'branch_tendency': Scale(0, 2.5, canvas),
                        'conductivity': Scale(1, 2.5, canvas),
                        'linearity': Scale(2, 2.5, canvas),
                        'frequency': Scale(3, 2.5, canvas),
                        'intensity': Scale(4, 2.5, canvas)}

    sparks(loc)
    arc(loc)
    root.mainloop()


if __name__ == '__main__':
    main()
