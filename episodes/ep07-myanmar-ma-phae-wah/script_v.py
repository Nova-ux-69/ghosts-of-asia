# Ghosts of Asia - Episode 7: Ma Phae Wah (Myanmar)
# True facts used (Wikipedia "Ma Phae Wah"):
#  - Ma Phae Wah is a Burmese nat (spirit), the guardian spirit of graveyards and cemeteries in Myanmar.
#  - Her name literally means "yellow-ribbon lady"; she is described wearing yellow (a yellow robe / longyi).
#  - At midnight she hoists a coffin onto her shoulder and shuffles through town, long hair waving.
#  - Where she lays her coffin on a doorstep, someone in that family will soon fall sick.
#  - King Tharrawaddy issued a royal order naming her guardian of the cemeteries.
# The story (Thiri, Grandma, the lamp, the shutter, the ribbon on the step) is our own fiction around these facts.
# Survival beats (PLAYBOOK 2a): goal = keep the lamp burning until sunrise (lamp-oil gauge on screen = ticking clock);
# rule = don't look, never call out; wrong choice = she calls out; near miss = praying in the dark while it knocks;
# escape = sunrise + the monastery bell; twist = another lamp goes out across the road.
PARTS = {
 "p1": [
  ("hook",    ["In Myanmar, if a woman in yellow walks past your house at midnight, carrying a coffin,",
               "pray she does not stop at your door."], 0.6, True),
  ("town",    ["Thiri lived with her grandma in a teak house, next to the graveyard.",
               "Tonight, she has one job: keep the lamp burning until sunrise."], 0.4, False),
  ("warn",    ["If you hear slow footsteps outside, Grandma said, do not look.",
               "And never, ever call out to her."], 0.5, False),
  ("look",    ["At midnight, the lamp oil was running low. Then she heard it.",
               "Shuffle... shuffle...",
               "She opened the shutter, just a little.",
               "A woman in yellow walked down the road, a coffin on her shoulder."], 0.5, False),
  ("call",    ["Hello? Thiri whispered.", "The woman stopped.", "And her head turned... too far."], 0.9, True),
  ("cliff",   ["Then she walked to the house. Step. By. Step.",
               "And slowly, she lowered the coffin, right at Thiri's door.",
               "If you were Thiri... would you run, or hide?"], 1.6, True),
 ],
 "p2": [
  ("recap",   ["Thiri called out to the woman in yellow.",
               "And she began to put her coffin down at Thiri's door."], 0.4, False),
  ("pray",    ["Grandma pulled Thiri away from the window.",
               "Do not look at her, she whispered. Pray with me.",
               "They held hands and prayed, until the lamp went out."], 0.6, False),
  ("door",    ["Something knocked on the door. Three times.", "Then, silence.",
               "Then the shutter flew open."], 1.5, True),
  ("empty",   ["Nobody was there."], 0.8, True),
  ("dawn",    ["At sunrise, the monastery bell rang. The coffin was gone.",
               "Only a yellow ribbon lay on the doorstep.",
               "But that night, across the road, another lamp went out."], 0.8, False),
  ("explain", ["This is Ma Phae Wah, from Burmese folklore. Her name means yellow ribbon lady.",
               "She guards the graveyards, by order of a Burmese king.",
               "At midnight, she carries a coffin through town.",
               "Where she puts it down, someone falls sick."], 0.5, False),
  ("outro",   ["So, would you have opened the shutter?", "And which country next? Tell me in the comments."], 1.4, False),
 ],
}
# How the narrator should pronounce some words (captions keep the normal spelling).
SAY = {"Ma Phae Wah": "Mah Peh Wah", "Thiri": "Theeri", "Myanmar": "Myan-mar"}
