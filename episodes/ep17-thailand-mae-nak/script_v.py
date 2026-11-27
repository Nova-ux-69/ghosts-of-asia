# Ghosts of Asia - Episode 17: Mae Nak of Phra Khanong (Thailand) - 2.1D survival version
# True facts used (read 2026-11-27, Wikipedia "Mae Nak Phra Khanong" + coconuts.co "Mae Nak: visiting the shrine"):
#  - Nak lived on the banks of the Phra Khanong canal with her husband Mak; 19th-century Siam (local folklore says the
#    reign of King Rama IV). Mak was away at war; Nak and their baby died in childbirth, but when he came home they
#    were waiting for him. Neighbours who tried to warn him were rebuffed.
#  - Mak found out when Nak, making nam phrik (chili paste), dropped a lime off the porch and stretched her arm down
#    to the ground below to pick it up.
#  - He fled; "according to Thai folklore, ghosts are afraid of sticky Blumea leaves", so he hid behind a nat
#    (Blumea balsamifera) bush, then ran into Wat Mahabut, holy ground a ghost cannot enter.
#  - Today her shrine at Wat Mahabut (On Nut / Sukhumvit 77, Bangkok) gets dresses, toys for her child, lotuses,
#    incense; men pray to avoid military conscription; lottery hopefuls come on draw nights.
# The boatman, the little boy and the lime-at-dawn twist are fiction (the story beats around them follow the legend).
PARTS = {
 "p1": [
  ("hook",    ["In Thailand, if your wife drops a lime... never watch her pick it up.",
               "Because her arm... might keep getting longer."], 0.6, True),
  ("setup",   ["Bangkok, long ago. The Phra Khanong canal.", "Mak is rowing home from the war.",
               "His wife Nak and their new baby are waiting."], 0.3, False),
  ("rule",    ["An old boatman grabbed his oar and whispered:", "Mak... your wife died giving birth.",
               "Watch her arms. And if you see... run to the temple."], 0.3, False),
  ("home",    ["But Nak was waiting on the porch, smiling, with the baby.", "The dogs stopped barking.",
               "Mak laughed at the old man's story."], 0.4, False),
  ("lime",    ["Later, Nak was making chili paste.", "A lime rolled... and dropped through the floor.",
               "Under the house, Mak watched her arm come down... and down."], 0.4, True),
  ("mistake", ["Mak gasped.", "Up on the porch, the pounding stopped.",
               "Mak... you saw it, didn't you?"], 0.4, True),
  ("cliff",   ["He ran into the dark, and hid in a bush of nat leaves.", "Her footsteps stopped... right beside him.",
               "Stay hidden... or run?"], 1.6, True),
 ],
 "p2": [
  ("recap",   ["Mak is hiding in a bush of nat leaves.", "And his dead wife is standing right beside it."], 0.3, False),
  ("bush",    ["Old people say ghosts hate sticky nat leaves.", "She sniffed... stepped back...",
               "and screamed."], 0.8, True),
  ("run",     ["Mak ran along the canal, toward Wat Mahabut.", "Behind him, her arm stretched across the water.",
               "Closer... and closer."], 0.3, False),
  ("temple",  ["He fell through the temple gate.", "Nak stopped at the line. Ghosts cannot enter holy ground.",
               "She only cried: Mak... come home."], 0.4, False),
  ("twist",   ["At dawn, a little boy came to the temple.", "Your wife says... you dropped this.",
               "In his hand... a lime."], 1.0, True),
  ("explain", ["This is Mae Nak of Phra Khanong, Thailand's most famous ghost.",
               "She died giving birth while Mak was at war... and waited for him anyway.",
               "Today her shrine at Wat Mahabut in Bangkok is full of dresses, and toys for her baby."], 0.5, False),
  ("outro",   ["Would YOU have run... or stayed?", "Thai friends, have you visited Mae Nak's shrine?"], 1.0, False),
 ],
}
SAY = {"Phra Khanong": "Prah Kah-nong", "Mahabut": "Mah-hah-boot", "Nak": "Nahk", "nat": "naht", "Mak": "Mahk"}
