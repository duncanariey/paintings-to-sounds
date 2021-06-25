from pyo import *
from PIL import Image
import requests

url = input("Enter image URL:")


def pixel_compare(pixel1, pixel2):
    return (abs(pixel1[0] - pixel2[0]) + abs(pixel1[1] - pixel2[1]) + abs(pixel1[2] - pixel2[2])) / 3


im_raw = Image.open(requests.get(str(url), stream=True).raw)
im = im_raw.convert('RGB')

red_total = 0
green_total = 0
blue_total = 0
busyness_total = 0
brightness_total = 0

for x in range(im.width - 2):
    for y in range(im.height - 2):
        pixelmain = im.getpixel((x + 1, y + 1))
        r, g, b = im.getpixel((x+1, y+1))
        red_total += r
        green_total += g
        blue_total += b
        pixel1 = im.getpixel((x + 2, y + 1))
        pixel2 = im.getpixel((x, y + 2))
        pixel3 = im.getpixel((x + 1, y + 2))
        pixel4 = im.getpixel((x + 2, y + 2))
        busyness_total += (pixel_compare(pixelmain, pixel1) + pixel_compare(pixelmain, pixel2) + pixel_compare(pixelmain, pixel3) + pixel_compare(pixelmain, pixel4)) / 4
    if x % 10 == 0:
        print(f"Analyzed row {str(x)} of {im.width-2}")


total_pixels = im.height * im.width
aspect_ratio = im.height / im.width
red_average = red_total / (im.width * im.height)
green_average = green_total / (im.width * im.height)
blue_average = blue_total / (im.width * im.height)
redness = (red_average - (green_average + blue_average)/2 + 255)*100/510
greenness = (green_average - (red_average + blue_average)/2 + 255)*100/510
blueness = (blue_average - (green_average + red_average)/2 + 255)*100/510
brightness = (red_average + green_average + blue_average)/3
busyness_average = busyness_total / ((im.width - 2) * (im.height - 2))

print(f"This image is {total_pixels} pixels large")
print(f"This image has an aspect ratio of {aspect_ratio}")
print(f"This image has a redness of {redness}, a value between 0 and 100")
print(f"This image has a greenness of {greenness}, a value between 0 and 100")
print(f"This image has a blueness of {blueness}, a value between 0 and 100")
print(f"This image has a brightness of {brightness}, a value between 0 and 255")
print(f"This image has a busyness rating of {busyness_average}, a measurement between 0 and 255")

s = Server().boot()

s.amp = 0.1


# NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin

if busyness_average > 80:
    busyness_average = 80

if total_pixels > 2000000:
    total_pixels = 2000000

frequency = round((((busyness_average - 0) * (600 - 100)) / 80) + 100)

harmonies = round((((total_pixels - 1) * (15 - 1)) / (2000000 - 1)) + 1)

feedback_max = (((redness - 0) * (1 - 0)) / (255 - 0)) + 0

feedback_freq = (((blueness - 0) * (1 - 0)) / (255 - 0)) + 0

chorus_max = (((greenness - 0) * (5 - 0)) / (255 - 0)) + 0

print(f"The frequency is {frequency}")
print(f"the number of harmonies is {harmonies - 1}")
print(f"The maximum feedback is {feedback_max}")
print(f"Feedback cycles every {1 / feedback_freq} seconds")
print(f"The chorus will peak at {chorus_max} out of 5")

feedback_sine = Sine(freq=feedback_freq).range(0, feedback_max)
chorus_sine = Sine(freq=0.5).range(0, chorus_max)
base_sound = SineLoop(freq=frequency, feedback=feedback_sine)
sound_with_chorus = Chorus(base_sound, depth=chorus_sine)

major_harmony = []
minor_harmony = []


def major_harmonizer(notes_set, source, intervals, channel):
    major_intervals = [1, 5, 8]
    for p in range(intervals):
        notes_set.append(Harmonizer(source, transpo=(major_intervals[(p % len(major_intervals))]) + (math.floor(p / len(major_intervals)) * 12)).out(channel))


def minor_harmonizer(notes_set, source, intervals, channel):
    minor_intervals = [1, 4, 8]
    for p in range(intervals):
        notes_set.append(Harmonizer(source, transpo=(minor_intervals[(p % len(minor_intervals))]) + (math.floor(p / len(minor_intervals)) * 12)).out(channel))

waveform = 0

if brightness > 127.5:
    print("This image is bright")
    major_harmonizer(major_harmony, sound_with_chorus, harmonies, 0)
    # for x in len(major_harmony):
    #     waveform += major_harmony[x]
else:
    print("This image is dark")
    minor_harmonizer(minor_harmony, sound_with_chorus, harmonies, 0)
    # for x in len(minor_harmony):
    #     waveform += minor_harmony[x]


Sp = Scope(major_harmony + minor_harmony)

s.gui(locals())
