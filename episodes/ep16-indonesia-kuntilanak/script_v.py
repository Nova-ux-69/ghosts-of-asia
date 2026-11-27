# Ghosts of Asia - Episode 16: Kuntilanak (Indonesia) - 2.1D survival version
# True facts used (read 2026-11-27):
#  - Wikipedia "Kuntilanak": usually shown as a long-haired woman in white; said to be the spirit of a woman who died
#    while pregnant / in childbirth; she announces herself with a baby's cry or a woman's laugh - "if the sounds are
#    quiet, she is nearby, but if they are loud, she is far away"; the smell of plumeria (frangipani) is a sign she is
#    near; linked to banana and banyan trees (also JSTOR Daily).
#  - Pontianak city (West Kalimantan, on the Kapuas River) is named after her. Legend: Sultan Syarif Abdurrahman
#    Alkadrie founded it in 1771 and drove the ghosts away with cannon fire (Wikipedia, JSTOR Daily "The Indonesian
#    frontier town named for a jungle vampire", detik.com, mothership.sg); locals still fire big wooden/bamboo cannons
#    at festival time.
# Putri, Grandma and the kampung are fiction. The night-watch drum (kentongan at the pos ronda) is a real Indonesian
# neighbourhood custom, used here as a story detail ("she hates loud bangs" echoes the cannon legend).
# Different from ep01 (Malaysia / Pontianak, banana trees): city riverfront, boardwalk kampung on stilts, the laugh rule.
PARTS = {
 "p1": [
  ("hook",    ["In Indonesia, if you hear a woman laughing far away... you're safe.",
               "If her laugh is soft... she's right next to you."], 0.6, True),
  ("setup",   ["Pontianak, on the Kapuas River. Midnight.", "Putri is closing her family's noodle stall.",
               "Home is three hundred metres away, along the old boardwalk."], 0.3, False),
  ("rule",    ["Grandma's rules for the walk home.", "If you smell frangipani, never look up.",
               "If her laugh is loud, she's far. If it's soft... keep walking."], 0.3, False),
  ("smell",   ["Halfway home... a sweet smell.", "Frangipani. But no frangipani grows here.",
               "White petals were falling from the banyan tree."], 0.4, False),
  ("laugh",   ["Then a woman laughed. Loud. Far away.", "Putri breathed out.",
               "Then the laugh came again... soft."], 0.5, True),
  ("mistake", ["Under the banyan, a baby was crying.", "Putri stopped... and looked up."], 0.4, True),
  ("cliff",   ["She ran, and hid under a house on stilts.", "Something white dropped down in front of her.",
               "Stay hidden... or run?"], 1.6, True),
 ],
 "p2": [
  ("recap",   ["Putri is hiding under a house on stilts.", "And something in white is hanging right above her."], 0.3, False),
  ("hair",    ["Long black hair slid over her shoulder.", "The laugh was so soft... it was inside her ear."], 0.6, True),
  ("bang",    ["Grandma's last rule: she hates loud bangs.",
               "Putri ran to the night-watch drum and hit it. Again. And again."], 0.3, False),
  ("escape",  ["Lights came on. Doors opened.", "The laugh flew higher... and further away.",
               "Putri ran all the way home."], 0.3, False),
  ("twist",   ["She locked the door. Grandma was asleep.", "On her pillow... a fresh frangipani flower.",
               "And very softly... someone laughed."], 1.0, True),
  ("explain", ["This is the Kuntilanak of Indonesian folklore.",
               "A woman in white: the spirit of a woman who died while pregnant.",
               "Legend says Pontianak's founder drove her away with cannons. The city still has her name."], 0.5, False),
  ("outro",   ["Would YOU have looked up?", "Indonesian friends, what did Grandma say about her laugh?"], 1.0, False),
 ],
}
SAY = {"Kuntilanak": "Koon-tee-lah-nak", "Pontianak": "Pon-tee-ah-nak", "Putri": "Poo-tree", "Kapuas": "Kah-poo-ahs"}
