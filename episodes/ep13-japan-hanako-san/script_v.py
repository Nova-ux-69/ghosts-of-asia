# Ghosts of Asia - Episode 13: Hanako-san of the toilet (Japan) - 2.1D survival version
# True facts used (searched 2026-11-25; Wikipedia "Hanako-san", folklore.usc.edu, nippon.com):
#  - Hanako-san is a Japanese urban legend: the spirit of a young girl who haunts school bathrooms.
#  - She is said to live in the third stall of the girls' bathroom, often on the third floor.
#  - You knock three times and ask "Hanako-san, are you there?" - and a small voice answers "Yes, I'm here."
#  - She is usually described with a bob haircut and a red skirt.
#  - The dare is a classic "test of courage" (kimodameshi) game played by Japanese kids in summer.
# Yui, her friends and the old wooden school are fiction.
PARTS = {
 "p1": [
  ("hook",    ["In Japan, if you knock three times on the third toilet stall...", "someone answers."], 0.6, True),
  ("dare",    ["Yui's friends dared her: go into the old wooden school.", "Third floor bathroom. Take a photo of stall three.",
               "Three minutes."], 0.3, False),
  ("rule",    ["Every kid in Japan knows the rule.", "Knock three times: Hanako-san, are you there?",
               "If she answers... never open the door."], 0.3, False),
  ("hall",    ["On the third floor, the cicadas stopped.", "A small red skirt ran past the end of the hall.",
               "You saw it. Yui didn't."], 0.5, True),
  ("knock",   ["Yui knocked. One. Two. Three.", "Hanako-san... are you there?", "A tiny voice answered: Yes. I'm here."], 0.5, False),
  ("mistake", ["But Yui's hand was on the door.", "It creaked open. Empty.",
               "Then the mirror showed a little girl... right behind her."], 0.5, False),
  ("cliff",   ["The lights died. Yui hid under a desk.", "Small red shoes walked in. Tap. Tap. Tap.",
               "Stay hidden... or run?"], 1.6, True),
 ],
 "p2": [
  ("recap",   ["Yui opened Hanako's door.", "Now small red shoes are standing next to her desk."], 0.3, False),
  ("chalk",   ["A small voice whispered: Let's play.", "Then the chalk began to write on the blackboard... by itself."], 0.6, True),
  ("stairs",  ["Yui ran for the stairs. Third floor. Second floor...", "Third floor again.", "Her timer hit zero."], 0.4, False),
  ("escape",  ["Then she remembered the end of the rule.", "Say goodbye, and never look back.",
               "Sayonara, Hanako-san. She walked out... and never looked back."], 0.4, False),
  ("twist",   ["At home, Yui checked her dare photo.", "Stall three. Door open. Empty.",
               "But inside... a girl in a red skirt, waving at her."], 1.0, True),
  ("explain", ["This is Hanako-san, Japan's most famous school ghost.",
               "Kids say she lives in the third stall of the girls' bathroom, often on the third floor.",
               "Knock three times... and a small voice answers."], 0.5, False),
  ("outro",   ["Would YOU knock three times?", "Japanese friends, which school ghost scared you? Which country next?"], 1.8, False),
 ],
}
SAY = {"Hanako-san": "Hah-nah-ko sahn", "Yui": "Yoo-ee", "Sayonara": "Sah-yo-nah-rah"}
