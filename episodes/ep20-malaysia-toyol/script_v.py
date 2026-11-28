# Ghosts of Asia - Episode 20: the Toyol (Malaysia) - 2.1D survival version
# True facts used (read 2026-11-28):
#  - Toyol: a small child spirit of Malay folklore (Malaysia; "tuyul" in Indonesia), traditionally a near-naked toddler,
#    in modern tellings green or grey with pointed ears and red eyes; called up by a bomoh with black magic and kept by
#    its owner, often in a jar or bottle, fed milk and sweets; it steals money and valuables for its owner and is said to
#    take only half (Wikipedia "Toyol"; Yahoo Malaysia "Toyol, a sneaky spirit with a sweet tooth").
#  - To protect money, people put out green beans, rice grains or marbles, which it must stop and count, and keep
#    needles or a mirror by their cash; it loves toys and sweets (Yahoo Malaysia; The Sun Malaysia 2026 "Missing cash?
#    Malaysians once had one answer: the toyol"; Wikipedia).
#  - 2006: a fisherman in Kuala Pahang found a bottle said to hold a toyol; it was handed to the state museum (Wikipedia).
# Aiman, his family's shop, Tok Wan's rules, the mirror escape and the coin-tin twist are fiction.
PARTS = {
 "p1": [
  ("hook",    ["In Malaysia, if your money keeps going missing... don't blame your little sister.",
               "Check under the bed. Something small... is counting it."], 0.6, True),
  ("setup",   ["A kampung in Kelantan, ten at night.",
               "Aiman is closing his family's little shop, alone.",
               "One goal: count the money and lock up before Abah gets back."], 0.3, False),
  ("rule",    ["Before she left, Tok Wan put a bowl of green beans by the till.",
               "If money goes missing, it's a toyol. They say it only takes half.",
               "It must count every bean. So whatever you do... let it count."], 0.3, False),
  ("coins",   ["Aiman counted the money: eight hundred ringgit.",
               "He went to pull down the shutter...", "and counted again. Four hundred."], 0.5, True),
  ("beans",   ["Then, behind the counter, tiny fingers began to count.",
               "Satu... dua... tiga...", "Something small was sitting by the bowl."], 0.4, True),
  ("mistake", ["Aiman grabbed the bowl and threw the beans out the door.",
               "The counting stopped.", "And every light in the shop went out."], 0.4, True),
  ("cliff",   ["He hid under the counter, holding his breath.",
               "Small wet feet came closer... and stopped.", "Stay hidden... or run?"], 1.6, True),
 ],
 "p2": [
  ("recap",   ["Aiman is hiding under the counter, in the dark.",
               "And the toyol is standing right in front of him."], 0.3, False),
  ("peek",    ["A tiny cold hand slid into his pocket.", "Half for me... half for you."], 0.8, True),
  ("mirror",  ["Then Aiman remembered Tok Wan's last rule:", "Show it its own face.",
               "He tore the round mirror off the wall... and held it up."], 0.4, False),
  ("flee",    ["It shrieked at its own reflection and ran out into the night,",
               "across the road, to the big new house... with a jar in the window.",
               "Aiman didn't move until the roosters crowed."], 0.4, False),
  ("twist",   ["That morning, his little sister shook her coin tin.", "Half was gone.",
               "And under her bed, something tiny was counting. Satu... dua..."], 1.0, True),
  ("explain", ["This is the toyol of Malay folklore: a small child spirit, said to be kept in a jar and fed milk and sweets.",
               "It steals money for its owner. So people leave out green beans or rice: it must count them.",
               "In 2006, a fisherman in Pahang found a bottle said to hold one. It went to a museum."], 0.5, False),
  ("outro",   ["Would YOU have let it count?", "Malaysian friends, did your family ever blame a toyol for missing money?"], 1.0, False),
 ],
}
SAY = {"toyol": "toy-yol", "Toyol": "Toy-yol", "Satu": "Sah-too", "dua": "doo-ah", "tiga": "tee-gah", "Kelantan": "Keh-lahn-tahn",
       "Aiman": "Eye-mahn", "Abah": "Ah-bah", "Tok Wan": "Toke Wahn", "kampung": "kahm-poong", "ringgit": "ring-git", "Pahang": "Pah-hahng"}
