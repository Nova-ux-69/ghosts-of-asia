# Ghosts of Asia - Episode 7: Ma Phae Wah (Myanmar) - 2.1D survival version
# True facts used (Wikipedia "Ma Phae Wah"; The Myanmar Times "The Ghost Guide: 6 terrifying ghouls of Myanmar", 2015):
#  - Ma Phae Wah means "yellow-ribbon lady"; she is a Burmese nat, the guardian spirit of graveyards and cemeteries.
#  - Folklore: at midnight she carries a coffin on her shoulder through town with her long hair waving;
#    where she stops and lays the coffin on a doorstep, someone in that family soon falls sick.
#  - King Tharrawaddy is said to have declared her guardian of the cemeteries.
# Yayway Cemetery is a real cemetery in North Okkalapa, Yangon (Wikipedia). The hero and events are fiction.
PARTS = {
 "p1": [
  ("hook",   ["In Myanmar, if every dog howls at midnight...", "go inside. And lock the door."], 0.6, True),
  ("bus",    ["Min works the night shift in Yangon.", "Tonight, he missed the last bus. His phone: three percent.",
              "The only way home is the lane beside the cemetery."], 0.3, False),
  ("rule",   ["His grandma always warned him.", "If you see a yellow ribbon at night, don't look at her.",
              "And never let her stop at your door."], 0.3, False),
  ("dogs",   ["Halfway down the lane, every dog began to howl.", "Then, all at once... they stopped."], 0.9, True),
  ("ribbon", ["A yellow ribbon lay on the road.", "And behind the graves stood a woman with long black hair,",
              "carrying a coffin on her shoulder."], 0.5, True),
  ("run",    ["Min ran. His phone died.", "Thump. Thump. Every time he looked back, she was closer."], 0.5, False),
  ("cliff",  ["He slammed his door and looked through the gap.", "She stopped. Right at his doorstep.",
              "And put the coffin down.", "Would you open the door?"], 1.6, True),
 ],
 "p2": [
  ("recap",   ["A ghost with a coffin followed Min home,", "and stopped at his door."], 0.3, False),
  ("knock",   ["Knock. Knock. Knock.", "Min, a soft voice whispered. It's grandma. Open the door."], 0.6, True),
  ("hide",    ["But grandma was far away, in her village.", "Min lit a candle, held his breath, and prayed.",
               "Under the door, a shadow moved left... then right."], 0.6, False),
  ("dawn",    ["Then, far away, a monastery bell rang. Dawn.", "When he opened the door, the coffin was gone."], 0.4, False),
  ("twist",   ["Only a yellow ribbon, tied to his door handle.", "And on his back, a cold mark of five fingers."], 1.0, True),
  ("explain", ["This is Ma Phae Wah, the yellow ribbon lady.", "In Burmese folklore, she is the spirit who guards the cemeteries.",
               "People say she carries a coffin at midnight,", "and where she puts it down, someone in that house falls sick."], 0.5, False),
  ("outro",   ["So, would you have survived?", "Did your grandma tell you about her? Which country next?"], 1.8, False),
 ],
}
SAY = {"Ma Phae Wah": "Mah Pheh Wah", "Myanmar": "Myan-mar", "Yangon": "Yan-gon", "Min": "Min"}
