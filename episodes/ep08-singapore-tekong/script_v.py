# Ghosts of Asia - Episode 8: Pulau Tekong (Singapore) - 2.1D survival version
# Legend sources: remembersingapore.org "Singapore's Most Enduring Ghost Stories" (Charlie Company recruit lost on a
# route march, told by NS batches since the eighties; a third door said to be added to free his spirit);
# smong.net "Charlie, we may have company"; thesmartlocal "Tekong ghost stories" (the 3-door bunk).
# Pulau Tekong is Singapore's Basic Military Training island. Darren and all events are fiction. No gore.
PARTS = {
 "p1": [
  ("hook",   ["In Singapore, every army boy knows this rule.", "If someone calls your name in the Tekong jungle... don't answer."], 0.6, True),
  ("ferry",  ["Pulau Tekong. The island where Singapore's recruits train.", "Tonight, Darren's platoon starts a night route march. In the rain."], 0.3, False),
  ("rule",   ["Their sergeant warns them.", "Stay with your buddy. Never leave the track.", "And if you hear your name from the trees, keep walking."], 0.3, False),
  ("fall",   ["But Darren feels sick. He slows down.", "His torch flickers. Battery low.", "When he looks up, the platoon is gone."], 0.6, True),
  ("voice",  ["Darren! a voice calls from the jungle.", "It sounds just like his buddy."], 0.8, True),
  ("answer", ["He almost answers.", "Then he sees his buddy's torch, far ahead on the track.", "So who is calling from the trees?"], 0.6, True),
  ("cliff",  ["Something pale steps out between the trees.", "His torch dies.", "And the voice is right behind him.", "Would you turn around?"], 1.6, True),
 ],
 "p2": [
  ("recap",   ["Lost in the Tekong jungle, a voice called Darren's name,", "and it was right behind him."], 0.3, False),
  ("run",     ["Don't turn around. Darren runs, blind, through the rain.", "Mud. Branches. Footsteps behind him, matching his."], 0.4, False),
  ("lights",  ["Then, through the trees, the camp lights.", "He falls onto the parade square. His platoon stares at him.", "You were gone for two hours, they say."], 0.6, False),
  ("bunk",    ["That night, at three a.m., Darren wakes up.", "He counts the doors of his bunk. One. Two. Three.", "There were only two before."], 0.6, True),
  ("twist",   ["In the third door, a recruit in a soaking wet uniform is standing.", "Darren, it whispers. You didn't wait for me."], 1.0, True),
  ("explain", ["This is Singapore's most famous army ghost story, from Pulau Tekong.", "Since the eighties, recruits have whispered about a Charlie Company boy who got lost on a route march,",
               "and about a bunk with a strange third door.", "Some say it was built to let his spirit out."], 0.5, False),
  ("outro",   ["NS boys, did you hear this story in Tekong?", "Would you have answered? Which country next?"], 1.8, False),
 ],
}
SAY = {"Tekong": "Teh-kong", "Pulau": "Poo-lau", "NS": "N S"}
