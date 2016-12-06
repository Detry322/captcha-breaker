import glob
import random

from collections import defaultdict, Counter
from functools import wraps
from multiprocessing import Pool
from PIL import Image

SINGLE = True
SHOW = True
PRINT = True
SHOW_IMAGES = SINGLE and SHOW

def show_decorator(show=True, copy=True):
    def wrap(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            image = args[0]
            if copy:
                image = args[0].copy()
                args = (image, ) + args[1:]
            result = function(*args, **kwargs) or image
            if SHOW_IMAGES and show:
                result.show()
            return result
        return wrapper
    return wrap


def iterator(image):
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            yield (i, j)


@show_decorator()
def highlight_difference(image1, image2, cutoff):
    image1 = image1.copy()
    i1px = image1.load()
    i2px = image2.load()
    for t in iterator(image1):
        if abs(i1px[t] - i2px[t]) > cutoff:
            i1px[t] = 255
        else:
            i1px[t] = 0


def pixelavg(images):
    image = images[0].copy()
    pixels = image.load()
    others_pixels = [i.load() for i in images]
    for p in iterator(image):
        r, g, b = (0, 0, 0)
        for pxls in others_pixels:
            r1, g1, b1 = pxls[p]
            r += r1
            g += g1
            b += b1
        pixels[p] = (r/len(images), g/len(images), b/len(images))
    return image

def pixelmode(images, level):
    image = images[0].copy()
    pixels = image.load()
    others_pixels = [i.load() for i in images]
    for p in iterator(image):
        pixels[p] = Counter([pxls[p] for pxls in others_pixels]).most_common(level)[-1][0]
    return image

def pixeldiff(p1, p2):
    return sum(abs(x - y) for x, y in zip(p1, p2))

@show_decorator()
def highlight_pixeldiff(image, average):
    pixels = image.load()
    avg_pixels = average.load()
    for p in iterator(image):
        pixels[p] = (pixeldiff(pixels[p], avg_pixels[p]*3),)*3

@show_decorator()
def filter(image, average):
    pixels = image.load()
    avg_pixels = average.load()
    for p in iterator(image):
        if pixeldiff(pixels[p], avg_pixels[p]) < 35 and (
            max(pixels[p]) - min(pixels[p]) > 10 or sum(pixels[p])/3 > 200):
            pixels[p] = (255, 255, 255)


@show_decorator()
def black_and_white(image):
    image = image.copy()
    pixels = image.load()
    for p in iterator(image):
        pixels[p] = (0, 0, 0) if sum(pixels[p])/3 < 195 else (255, 255, 255)
    return image.convert('L')


def count_around(pixels, i, j):
    tups = [(i+1, j+1), (i+1, j), (i+1, j-1), (i, j+1), (i, j-1), (i-1, j+1), (i-1, j), (i-1, j-1)]
    return sum(0 if pixels[tup] == 255 else 1 for tup in tups)


@show_decorator()
def conway_low(image):
    old_pixels = image.copy().load()
    pixels = image.load()
    for (i, j) in iterator(image):
        if i == 0 or j == 0 or i + 1 == image.size[0] or j + 1 == image.size[1]:
            continue
        if pixels[i, j] == 0 and count_around(old_pixels, i, j) < 3:
            pixels[i, j] = 255


@show_decorator(show=False, copy=False)
def conway_grow(image):
    old_pixels = image.copy().load()
    pixels = image.load()
    for (i, j) in iterator(image):
        if i == 0 or j == 0 or i + 1 == image.size[0] or j + 1 == image.size[1]:
            continue
        if pixels[i, j] == 255 and count_around(old_pixels, i, j) > 4:
            pixels[i, j] = 0


@show_decorator()
def conway_many(image):
    for i in range(3):
        conway_grow(image)


@show_decorator()
def highlight_is_gray(image):
    pixels = image.load()
    for p in iterator(image):
        pixels[p] = (max(abs(max(pixels[p]) - sum(pixels[p])/3),
                        abs(min(pixels[p]) - sum(pixels[p])/3)) * 3,)*3

def replace_over(image, replacer):
    replacer_pix = replacer.load()
    pixels = image.load()
    for p in iterator(image):
        print pixels[p]
        if max(pixels[p][:3]) == 0:
            pixels[p] = replacer_pix[p]


def subtract(image, background):
    pixels = image.load()
    background_p = background.load()
    for p in iterator(image):
        difference = sum(abs(a - b) for a, b in zip(pixels[p], background_p[p]))
        if difference > 60:
            pixels[p] = (0, 0, 0)
        else:
            pixels[p] = (255, 255, 255)

def main():
    # pixelmode([Image.open(i) for i in glob.glob('tests/*.jpeg')], 2).show()
    background = Image.open('background.png')
    test = Image.open(random.choice(glob.glob('tests/*.jpeg')))
    subtract(test, background)
    test.show()
    # image = Image.open(random.choice(glob.glob('tests/*.jpeg')))
    # highlight_pixeldiff(image, avg)
    # highlight_is_gray(image)

if __name__ == "__main__":
    main()
