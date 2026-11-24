# Ghosts of Asia - SPECIAL EPISODE: South Korea / Cheonyeo Gwishin (the maiden ghost)
# Mixed style (Nova's choice, 2026-11-25): painted blood-moon exteriors, red-silhouette interiors, CCTV scares.
# True facts used (Wikipedia "Korean virgin ghost" / "Gwisin", searched 2026-11-25):
#  - The cheonyeo gwishin is the ghost of a young woman who died unmarried; folklore says she is full of "han",
#    a deep sorrow and resentment that keeps her from resting.
#  - She is shown in a white hanbok called "sobok", the traditional mourning clothes, with her long hair down,
#    because traditionally only married women tied their hair up.
#  - In Korean, the number four (sa) sounds like the word for death, so many buildings avoid a "4th floor".
# Ji-ho, his school and the gate guard are fiction. "Night self-study" (yaja) is a real Korean high school routine.
PARTS = {
 "p1": [
  ("hook",    ["In Korea, if you're alone at school at night...", "and a girl hums in the empty hallway...",
               "don't look back."], 0.6, True),
  ("school",  ["Ji-ho stayed late for night study at his school in Seoul.",
               "It's ten fifty-five. The gate locks at eleven.", "And his classroom is on the fourth floor."], 0.3, False),
  ("rule",    ["In Korean, four sounds like death.", "The rule for this floor: if a girl in white hums...",
               "keep your eyes down, and hold your red talisman."], 0.3, False),
  ("hall",    ["Then the lights went out, one by one.", "Far away, the dogs began to howl.",
               "And at the end of the hallway... humming."], 0.5, True),
  ("camera",  ["On the school camera, you can see Ji-ho walking fast.", "And you can see who is walking behind him.",
               "Closer. Every time."], 0.4, False),
  ("mistake", ["Ji-ho ran. His talisman slipped from his pocket.", "Behind him, a girl's voice whispered his name.",
               "And he looked back."], 0.5, True),
  ("cliff",   ["He hid in the toilet and held his breath.", "The humming stopped. Right outside his door.",
               "Open the door... or wait?"], 1.8, True),
 ],
 "p2": [
  ("recap",   ["Ji-ho lost his talisman, and he looked back.", "Now she is waiting outside his toilet stall."], 0.3, False),
  ("stall",   ["Drip. Drip. Then, under the door...", "long black hair slid across the floor.",
               "Toward his shoes."], 0.6, True),
  ("escape",  ["He remembered the rule. Eyes down. Don't look at her.", "He pushed past the cold, and ran for the stairs.",
               "Fourth floor. Third. Second."], 0.3, False),
  ("gate",    ["Ten fifty-nine. The guard was closing the gate!", "Ji-ho squeezed through, just in time.",
               "Behind him, the humming stopped."], 0.4, False),
  ("twist",   ["Next morning, the guard checked the gate camera.", "Ji-ho ran out alone.",
               "One second later... a girl in white walked out after him."], 1.0, True),
  ("home",    ["Ji-ho never came back to school.", "His mother says, every night, he sits by his window...",
               "and hums a song he never learned."], 1.6, True),
  ("explain", ["The Cheonyeo Gwishin: a young woman who died unmarried, full of han, deep sorrow.",
               "White mourning hanbok. Long hair down."], 0.5, False),
  ("outro",   ["So, would YOU have looked back?", "Which country next? Comment below!"], 1.6, False),
 ],
}
SAY = {"Ji-ho": "Jee-ho", "Cheonyeo Gwishin": "Chuh-nyuh Gwee-shin", "full of han,": "full of hahn,", "hanbok": "hahn-bok"}
