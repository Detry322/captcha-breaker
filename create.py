import random
from PIL import Image, ImageFont, ImageDraw
from StringIO import StringIO

def add_letter(background, location, angle, letter):
    GRAY = 185
    font = ImageFont.truetype("Verdana Bold.ttf", 23)
    text = letter
    width, height = font.getsize(text)
    image1 = background

    image2 = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(image2)
    draw2.text((0, 0), text=text, font=font, fill=(GRAY, GRAY, GRAY))

    image2 = image2.rotate(-angle, expand=1)

    px, py = location
    sx, sy = image2.size
    image1.paste(image2, (px, py, px + sx, py + sy), image2)


def random_location(base):
    return (base[0] + random.randint(-3, 4), base[1] + random.randint(-4, 4))


def random_image(base):
    LETTERS = 'abcdefghijklmnopqrstuvwxyz0123456789'
    background = base.copy()
    string = ''.join([random.choice(LETTERS) for i in range(4)])
    add_letter(background, random_location((17, 7)), random.randint(-20, 40), string[0])
    add_letter(background, random_location((37, 7)), random.randint(-20, 40), string[1])
    add_letter(background, random_location((57, 7)), random.randint(-20, 40), string[2])
    add_letter(background, random_location((77, 7)), random.randint(-20, 40), string[3])
    b = StringIO()
    background.save(b, "JPEG", quality=70)
    return Image.open(b), string


def main():
    background = Image.open('background.png')
    for i in range(3):
        random_image(background)[0].show()

if __name__ == "__main__":
    main()
