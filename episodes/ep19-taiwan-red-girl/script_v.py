# Ghosts of Asia - Episode 19: the little girl in red / mo-sin-a (Taiwan) - 2.1D survival version
# True facts used (read 2026-11-28):
#  - Mo-sin-a (魔神仔, "mosien"/"moxina"): a mountain spirit of Taiwanese folklore, shared by Hoklo, Hakka and
#    indigenous communities; often described as small, like a child; it makes people lose their sense of direction and
#    leads them deep into the mountains / woods until they cannot find their way home - usually children and the
#    elderly (islandfolklore.com "In the shadows"; Taipei Times 2015-11-27; Wikipedia "Mo-sin-a").
#  - They are said to dislike loud noise, so loud firecrackers are used to drive them away (islandfolklore.com).
#  - The "little girl in red" (紅衣小女孩): a family's hiking home video broadcast on Taiwanese TV in the 1990s showed
#    a little girl in red walking with the group whom nobody remembered seeing (Taipei Times 2017-08-21; USC Folklore
#    Archives "Red-shirted girl in the mountain"); many believe she is a mo-sin-a. It inspired the horror film
#    "The Tag-Along" (紅衣小女孩, 2015) (Wikipedia; Taipei Times 2015-11-27).
# Mei, her family, the shrine firecrackers and the video-at-home twist are fiction. The date/place of the real video
# vary between sources, so the script only says "in the 1990s".
PARTS = {
 "p1": [
  ("hook",    ["In Taiwan, if you count your hiking group... and get one extra...",
               "don't count again. Because the extra one... wears red."], 0.6, True),
  ("setup",   ["A mountain trail near Taichung, at four in the afternoon.",
               "Mei is hiking with her grandpa, her mum and her little brother.",
               "One goal: get down before dark."], 0.3, False),
  ("rule",    ["At a tiny Earth God shrine, Grandpa lit incense and whispered:",
               "These mountains have a mo-sin-a. It leads people away.",
               "If it calls your name, don't answer. Stay with the ribbons.", "And it hates loud bangs."], 0.3, False),
  ("count",   ["Mei filmed them on the stone steps.", "Later, she counted on the screen: one, two, three...",
               "four. A little girl in red, at the back of the line."], 0.5, True),
  ("fog",     ["Then the fog came down. Grandpa's voice faded.",
               "The trail ribbons... were all red now.", "Mei followed them anyway."], 0.4, False),
  ("mistake", ["Mei! Mei, over here! It was Grandpa's voice.", "She shouted back: Grandpa?",
               "And the whole forest went silent."], 0.4, True),
  ("cliff",   ["She hid inside a hollow camphor tree.", "Small red shoes stopped... right in front of her.",
               "Stay hidden... or run?"], 1.6, True),
 ],
 "p2": [
  ("recap",   ["Mei is lost in the fog, hiding in a hollow tree.",
               "And the little girl in red is standing right outside."], 0.3, False),
  ("peek",    ["A small hand touched the bark.", "Mei... come and play with me."], 0.8, True),
  ("bang",    ["Then Mei remembered the firecrackers Grandpa bought for the shrine.",
               "She lit the whole string.", "BANG! The girl screamed... and the fog tore open."], 0.4, False),
  ("run",     ["Mei ran down the steps, past the real white ribbons.",
               "Torches. Voices. Grandpa, calling from the right direction."], 0.4, False),
  ("twist",   ["That night at home, Mei played the video again.", "One, two, three... the girl in red was gone.",
               "Then, right behind Mei, a small voice counted: four."], 1.0, True),
  ("explain", ["This is the mo-sin-a of Taiwanese folklore: a small mountain spirit, often like a child.",
               "People say it leads hikers, kids and old people deep into the mountains... and hates loud bangs.",
               "In the 1990s, a family's hiking video on Taiwanese TV showed a little girl in red nobody had seen."], 0.5, False),
  ("outro",   ["Would YOU have answered?", "Taiwanese friends, did your grandparents warn you about the mo-sin-a?"], 1.0, False),
 ],
}
SAY = {"mo-sin-a": "moh-sheen-ah", "Taichung": "Tie-chung", "Mei": "May"}
