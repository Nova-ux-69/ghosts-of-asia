# Ghosts of Asia - Episode 11: the Ma Da (Vietnam) - 2.1D survival version
# True facts used (searched 2026-11-25; thesmartlocal.com "Ghosts and demons in Vietnamese folklore", Toan Ngo 2021):
#  - Ma Da are believed to be the souls of people who drowned; they lurk in rivers and lakes.
#  - They cannot find peace and can only be reborn if someone else takes their place, so they drag swimmers down.
#  - They are said to look like drowned bodies with river weed for hair; children in river areas are taught to fear them
#    (a warning not to swim alone / in unsafe water).
#  - Many Vietnamese boats have eyes painted on the bow ("mat thuyen"), a long tradition to watch over the boat on the water.
# Bao, his grandma, the canal and the shrine are fiction; the setting is a generic Mekong Delta canal village.
PARTS = {
 "p1": [
  ("hook",    ["In Vietnam, if a child calls for help from the river at night...", "don't reach in."], 0.6, True),
  ("bridge",  ["Bảo is walking home through the Mekong Delta.", "Midnight. One last bamboo bridge over the canal.",
               "And his torch is dying."], 0.3, False),
  ("rule",    ["His grandma always warned him.", "The drowned cannot rest until someone takes their place.",
               "So never touch the water at night."], 0.3, False),
  ("water",   ["Halfway across, the dogs stopped howling.", "Something is swimming under the bridge.",
               "You can see it. Bảo can't."], 0.5, True),
  ("voice",   ["Then a small voice, from the dark water.", "Help me... I'm drowning!"], 0.4, False),
  ("mistake", ["Bảo knelt down and reached for the voice.", "A cold hand closed around his wrist.",
               "His torch fell in... and sank, still shining."], 0.5, False),
  ("cliff",   ["He pulled free and hid in an old boat.", "Drip. Drip. Wet hair slid over the side.",
               "Stay hidden... or jump?"], 1.6, True),
 ],
 "p2": [
  ("recap",   ["Bảo reached into the river at night.", "Now the drowned one is climbing into his boat."], 0.3, False),
  ("boat",    ["The boat tipped. Cold water crept toward his feet.", "Then a giggle... right behind his ear."], 0.6, True),
  ("eyes",    ["On the bow, two big painted eyes stared into the dark.", "And the thing stopped... as if it was afraid.",
               "Bảo jumped for the bank and ran."], 0.4, False),
  ("shrine",  ["Wet footsteps chased him along the canal.", "He reached the little shrine and lit the incense.",
               "The footsteps stopped. The sky turned grey."], 0.4, False),
  ("twist",   ["At home, Bảo washed his face, shaking.", "Then he saw his wrist.",
               "Tied around it... a ring of wet river weed."], 1.0, True),
  ("explain", ["This is the Ma Da, the water ghost of Vietnam.",
               "Folk tales say they are the souls of the drowned.",
               "To be reborn, one must take someone's place. So they pull swimmers down."], 0.5, False),
  ("outro",   ["So, would YOU have reached into the water?", "Vietnamese friends, did your grandma warn you about the river? Which country next?"], 1.8, False),
 ],
}
SAY = {"Bảo": "Bough", "Ma Da": "Mah Zah", "Mekong": "May-kong"}
