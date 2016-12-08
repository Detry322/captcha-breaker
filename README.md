captcha-breaker
===============

This is a simple CAPTCHA breaker I wrote. It only breaks a specific type of captcha. Here is some proof that it works! :D

![LOOK IT WORKS :D](/yay_works.png?raw=true "Breaking Captchas")

Usage
-----

`python predict.py` to load the model and run some predictions. It requires that there are images in the `tests/` directory to load from. You can use the included script to download images.

Method
------

I tried many different things over the course of this to get it to work. My first attempts were more methodical in operation. I tried some custom image transformations, ultimately passing it into the tesseract library. This gave limited success, but it wasn't great.

The current model is actually 4 single-character models trained to recognize a specific character position. Each single-character model is a an 8-layer Convolutional Neural Net, with 3 Convolutional layers, each with 32 filters (except the last, which has 64).

I trained the model on 100000 captcha images. After downloading and manually solving 200 samples, I realized it would be infeasible to get the data I need. So, to compensate, I used the custom image transformations I had developed earlier to extract the background image from this captcha. From there, I used PIL to auto-generate captcha images, which were close enough to be used as training data. If you can generate your own data, you can train to arbirary accuracy.

Install Dependencies
--------------------

`brew install tesseract`
`pip install -r requirements.txt`

Then, run `./create_tests.sh` to download some captchas. You'll have to manually solve them. Solutions should be in the form: `<solution>.jpeg`. Example: `fv8w.jpeg`.

Other
-----

This is a work in progress. Released under the MIT License.
