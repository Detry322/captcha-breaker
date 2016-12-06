import glob
import pytesseract
import random

from collections import defaultdict
from functools import wraps
from multiprocessing import Pool
from PIL import Image

SINGLE = False
SHOW = True
PRINT = True
SHOW_IMAGES = SINGLE and SHOW


DEFAULT_CONFIG = {
    'pixeldiff_similarity_cutoff': 35,        # ranges (20, 50)
    'min_max_colorful_cutoff': 10,            # ranges (5, 20)
    'filter_grayscale_cutoff': 200,           # ranges (170, 215)
    'black_and_white_grayscale_cutoff': 195,  # ranges (170, 215)
    'count_around_delete_cutoff': 2,          # ranges (2, 4)
    'count_around_add_cutoff': 4,             # ranges (2, 5)
    'conway_many_count': 2,                   # ranges (0, 5)
    'overlay': False                          # ranges (False, True)
}

AWESOME_CONFIG = {
    'conway_many_count': 4,
    'count_around_add_cutoff': 5,
    'min_max_colorful_cutoff': 10,
    'pixeldiff_similarity_cutoff': 20,
    'filter_grayscale_cutoff': 181,
    'overlay': True,
    'black_and_white_grayscale_cutoff': 203,
    'count_around_delete_cutoff': 3
}



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
def filter(image, average, config):
    pixels = image.load()
    avg_pixels = average.load()
    pixeldiff_cutoff = config['pixeldiff_similarity_cutoff']
    grayscale_cutoff = config['filter_grayscale_cutoff']
    minmax_cutoff = config['min_max_colorful_cutoff']
    for p in iterator(image):
        if pixeldiff(pixels[p], avg_pixels[p]) < pixeldiff_cutoff and (
            max(pixels[p]) - min(pixels[p]) > minmax_cutoff or sum(pixels[p])/3 > grayscale_cutoff):
            pixels[p] = (255, 255, 255)


@show_decorator()
def black_and_white(image, config):
    image = image.copy()
    pixels = image.load()
    cutoff = config['black_and_white_grayscale_cutoff']
    for p in iterator(image):
        pixels[p] = (0, 0, 0) if sum(pixels[p])/3 < cutoff else (255, 255, 255)
    return image.convert('L')


def count_around(pixels, i, j):
    tups = [(i+1, j+1), (i+1, j), (i+1, j-1), (i, j+1), (i, j-1), (i-1, j+1), (i-1, j), (i-1, j-1)]
    return sum(0 if pixels[tup] == 255 else 1 for tup in tups)


@show_decorator()
def conway_low(image, config):
    old_pixels = image.copy().load()
    pixels = image.load()
    for (i, j) in iterator(image):
        if i == 0 or j == 0 or i + 1 == image.size[0] or j + 1 == image.size[1]:
            continue
        cutoff = config['count_around_delete_cutoff']
        if pixels[i, j] == 0 and count_around(old_pixels, i, j) < cutoff:
            pixels[i, j] = 255


@show_decorator(show=False, copy=False)
def conway_grow(image, config):
    old_pixels = image.copy().load()
    pixels = image.load()
    for (i, j) in iterator(image):
        if i == 0 or j == 0 or i + 1 == image.size[0] or j + 1 == image.size[1]:
            continue
        cutoff = config['count_around_add_cutoff']
        if pixels[i, j] == 255 and count_around(old_pixels, i, j) > cutoff:
            pixels[i, j] = 0


@show_decorator()
def conway_many(image, config):
    for i in range(config['conway_many_count']):
        conway_grow(image, config)


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
    result.append(image.crop((base, 5, image.size[0], image.size[1])))
    return result


def filter_split(image):
    return [s for s in split(image) if len([p for p in iterator(s) if s.load()[p] != (255, 255, 255)]) > 10]


def solution_from_image(image):
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


def attempt_detect(image, average, config):
    original = image.copy()
    image = filter(image, average, config)
    image = black_and_white(image, config)
    image = conway_low(image, config)
    image = conway_many(image, config)
    if config['overlay']:
        image = overlay(image, original)
    return solution_from_image(image), filter_split(image)


def detect(args):
    image_filename, config = args
    image = Image.open(image_filename)
    answer = image_filename[6:-5]
    average = Image.open('average.png')
    solution, pieces = attempt_detect(image, average, config)
    # if len(pieces) == 4:
    #     import uuid, os
    #     for char, chari in zip(answer, pieces):
    #         path = 'characters/{}'.format(char)
    #         if not os.path.exists(path):
    #             os.mkdir(path)
    #         chari.save('{}/{}.jpeg'.format(path, uuid.uuid4().hex))
    return (answer, solution)


def score_single(config):
    args = (random.choice(glob.glob('tests/*.jpeg')), config)
    answer, solution = detect(args)
    if PRINT:
        print "Solution: {}".format(solution)
        print "Answer:   {}".format(answer)
    return 0


def score_multiple(config):
    p = Pool(8)
    files = glob.glob('tests/*.jpeg')
    args = zip(files, [config]*len(files))
    results = p.map(detect, args)
    p.close()

    correct, incorrect, skipped = 0, 0, 0
    cchar, tchar = 0, 0

    stuff = defaultdict(lambda: defaultdict(lambda: 0))

    for answer, solution in results:
        if answer == solution:
            correct += 1
        elif '?' in solution:
            skipped += 1
        else:
            incorrect += 1
        cchar += sum(int(c1 == c2) for (c1, c2) in zip(answer, solution))
        tchar += sum(int(c != '?') for c in solution)
        for a, s in zip(answer, solution):
            if s == '?':
                continue
            stuff[a][s] += 1

    if PRINT:
        print "Correct:   {}".format(correct)
        print "Incorrect: {}".format(incorrect)
        print "Skipped:   {}".format(skipped)
        print "Character accuracy: {}/{} {}".format(cchar, tchar, float(cchar)/tchar)
        for c in sorted('abcdefghijklmnopqrstuvwxyz1234567890', key=lambda c:float(stuff[c][c])/sum(stuff[c][a] for a in stuff[c].keys())):
            total = sum(stuff[c][a] for a in stuff[c].keys())
            correct = stuff[c][c]
            most_picked = max(stuff[c].keys(), key=lambda a: 0 if a == c else stuff[c][a])
            print "{}:\t{:.04f}\t{}/{}\t{}\t{}".format(c, float(correct)/total, correct, total, most_picked, stuff[c][most_picked])
    score = skipped + 10*correct - 10*incorrect
    if PRINT:
        print "SCORE: {}".format(score)
    return (score, correct, incorrect, len(files))


def main():
    if SINGLE:
        score_single(AWESOME_CONFIG)
    else:
        score_multiple(AWESOME_CONFIG)


if __name__ == "__main__":
    main()
