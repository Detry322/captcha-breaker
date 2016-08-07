import glob
import pytesseract
import random

from functools import wraps
from multiprocessing import Pool
from PIL import Image

SINGLE = False
SHOW = True
PRINT = False
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


def pixeldiff(p1, p2):
    return sum(abs(x - y) for x, y in zip(p1, p2))


@show_decorator()
def filter(image, average):
    pixels = image.load()
    avg_pixels = average.load()
    for p in iterator(image):
        if pixeldiff(pixels[p], avg_pixels[p]) < 35 and (max(pixels[p]) - min(pixels[p]) > 10 or sum(pixels[p])/3 > 200):
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
        if pixels[i, j] == 0 and count_around(old_pixels, i, j) < 2:
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
def conway_many(image, count):
    for i in range(count):
        conway_grow(image)


@show_decorator()
def overlay(image, original):
    image = image.convert('RGB')
    orignal_pixels = original.load()
    pixels = image.load()
    for p in iterator(image):
        if pixels[p] == (0, 0, 0):
            pixels[p] = orignal_pixels[p]
    return image


def vertical_scan(image, i):
    pixels = image.load()
    for j in range(image.size[1]):
        pixel = pixels[i, j]
        if isinstance(pixel, int):
            pixel = (pixel, pixel, pixel)
        if pixel != (255, 255, 255):
            return True
    return False


def split(image):
    result = []
    base = 0
    for i in range(image.size[0]):
        if vertical_scan(image, i):
            base = i - 3
            break
    seeking = True
    for i in range(image.size[0]):
        found_data = vertical_scan(image, i)
        if seeking and found_data:
            seeking = False
        elif not seeking and not found_data:
            seeking = True
            result.append(image.crop((base, 5, i + 2, image.size[1])))
            base = i
    return result


def filter_split(image):
    return [s for s in split(image) if len([p for p in iterator(s) if s.load()[p] != (255, 255, 255)]) > 10]


def attempt_detect(image, average):
    # original = image.copy()
    image = filter(image, average)
    image = black_and_white(image)
    image = conway_low(image)
    image = conway_many(image, 2)
    # image = overlay(image, original)
    pieces = filter_split(image)
    if len(pieces) != 4:
        return '????'
    string = ''
    for piece in pieces:
        try:
            solved = pytesseract.image_to_string(piece, config='-psm 10 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyz')
        except pytesseract.pytesseract.TesseractError:
            solved = None
        if not solved:
            solved = '?'
        string += solved
    return string


def detect(image_filename):
    image = Image.open(image_filename)
    answer = image_filename[6:-5]
    average = Image.open('average.png')
    solution = attempt_detect(image, average)
    return (answer, solution)


def score_single():
    answer, solution = detect(random.choice(glob.glob('tests/*.jpeg')))
    if PRINT:
        print "Solution: {}".format(solution)
        print "Answer:     {}".format(answer)
    return 0


def score_multiple():
    p = Pool(8)
    files = glob.glob('tests/*.jpeg')
    results = p.map(detect, files)
    p.close()

    correct, incorrect, skipped = 0, 0, 0
    cchar, tchar = 0, 0

    for answer, solution in results:
        if answer == solution:
            correct += 1
        elif '?' in solution:
            skipped += 1
        else:
            incorrect += 1
        cchar += sum(int(c1 == c2) for (c1, c2) in zip(answer, solution))
        tchar += sum(int(c != '?') for c in solution)

    if PRINT:
        print "Correct:   {}".format(correct)
        print "Incorrect: {}".format(incorrect)
        print "Skipped:   {}".format(skipped)
        print "Character accuracy: {}/{} {}".format(cchar, tchar, float(cchar)/tchar)
    score = skipped + 10*correct - 10*incorrect
    if PRINT:
        print "SCORE: {}".format(score)
    return score


def main():
    if SINGLE:
        score_single()
    else:
        print score_multiple()


if __name__ == "__main__":
    main()
