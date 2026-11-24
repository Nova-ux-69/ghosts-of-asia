# Ghosts of Asia - Episode 10: the Chudail (India) - 2.1D survival version
# True facts used (well-known South Asian folklore; Wikipedia "Churel", searched 2026-11-24):
#  - The chudail (also churel / churail) is a female ghost of Indian and South Asian folklore.
#  - She is said to be the spirit of a woman who died in childbirth or during pregnancy, or who was treated
#    cruelly by her family (in-laws).
#  - Her feet are turned backwards. She may look like a beautiful woman, and lures young men on lonely roads,
#    calling them by name. Folk tales place her near peepal trees, crossroads and graveyards.
# Arjun, his Dadi, the village and the stepwell are fiction; the desert road is a generic Rajasthan setting.
PARTS = {
 "p1": [
  ("hook",    ["In India, if a woman on a dark road calls your name...", "look at her feet first."], 0.6, True),
  ("road",    ["Arjun is riding home across the Rajasthan desert.", "Midnight. Twelve kilometres to his village.",
               "And the fuel light is blinking."], 0.3, False),
  ("rule",    ["His Dadi always warned him.", "If a woman calls your name at night, look at her feet.",
               "If they point backwards, don't answer. Don't stop."], 0.3, False),
  ("tree",    ["At the old peepal tree, the scooter coughed... and died.", "And far away, the dogs began to howl."], 0.6, True),
  ("woman",   ["Then, the tinkle of anklets.", "Arjun? It's late. Walk with me.",
               "You can see her feet. Arjun can't."], 0.5, True),
  ("mistake", ["Arjun answered. Yes?", "The lantern went out.",
               "And her footprints in the sand... pointed the wrong way."], 0.5, False),
  ("cliff",   ["He ran into an old stepwell and hid in the dark.", "Anklets. On the steps above. Coming down.",
               "Stay hidden... or run?"], 1.6, True),
 ],
 "p2": [
  ("recap",   ["Arjun answered the woman with backward feet.", "Now she is coming down the stepwell."], 0.3, False),
  ("steps",   ["Arjun, she sang. Every step came closer.", "Then the anklets stopped. Right behind him."], 0.6, True),
  ("escape",  ["He remembered Dadi's last rule.", "Walk to the temple light, and never look back.",
               "He climbed out the far side and ran."], 0.4, False),
  ("bell",    ["Behind him, his name. Again and again.", "He rang the temple bell. And the voice stopped."], 0.4, False),
  ("twist",   ["At home, Dadi was waiting at the door.", "Arjun hugged her, shaking.", "Then he looked down. At her feet."], 1.0, True),
  ("explain", ["This is the Chudail, India's most feared ghost.",
               "Folk tales say she died in childbirth, or was treated cruelly.",
               "Her feet point backwards. She calls men by name on lonely roads."], 0.5, False),
  ("outro",   ["So, would YOU have answered?", "Indian friends, what did your Dadi warn you about? Which country next?"], 1.8, False),
 ],
}
SAY = {"Chudail": "Choo-rail", "Dadi": "Daadee", "Nani": "Naanee", "Arjun": "Arjoon", "peepal": "peepul", "Rajasthan": "Raajusthaan"}
