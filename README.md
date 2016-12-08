captcha-breaker
===============

This is a simple CAPTCHA breaker I wrote. It only breaks a specific type of captcha. Here is some proof that it works! :D

![LOOK IT WORKS :D](/yay_works.png?raw=true "Breaking Captchas")

Usage
-----

`python predict.py` to load the model and run some predictions. It requires that there are images in the `tests/` directory to load from.

Install Dependencies
--------------------

`brew install tesseract`
`pip install -r requirements.txt`

Then, run `./create_tests.sh` to download some captchas. You'll have to manually solve them. Solutions should be in the form: `<solution>.jpeg`. Example: `fv8w.jpeg`.

Other
-----

This is a work in progress. Released under the MIT License.
