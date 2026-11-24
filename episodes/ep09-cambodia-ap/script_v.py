# Ghosts of Asia - Episode 9: the Ap (Cambodia) - 2.1D survival version
# True facts used (Wikipedia "Krasue", section on Cambodia, read 2026-11-24):
#  - In Cambodia this ghost is called the Ahp / Ap (Khmer: អាប); in Thailand it is the Krasue.
#  - Cambodian folklore: she is a woman who is half spirit and half mortal. By day she looks like a normal person;
#    at night her head leaves the body and flies off to hunt, with a glowing light.
#  - Her weaknesses are thorns and guard dogs: relatives put thorny branches around the house to protect pregnant women.
#  - Laundry left outside at night is said to be found soiled, because she wipes her mouth on it, so villagers bring it in.
#  - She must get back to her body before daybreak (Thai Krasue lore, same page).
# The village near Siem Reap is a generic setting. Dara, Aunt Srey and the neighbour are fiction.
PARTS = {
 "p1": [
  ("hook",    ["In Cambodia, never leave your laundry outside at night.", "Something comes to wipe its mouth on it."], 0.6, True),
  ("village", ["Dara is visiting her aunt near Siem Reap.", "Her aunt is about to give birth. Tonight, they are alone.",
               "Sunrise: five forty."], 0.3, False),
  ("rule",    ["Aunt Srey's rules.", "Thorns around the house. Laundry inside.",
               "And if the dogs bark at a light, stay inside."], 0.3, False),
  ("dogs",    ["At midnight, every dog began to bark.", "And Dara's white sarong was still on the line."], 0.6, True),
  ("light",   ["Over the rice field, a light floated closer.", "Not a lantern. A woman's head. Glowing."], 0.5, True),
  ("mistake", ["Dara ran down to grab the sarong.", "The dogs went silent. And the thorns under the house were gone."], 0.5, False),
  ("cliff",   ["She hid behind the water jar and held her breath.", "The glow stopped. Right above her.",
               "Would you look up?"], 1.6, True),
 ],
 "p2": [
  ("recap",   ["A glowing head found Dara hiding under the house.", "And it was right above her."], 0.3, False),
  ("whisper", ["Something cold touched her hair.", "Dara, it whispered. Is your aunt asleep?"], 0.6, True),
  ("escape",  ["Dara grabbed a thorny branch and swung it.", "The head shrieked and flew back.",
               "She ran upstairs and circled her aunt's bed with thorns."], 0.4, False),
  ("dawn",    ["All night, the light circled the house.", "Then the sun rose, and it raced back to the forest, to find its body."], 0.4, False),
  ("twist",   ["In the morning, a kind neighbour brought rice soup.", "She smiled. And on her cheek...", "a fresh thorn scratch."], 1.0, True),
  ("explain", ["This is the Ap, Cambodia's floating head. Thailand calls her Krasue.",
               "By day, a normal woman. At night, her head flies off to hunt.",
               "Thorns and guard dogs keep her away, and laundry comes in at night."], 0.5, False),
  ("outro",   ["So, would YOU have survived?", "Cambodian friends, did your grandma warn you about the Ap? Which country next?"], 1.8, False),
 ],
}
SAY = {"Siem Reap": "See-em Reeup", "Srey": "Srei", "Krasue": "Krah-sue", "the Ap": "the Ahp", "Ap,": "Ahp,", "Dara": "Dah-ra"}
