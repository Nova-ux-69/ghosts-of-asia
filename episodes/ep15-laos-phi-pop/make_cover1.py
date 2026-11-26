"""Part 1 cover: Grandma's room, Noy at the door, the Phi Pop's long-necked shadow reaching over her with red eyes."""
import os, sys
os.environ["NO_UI"] = "1"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "toolkit"))
import numpy as np
import scenes_ep15 as S
from art_ep15 import room, noy, finish, VIG_H
import thumbnail as TH
R = room()
m, e = S.shadow(1.0, 1.0, 0.8, 0.8)
SX, SY = 760, 1700
def girl(img, t_):
    im, fx, fy = noy(0.0, back=True, scale=1.05)
    return S.put_sprite(img, im, 470 + 100, 1900, fx, fy)
img = R.frame(1.0, 0, lamp=1.0, shadow=(m, SX, SY - 280, 1.0), door_light=1.0, door_fig=1.0, front=[girl])
S.shadow_eyes(img, m, e, SX, SY - 280, 0, 1.0, 1.0, 0.95)
a = finish(img, 1.0, VIG_H, push=1.0)
TH.make(np.clip(a, 0, 255).astype(np.uint8), "LAOS", "PART 1", "Don't open the *door*", "ep15_part1_thumb_raw.jpg", 260)
