from create import random_image

import glob
import random
import numpy as np

from PIL import Image
from keras.models import Sequential
from keras.layers import Convolution2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense

background = Image.open('background.png')

LETTERS = 'abcdefghijklmnopqrstuvwxyz0123456789'

def string_to_onehot(string):
  arr0 = np.array([int(string[0] == c) for c in LETTERS])
  # arr1 = np.array([int(string[1] == c) for c in LETTERS])
  # arr2 = np.array([int(string[2] == c) for c in LETTERS])
  # arr3 = np.array([int(string[3] == c) for c in LETTERS])
  return arr0 #np.append(arr0, [arr1, arr2, arr3])


def onehot_to_string(vector):
  _1 = vector[0:36]
  # _2 = vector[36:72]
  # _3 = vector[72:108]
  # _4 = vector[108:144]
  return LETTERS[list(_1).index(max(_1))] #+ LETTERS[list(_2).index(max(_2))] + LETTERS[list(_3).index(max(_3))] + LETTERS[list(_4).index(max(_4))]


def image_training_generator():
  while True:
    GENERATE_PER = 1000
    images_and_answers = [random_image(background) for i in range(GENERATE_PER)]
    images, answers = zip(*images_and_answers)
    yield (np.array([np.array(image) for image in images]),
           np.array([string_to_onehot(answer) for answer in answers]))


def main():
  print "Creating Model..."
  model = Sequential()
  model.add(Convolution2D(32, 3, 3, input_shape=(background.size[::-1] + (3,))))
  model.add(Activation('relu'))
  model.add(MaxPooling2D(pool_size=(2, 2), dim_ordering="tf"))

  model.add(Convolution2D(32, 3, 3))
  model.add(Activation('relu'))
  model.add(MaxPooling2D(pool_size=(2, 2), dim_ordering="tf"))

  model.add(Convolution2D(64, 3, 3))
  model.add(Activation('relu'))
  model.add(MaxPooling2D(pool_size=(2, 2), dim_ordering="tf"))

  model.add(Flatten())
  model.add(Dense(64))
  model.add(Activation('relu'))
  model.add(Dropout(0.5))
  model.add(Dense(36))
  model.add(Activation('softmax'))

  print "Compiling Model..."
  model.compile(loss='categorical_crossentropy',
                optimizer='rmsprop',
                metrics=['accuracy'])

  model.fit_generator(
        image_training_generator(),
        samples_per_epoch=10000,
        nb_epoch=5,
        validation_data=image_training_generator(),
        nb_val_samples=100)

  test = Image.open(random.choice(glob.glob('tests/*.jpeg')))
  test.show()
  result = model.predict(np.array([np.array(test)]))[0]
  print onehot_to_string(result)

if __name__ == '__main__':
  main()
