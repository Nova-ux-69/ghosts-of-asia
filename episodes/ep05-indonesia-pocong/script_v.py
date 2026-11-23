# Ghosts of Asia - Episode 5: Pocong (Indonesia)
# True facts used (Wikipedia "Pocong"):
#  - "Pocong" comes from Javanese and means "wrapped in a shroud". In Malaysia it is called Hantu Bungkus.
#  - In a Muslim burial the shroud (kain kafan) is tied over the head, at the neck and under the feet.
#    Folk belief says the knots must be undone; otherwise the body rises as a Pocong.
#  - The Pocong hops because the knot under its feet stops it from walking.
#  - Extra village detail: a yellow flag (bendera kuning) at the lane entrance tells neighbours someone has died.
PARTS = {
 "p1": [
  ("hook",    ["In Indonesia, if you hear a soft thump... thump... behind you at night,",
               "it is not a rabbit. And it is not a person."], 0.6, True),
  ("village", ["Bayu lived in a village in Java, between the rice fields and the old graveyard.",
               "That afternoon, the whole village buried old Pak Harjo."], 0.4, False),
  ("warn",    ["His grandmother had one rule.",
               "After a funeral, never take the shortcut through the graveyard at night."], 0.4, False),
  ("shortcut",["But it was late, and the rain was coming.",
               "So Bayu ran into the graveyard, between the frangipani trees."], 0.4, False),
  ("thump",   ["Then he heard it behind him.", "Thump. Thump. Thump.",
               "Something white was hopping between the graves."], 0.8, True),
  ("cliff",   ["It came closer... and stopped right behind him.", "Then it whispered his name.",
               "Part two is up now."], 2.2, True),
 ],
 "p2": [
  ("recap",   ["Last time, Bayu took the graveyard shortcut after a funeral.",
               "And something white hopped up right behind him."], 0.4, False),
  ("turn",    ["Slowly, Bayu turned around.", "Wrapped in white cloth. Tied at the feet, and at the head.",
               "Two pale eyes stared out of the shroud."], 1.0, True),
  ("bow",     ["But it did not attack.", "It bowed its head... and showed him the knot on top."], 0.6, False),
  ("untie",   ["With shaking hands, Bayu pulled the knot loose.",
               "The white cloth sighed... and fell empty to the ground."], 0.8, False),
  ("morning", ["The next morning, the gravedigger said it quietly.", "He had forgotten to untie the knots."], 0.6, False),
  ("explain", ["This is the Pocong, from Indonesian folklore.",
               "Its name is Javanese for wrapped in a shroud.",
               "Folk tales say if the knots are not untied, the body rises. And it hops, because its feet are tied."], 0.5, False),
  ("outro",   ["So, would you untie the knot... or run?", "And which country next? Tell me in the comments."], 2.0, False),
 ],
}
# How the narrator should pronounce some words (captions keep the normal spelling).
SAY = {"Pocong": "Po-chong", "Pak Harjo": "Pahk Har-jo", "Bayu": "Bah-yoo"}
