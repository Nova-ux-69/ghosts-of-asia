# Ghosts of Asia - Episode 3: Kuchisake-onna (Japan)
# True facts used (Wikipedia "Kuchisake-onna", nippon.com, Tokyo Weekender):
#  - She wears a mask (today a surgical mask) and asks "Watashi, kirei?" - "Am I pretty?"
#  - In 1979 rumors spread across Japan from Gifu; some schools had children walk home in groups with teachers.
#  - Folk escapes: answer that she looks "average" (so-so), or throw hard candy / fruit to distract her.
PARTS = {
 "p1": [
  ("hook",  ["In Japan, if a woman in a mask stops you at night and asks if she is pretty...",
             "be very careful how you answer."], 0.6, True),
  ("walk",  ["Yui was walking home late from cram school.",
             "The street was empty. Only the vending machines were glowing."], 0.4, False),
  ("warn",  ["That morning, her grandmother had warned her.",
             "If a masked woman asks you a question, never say yes. Never say no."], 0.4, False),
  ("appear",["Yui laughed it off.", "But under the next streetlight, someone was standing very still.",
             "A tall woman, in a long red coat and a white mask."], 0.5, False),
  ("ask",   ["She stepped closer. Her eyes never blinked.", "And she whispered...", "Am I pretty?"], 0.9, True),
  ("cliff", ["Yui's heart was pounding.", "What would you say?", "Part two, tonight."], 2.2, True),
 ],
 "p2": [
  ("recap", ["Last time, a masked woman stopped Yui on an empty street.",
             "She asked one question. Am I pretty?"], 0.4, False),
  ("answer",["Yui forgot the warning.", "She whispered, yes."], 0.5, True),
  ("mask",  ["The woman smiled behind her mask.", "Slowly, she began to pull it down.", "How about... now?"], 1.6, True),
  ("trick", ["Then Yui remembered her grandmother's trick.", "She looked up and said, you look... average."], 0.5, False),
  ("run",   ["The woman froze. She did not know what to do.",
             "And Yui ran, and ran, all the way home."], 0.5, False),
  ("explain",["This is Kuchisake-onna, the slit-mouthed woman of Japanese legend.",
              "In 1979, rumors about her spread so fast that some schools sent children home in groups.",
              "People say you can escape her by calling her average, or by throwing her hard candy."], 0.5, False),
  ("outro", ["So, what would you answer?", "Tell me in the comments."], 2.0, False),
 ],
}
