from math import ceil
import random
from io import BytesIO

import urllib.request
from PIL import Image
from flask import render_template, jsonify,send_file


def create_mosaic(rows, cols, images, m_width, m_height, new_size):
    mosaic = Image.new("RGB", (m_width, m_height), color="white")
    i = 0 
    x_axis = 0
    y_axis = 0
    if rows != 1 and len(images) - rows * cols != 0:
        rows -= 1
    for row in range(rows):
        for col in range(cols):
            try:
                mosaic.paste(images[i],(x_axis, y_axis))
            except:
                return jsonify({'Error':'400','message':'Invalid image'}),400
            i += 1
            x_axis += new_size[0]
        y_axis += new_size[1]
        x_axis = 0
    if i == len(images) - 1:
        try:
            mosaic.paste(images[i], (int((m_width - new_size[0]) / 2), y_axis))
        except:
            return jsonify({'Error':'400','message':'Invalid image'}),400 
        
    x_axis = int(new_size[0] / 2)
    if i == len(images) - 2:
        for i in range(i, len(images)):
            try:
                mosaic.paste(images[i], (x_axis, y_axis))
            except:
                return jsonify({'Error':'400','message':'Invalid image'}),400 
            x_axis += new_size[0]
    img_io = BytesIO()
    mosaic.save(img_io, "JPEG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/jpeg")



def prepare(images, new_size, m_width, m_height,rows,cols):
    for i in range(len(images)):
        try:
            image = Image.open(
                urllib.request.urlopen(images[i]))  
        except:
            return jsonify({"Error": "400", "message": "Invalid image URL"}),400
        ratio = new_size[0] / image.width
        new_height = int(image.height * ratio)
        image = image.resize((new_size[0], new_height))
        images[i]=image
        if image.height < new_size[1]:
            ratio = new_size[1] / image.height
            new_width = int(image.width * ratio)
            if new_width >= new_size[0]:
                image = image.resize((new_width, new_size[1]))
            else:
                while new_width < new_size[0]:
                    ratio = new_size[1] + 100 / image.height
                    new_width = int(image.width * ratio)
                image = image.resize(new_width, new_size[1])
            images[i]=image

        if image.height != new_size[1]:
            space = image.height - new_size[1]
            if isinstance(space / 2, float):
                box = (
                    0,
                    space / 2 - 0.5,
                    image.width,
                    image.height - (space / 2 + 0.5),
                )
            else:
                box = (0, space / 2, image.width, image.height - (space / 2))
            cropped_img = image.crop(box)
            images[i] = cropped_img
        if image.width != new_size[0]:
            space = image.width - new_size[0]
            if isinstance(space / 2, float):
                box = (
                    ((space / 2) - 0.5),
                    0,
                    (image.width - (space / 2 + 0.5)),
                    image.height,
                )
            else:
                box = (space / 2, 0, image.width - (space / 2), image.height)
            cropped_img = image.crop(box)
            images[i] = cropped_img

    return create_mosaic(rows, cols, images, m_width, m_height, new_size)


def body(images, rozdzielczosc="2048x2048", losowo="0"):
    if losowo == "1":
        random.shuffle(images)
    try:
        m_width = int(rozdzielczosc.split("x")[0])
        m_height = int(rozdzielczosc.split("x")[1])
    except:
        return jsonify({"Error": "400", "message": "Invalid resolution values"}),400
    if m_width < m_height:
        if len(images) > 6:
            cols = 3
        else:
            cols = 2
    else:
        if len(images) > 4:
            cols = 3
        else:
            cols = 2

    rows = ceil(len(images) / cols)
    if len(images)==1:
        cols=rows=1
    new_size = m_width // cols, m_height // rows
    return prepare(images, new_size, m_width, m_height,rows,cols)