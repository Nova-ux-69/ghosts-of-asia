# Ghosts of Asia - Episode 6: Jiangshi (China)
# True facts used (Wikipedia "Jiangshi"):
#  - "Jiangshi" literally means "stiff corpse"; it is usually shown in official clothes from the Qing dynasty.
#  - A Taoist paper talisman (fulu) stuck on the forehead immobilises it.
#  - The legend is linked to "driving corpses" in Xiangxi (western Hunan): priests were hired to bring people who
#    died far away home for burial, "transporting a corpse over a thousand li", moving only at night, ringing bells.
#  - Folk advice: hold your breath and a jiangshi cannot find you (the page says because they are blind).
#  - Glutinous (sticky) rice, mirrors and peach wood are listed as things that keep it away.
PARTS = {
 "p1": [
  ("hook",    ["In China, if you see a man hopping on a dark mountain road,",
               "do not breathe. Not even a little."], 0.6, True),
  ("inn",     ["Mei lived at a small inn on a river in Hunan, under the misty mountains.",
               "One night, a priest knocked at the door, ringing a little bell."], 0.4, False),
  ("warn",    ["He was walking three dead travellers home, to be buried.",
               "They sleep in your shed tonight, he said.",
               "Never touch the yellow paper on their faces."], 0.4, False),
  ("paper",   ["But at midnight, Mei wanted to see.",
               "She lifted one yellow paper, just a little.",
               "And the wind took it from her hand."], 0.6, False),
  ("wake",    ["The tall man in the old robe opened his eyes.",
               "His arms rose straight out.", "And he hopped."], 0.8, True),
  ("cliff",   ["Mei ran for the door. Thud. Thud. It was faster.",
               "It stopped one breath away from her face.",
               "Part two is up now."], 2.2, True),
 ],
 "p2": [
  ("recap",   ["Last time, the wind blew the yellow paper off a dead man's face.",
               "And he hopped after Mei."], 0.4, False),
  ("breath",  ["Then Mei remembered the old tales.", "Hold your breath, and it cannot find you.",
               "So she held it. Its cold face turned left... then right."], 0.8, True),
  ("bell",    ["Her chest burned. She could not hold on much longer.",
               "Then a bell rang. The priest ran in, and slapped the paper back on.",
               "The dead man froze."], 0.6, False),
  ("dawn",    ["Before sunrise, the priest led them away,",
               "three dead men hopping in a line, his bell ringing in the mist."], 0.6, False),
  ("explain", ["This is the Jiangshi, from Chinese folklore. Its name means stiff corpse.",
               "It wears the clothes of an old Qing dynasty official.",
               "Old stories from Hunan say priests walked the dead home at night, ringing bells."], 0.5, False),
  ("outro",   ["So, could you hold your breath that long?", "And which country next? Tell me in the comments."], 2.0, False),
 ],
}
# How the narrator should pronounce some words (captions keep the normal spelling).
SAY = {"Jiangshi": "Jyahng-shir", "Hunan": "Hoo-nahn", "Qing": "Ching", "Mei": "May"}
