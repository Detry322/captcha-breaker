from create import random_image

import glob
import random
import numpy as np

from PIL import Image
from keras.models import Sequential, load_model
from keras.layers import Convolution2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense

background = Image.open('background.png')

LETTERS = 'abcdefghijklmnopqrstuvwxyz0123456789'

def string_to_onehot(string):
  arr0 = np.array([int(string[1] == c) for c in LETTERS])
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


def image_training_generator(per):
  while True:
    images_and_answers = [random_image(background) for i in range(per)]
    images, answers = zip(*images_and_answers)
    yield (np.array([np.array(image) for image in images]),
           np.array([string_to_onehot(answer) for answer in answers]))

from keras import backend as K


def reset_weights(model):
    session = K.get_session()
    for layer in model.layers:
        if isinstance(layer, Dense):
            old = layer.get_weights()
            layer.W.initializer.run(session=session)
            layer.b.initializer.run(session=session)
            print(np.array_equal(old, layer.get_weights())," after initializer run")
        else:
            print(layer, "not reinitialized")

def create_model():
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
  return model

def train(model):
  model.fit_generator(
        image_training_generator(1000),
        samples_per_epoch=100000,
        nb_epoch=20,
        validation_data=image_training_generator(1),
        nb_val_samples=100)

  print "Saving model..."
  model.save('model.h5')

  test = Image.open(random.choice(glob.glob('tests/*.jpeg')))
  test.show()
  result = model.predict(np.array([np.array(test)]))[0]
  print onehot_to_string(result)

def main():
  model = load_model('Definitely_good_model.h5')
  reset_weights(model)
  train(model)
  while True:
    test = Image.open(random.choice(glob.glob('tests/*.jpeg')))
    test.show()
    result = model.predict(np.array([np.array(test)]))[0]
    print onehot_to_string(result)
    raw_input("Press enter to continue")

if __name__ == '__main__':
  main()
