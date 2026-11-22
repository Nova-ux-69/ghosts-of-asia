# Ghosts of Asia - Episode 4: Manananggal (Philippines)
# True facts used (Wikipedia "Manananggal", USC Digital Folklore Archives):
#  - The name comes from the Tagalog word "tanggal", meaning "to remove" or "to separate".
#  - She leaves her lower body standing and flies at night on huge bat-like wings.
#  - Salt, crushed garlic or ash sprinkled on the standing lower half stops her from rejoining it;
#    if she cannot rejoin before sunrise, she perishes. Garlic and salt also keep her away.
PARTS = {
 "p1": [
  ("hook",   ["In the Philippines, if you hear big wings flapping over your roof at night...",
              "never, ever open the window."], 0.6, True),
  ("village",["Lito lived with his lola in a little house made of bamboo and palm leaves.",
              "Every night, she shut the shell windows before dark."], 0.4, False),
  ("warn",   ["Lola had one rule.", "Keep the windows shut. And keep a jar of salt by the door."], 0.4, False),
  ("open",   ["But that night was so hot.", "Lito slid the window open. Just a little."], 0.5, False),
  ("legs",   ["Down by the mango tree, something was standing very still.", "A woman's legs.", "Only her legs."], 0.8, True),
  ("cliff",  ["Then he heard it. Flap. Flap. Right above his head.", "So where was the rest of her?", "Part two is up now."], 2.2, True),
 ],
 "p2": [
  ("recap",  ["Last time, Lito saw a woman's legs standing all alone under the mango tree.",
              "Then something landed on his roof."], 0.4, False),
  ("face",   ["Slowly, a face rose up outside the window.", "Long wild hair. Huge bat wings.", "And nothing below her waist."], 1.0, True),
  ("lola",   ["Lola woke up and pushed the salt jar into his hands.", "Run to the legs, she said. Pour the salt. Now!"], 0.4, False),
  ("salt",   ["Lito ran to the mango tree and poured salt all over the legs.", "High in the sky, the creature screamed."], 0.6, False),
  ("dawn",   ["Now she could not join her body again.", "And when the sun came up... she was gone."], 0.6, False),
  ("explain",["This is the Manananggal, from Philippine folklore.",
              "Her name comes from tanggal, a Tagalog word meaning to separate.",
              "Salt, garlic or ash on her lower half traps her until sunrise."], 0.5, False),
  ("outro",  ["So, would you have opened the window?", "Tell me what your lola warned you about, in the comments."], 2.0, False),
 ],
}
# How the narrator should pronounce some words (captions keep the normal spelling).
SAY = {"Manananggal": "Mana-nang-gal", "tanggal": "tang-gal"}
