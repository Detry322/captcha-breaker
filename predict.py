from keras.models import load_model
from PIL import Image

import glob
import random
import numpy as np

LETTERS = 'abcdefghijklmnopqrstuvwxyz0123456789'
def onehot_to_string(vector):
  _1 = vector[0:36]
  # _2 = vector[36:72]
  # _3 = vector[72:108]
  # _4 = vector[108:144]
  return LETTERS[list(_1).index(max(_1))] #+ LETTERS[list(_2).index(max(_2))] + LETTERS[list(_3).index(max(_3))] + LETTERS[list(_4).index(max(_4))]

def load_models():
  return [load_model('index_{}_model.h5'.format(i)) for i in range(4)]

def predict(image, models):
  result = ''
  probability = 1.0
  probabilities = []
  image_np = np.array([np.array(image)])
  for model in models:
    predictions = model.predict_proba(image_np)[0]
    result += onehot_to_string(predictions)
    prob = max(predictions)
    probability *= prob
    probabilities.append(prob)
  return result, probability, tuple(probabilities)

def main():
  models = load_models()
  while True:
    test = Image.open(random.choice(glob.glob('tests/*.jpeg')))
    test.show()
    print predict(test, models)
    raw_input("Press enter to continue")

if __name__ == "__main__":
  main()
