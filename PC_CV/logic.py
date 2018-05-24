import io
import os

from PIL import Image, ImageFilter

from .vision.google_api import Google_API
from .vision.azure_api import Azure_API
import uuid


def crop_and_transpose_face(img, rect):
    left = rect['left']
    top = rect['top']
    width = rect['width']
    height = rect['height']
    box = (left, top, left +width, top + height)
    ic = img.crop(box)
    ic = ic.transpose(Image.ROTATE_180)
    img.paste(ic, box)
    return img

def my_logic(imgbytes, az_face_client, g_annotation_client):
    """Give an image, some annotations and return what you need in the template
    """

    # Debug, write to disk
    filename = '/tmp/{}.png'.format(uuid.uuid1())
    print(filename)
    with open(filename, 'wb') as f:
        f.write(imgbytes)

    #TODO: your logic (modularize it to easy debug)

    imgpil = Image.open(io.BytesIO(imgbytes))  # Pillow library

    faces_raw = az_face_client.face_detect(filename)

    if (faces_raw and faces_raw[0]['faceRectangle']):
        topic = "face"
        rect = faces_raw[0]['faceRectangle']
        imgpil = crop_and_transpose_face(imgpil, rect)
        #ic = ic.filter(ImageFilter.BLUR)
    else:
        tags_raw = g_annotation_client.annotate(imgbytes)
        topic = tags_raw[0].description if tags_raw else "nothing"
        imgpil = imgpil.convert("L")  # image to grayscale

    # Pillow image to PNG bytearray
    imgbuffer = io.BytesIO()
    imgpil.save(imgbuffer, 'PNG')
    imgpng = imgbuffer.getvalue()

    os.remove(filename)
    return (imgpng, topic)
