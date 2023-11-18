import webcolors
import cv2
import numpy as np
import os
import time
import tensorflow as tf
from .mathmetica import ensemble


class BoundingUtils:
    def __init__(self) -> None:
        super(BoundingUtils, self).__init__()

    def CornerRectangle(self, images, x, min, max, color, thickness):
        x1, y1 = min
        x2, y2 = max

        #  Top left
        cv2.line(images, (int(x1), int(y1)),
                 (int(x1+x), int(y1)), color, thickness)
        cv2.line(images, (int(x1), int(y1)),
                 (int(x1), int(y1+x)), color, thickness)

        # Bottom Right
        cv2.line(images, (int(x2-x), int(y2)),
                 (int(x2), int(y2)), color, thickness)
        cv2.line(images, (int(x2), int(y2-x)),
                 (int(x2), int(y2)), color, thickness)

        # Top RIght
        cv2.line(images, (int(x2), int(y1)),
                 (int(x2), int(y1+x)), color, thickness)
        cv2.line(images, (int(x2), int(y1)),
                 (int(x2-x), int(y1)), color, thickness)

        # Bottom Left
        cv2.line(images, (int(x1), int(y2)),
                 (int(x1), int(y2-x)), color, thickness)
        cv2.line(images, (int(x1), int(y2)),
                 (int(x1+x), int(y2)), color, thickness)

    def text_draw(self, text, image, cords, font_scale=.3, font_thickness=1, font_color=(0, 255, 0), border_color=(0, 0, 0), neon_color=(0, 255, 255), fill_color=(0, 0, 0), border_thickness=2, font=cv2.FONT_HERSHEY_SIMPLEX, rect_length=50, overlap=5):
        x1, y1 = map(int, cords[0])
        x2, y2 = map(int, cords[1])

        font = font
        font_scale = font_scale

        font_thickness = font_thickness

        font_color = font_color
        lines = text.split('\n')

        max_line_width = max(cv2.getTextSize(
            line, font, font_scale, thickness=font_thickness)[0] for line in lines)
        max_line_width = max(max_line_width)
        text_height = len(lines) * cv2.getTextSize("T", font,
                                                   font_scale, thickness=font_thickness)[0][1]

        rect_x1 = x1
        rect_y1 = y2 + 10
        rect_x2 = x1 + max_line_width + 18
        rect_y2 = rect_y1 + text_height + rect_length
        reducer = 0

        if (x2 - x1) > 50.:
            rect_x1 = x1
            rect_y1 = y2
            rect_x2 = x1 + max_line_width
            rect_y2 = rect_y1 + text_height
            overlap = 0
            reducer = 2

        border_color = border_color
        border_thickness = border_thickness
        image_neon = image.copy()

        cv2.rectangle(image, (rect_x1, rect_y1), (rect_x2, rect_y2),
                      fill_color, thickness=cv2.FILLED)

        cv2.rectangle(image, (rect_x1, rect_y1), (rect_x2, rect_y2),
                      border_color, thickness=border_thickness)

        cv2.rectangle(image_neon, (rect_x1, rect_y1), (rect_x2,
                      rect_y2), neon_color, thickness=border_thickness)

        radius = border_thickness*2
        if radius % 2 == 0:
            radius += 1
        if radius <= 0:
            radius = 2

        image_neon = cv2.GaussianBlur(
            image_neon, (radius := radius+10, radius), 0)
        final_image = cv2.addWeighted(image, 1, image_neon, .7, 0)

        text_x = (rect_x1 + rect_x2) // 2
        text_y = rect_y1 + text_height // 2

        for line in lines:
            text_x_centered = text_x - max_line_width // 2
            line = " "*2 + line + " "*2
            text_y += cv2.getTextSize(line, font, font_scale,
                                      thickness=font_thickness)[0][1] + overlap
            cv2.putText(image, line, (text_x_centered, text_y-reducer),
                        font, font_scale, font_color, thickness=font_thickness)

        return final_image
    
    def draw_box(self, image: np.ndarray, models: dict, max_boxes: int, max_scores: float, text_show: bool = False, terms: int = 5, expand:int=0):
        """
        model keys:
            'detection': r""
            'gender-ethnicity': r""

        """

        images = np.copy(image)
        indexes = []
        score = []
        model = models["detection"](
            tf.convert_to_tensor(image)[tf.newaxis, ...])
        ethnic_gender = models["gender-ethnicity"]

        for i, j in enumerate(model["detection_scores"].numpy().tolist()[0]):
            if j > max_scores:
                indexes.append(i)
                score.append(j)

        idx = np.array(indexes)[:(max_boxes + 1)]
        scores = np.array(score)[:(max_boxes + 1)]*100
        height, width, _ = images.shape
        c = 1

        formats = []

        for i, j in zip(idx, scores):
            s0 = time.time()
            classes = model["detection_classes"].numpy().astype(np.int64)[
                0][i] - 1
            
            ymin, xmin, ymax, xmax = tuple(
                model["detection_boxes"].numpy()[0][i].tolist())
            x1 = xmin*width
            y1 = ymin*height
            x2 = xmax*width
            y2 = ymax*height

            CROPPED_IMAGED = tf.image.resize(images[int(y1)+expand:int(y2)+expand, int(
                x1)+expand:int(x2)+expand] / 255., (224, 224))[tf.newaxis, ...]
            ethnic_label = ["white", "black", "asian", "indian", "other"]

            try:
                ETHNICITY = [ethnic_label[ensemble(CROPPED_IMAGED, ethnic_gender, term=terms)[1][0]].capitalize(), ethnic_label[ensemble(CROPPED_IMAGED, ethnic_gender, term=terms)[1][1]].capitalize()]
            except IndexError:
                ETHNICITY = ethnic_label[ensemble(CROPPED_IMAGED, ethnic_gender, term=terms)[1][0]].capitalize()
            

            GENDER = {True: "Female", False: "Male"}[ensemble(CROPPED_IMAGED, ethnic_gender, term=terms)[0]]

            name, color = self.random_color()

            scaling_factor = 500
            thickness = 15

            if (x2 - x1) > 50.:
                scaling_factor = 256
                thickness = 20

            x_base = thickness
            x = min(height, width) / scaling_factor
            x = int(x_base * x)
            final = round(time.time() - s0, 2)
            label = f"No: {c} Person\ncolor: {name} \nrgba: {tuple(webcolors.name_to_rgb(name)) + (0.2,)}\nMask: {['yes', 'no', 'no'][classes]}\nScore: {round(j, 2)}%\nBody Part: Face\nTime: {final}s\nGender: {GENDER}\nEthnicity: {ETHNICITY}"
            formats.append(label)
            if text_show:
                self.text_draw(label, images, ((x1, y1), (x2, y2)),
                               0.35, font_color=(0, 255, 0))
            self.CornerRectangle(images, x, (x1, y1), (x2, y2), color, 2)
            c += 1

        return images, formats

    @staticmethod
    def img_to_array(x):
        if not os.path.exists(x):
            raise FileNotFoundError("Error: Due to Invalid Path")
        image = cv2.imread(x)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        return image

    def batch_estimator(self, image, expand_animations: bool = False):
        x = tf.io.read_file(image)
        x = tf.io.decode_image(x, 3, expand_animations=expand_animations)
        x = tf.image.resize(x, (224, 224))
        x = tf.cast(x, tf.float32)

        return x

    def random_color(self):
        named_colors = list(webcolors.CSS3_HEX_TO_NAMES.values())  
        random_color_name = np.random.choice(named_colors)
        rgb_code = webcolors.name_to_rgb(random_color_name)

        return random_color_name, (rgb_code[0], rgb_code[1], rgb_code[2])

    @staticmethod
    def str_to_list(x:str, sep:str="\n") -> list:
        result = list()
        for i in x:
            result.append([j for j in i.split(sep)])
        return result

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    detections = tf.saved_model.load(
        r"E:\keras\Projects\New folder\weights\models\detector\saved_model")
    ethnic = tf.saved_model.load(
        r"E:\keras\Projects\New folder\weights\models\gender-ethnic")
    utils = BoundingUtils()
    image = utils.img_to_array(
        r"E:\keras\Projects\New folder\waste\test\maksssksksss0.png")
    x = tf.convert_to_tensor(image)
    # x = x[tf.newaxis, ...]

    # detections = detections(x)

    image, text = utils.draw_box(image, {
                                 'detection': detections, 'gender-ethnicity': ethnic}, 5, .5, text_show=False, terms=20)
    # for i in text:
    #     print("-"*15)
    #     for j in i.split("\n"):
    #         print(j)
    #     print("\n")
    # print(utils.str_to_list(text))
    # plt.imshow(image)
    # plt.axis("off")
    # plt.show()
    y = []
    for i in text:
        y.append([j for j in i.split("\n")])
    print(y)