# Ghosts of Asia - Episode 15: Phi Pop (Laos) - 2.1D survival version
# True facts used (Wikipedia "Pop (ghost)"; Ian G. Baird, "Where Do the Ravenous Spirits (Phi Pop) Go?",
# Southeast Asian Studies 13(1), 2024 - read 2026-11-26):
#  - The Phi Pop is a hungry, "ravenous" spirit of Lao (and Thai Isan) folklore that possesses a living person.
#  - Stories say it gets into people who practised magic carelessly.
#  - A spirit doctor (mor phi) is called to drive it out.
# Story detail (Lao custom, not a Phi Pop fact): white baci strings are tied on the wrist as a blessing to keep
# the soul with the body.
# Noy, Tou, Grandma, Auntie Kham and the village are fiction. Real people are still accused of being Phi Pop in
# some villages, so the story never points at any real group: the spirit is the villain, and Auntie Kham is saved.
PARTS = {
 "p1": [
  ("hook",    ["In Laos, if a neighbor knocks at midnight and says she's hungry...", "do NOT let her in."], 0.6, True),
  ("setup",   ["Noy is babysitting her little brother Tou.", "Grandma is at the temple all night.",
               "Keep him safe until the dawn drum."], 0.3, False),
  ("rule",    ["Grandma tied white strings on their wrists.",
               "A Phi Pop hides inside people. The strings keep it off you.",
               "And never let in anyone who's hungry."], 0.3, False),
  ("visitor", ["At midnight... a knock.", "Auntie Kham from next door. Noy... I'm so hungry. Let me in.",
               "Noy didn't see her shadow."], 0.5, True),
  ("gone",    ["Noy said no. The dogs went quiet.", "Then she checked the mosquito net.", "Tou was gone."], 0.4, False),
  ("mistake", ["From under the house, a small voice. Noy... come down.",
               "In the dark, a nail caught her wrist.", "One string snapped."], 0.4, False),
  ("cliff",   ["She hid in the rice barn.", "Something was sniffing through the slats.", "Stay hidden... or run?"], 1.6, True),
 ],
 "p2": [
  ("recap",   ["Noy's little brother is missing.", "And something is sniffing outside the rice barn."], 0.3, False),
  ("snap",    ["Long fingers slid through the slats.", "A second string snapped.",
               "Then her face looked down from the roof."], 0.6, True),
  ("found",   ["On the rice sacks... Tou was asleep.", "Then, far away, the temple drum. Dawn."], 0.3, False),
  ("run",     ["Noy grabbed him and ran for the temple.", "Bare feet behind them. Faster than any person.",
               "At the temple gate, the drum boomed.",
               "Auntie Kham fell. Something dark left her... and flew away."], 0.4, False),
  ("twist",   ["Auntie Kham remembered nothing.", "But at breakfast, Tou ate... and ate...",
               "I'm still so hungry, he said."], 1.0, True),
  ("explain", ["This is the Phi Pop of Lao folklore.", "A hungry spirit that hides inside a living person.",
               "Stories say it gets in through careless magic. A spirit doctor, the mor phi, drives it out."], 0.5, False),
  ("outro",   ["Would YOU have opened the door?", "Lao friends, what did your grandparents say about the Phi Pop? Which country next?"], 1.8, False),
 ],
}
SAY = {"Phi Pop": "Pee Pop", "mor phi": "mor pee", "Tou": "Too", "Kham": "Kahm", "Noy": "Noi"}
