# Ghosts of Asia - Episode 14: Tikbalang (Philippines) - 2.1D survival version
# True facts used (Wikipedia "Tikbalang", read 2026-11-26):
#  - A tall, bony creature with the head and hooves of a horse and very long limbs:
#    when it squats, its knees reach above its head.
#  - It is linked to dark, overgrown places: bamboo clumps, banana groves, big trees, and beneath bridges.
#  - It leads travelers astray, making them return to the same path no matter how far they go.
#  - Wearing your shirt inside out is believed to counteract this; people also ask permission aloud to pass.
#  - Rain from a clear sky: "may kinakasal na tikbalang" - a tikbalang is getting married.
# Paolo, his lola and the barangay are fiction.
PARTS = {
 "p1": [
  ("hook",    ["In the Philippines, if the same path keeps bringing you back...", "something tall is playing with you."], 0.6, True),
  ("setup",   ["Paolo missed the last jeepney.", "Lola's house is two kilometers away, through the bamboo forest.",
               "Phone battery: nine percent."], 0.3, False),
  ("rule",    ["Lola always said: in the forest, ask permission to pass.",
               "And if the path keeps bringing you back... turn your shirt inside out."], 0.3, False),
  ("rain",    ["Then it rained... from a clear, moonlit sky.", "Lola called that a tikbalang wedding.",
               "Something tall was watching. Paolo didn't see it."], 0.4, True),
  ("loop",    ["Ten minutes later, he passed the same broken sign.", "Then again. And again.",
               "The map said one point two kilometers. Always."], 0.3, False),
  ("mistake", ["Paolo forgot the rule. He shouted: Who's there?", "Something laughed... like a horse.",
               "Then hooves. Running. Straight at him."], 0.4, False),
  ("cliff",   ["He hid under an old wooden bridge.", "The hooves stopped... right above him.",
               "Stay hidden... or run?"], 1.6, True),
 ],
 "p2": [
  ("recap",   ["Paolo is lost in the bamboo forest.", "And the hooves just stopped on the bridge above him."], 0.3, False),
  ("under",   ["Dust fell through the planks.", "Then a long face leaned down... upside down... and smiled."], 0.6, True),
  ("chase",   ["Paolo ran. His phone died.", "And there it was on the path, squatting.",
               "Its knees were higher than its head."], 0.4, False),
  ("escape",  ["Then he remembered the rest of the rule.", "He turned his shirt inside out.",
               "Tabi po. Please, let me pass.", "The rain stopped. And there were the lights of Lola's house."], 0.4, False),
  ("twist",   ["The next morning, there were hoofprints around the house.",
               "And on his window... three long, golden hairs."], 1.0, True),
  ("explain", ["This is the tikbalang of Philippine folklore.",
               "Tall and bony, with the head and hooves of a horse.",
               "It leads travelers in circles. A shirt worn inside out is said to break the trick."], 0.5, False),
  ("outro",   ["Would YOU find your way out?", "Filipino friends, what did your lola warn you about? Which country next?"], 1.8, False),
 ],
}
SAY = {"tikbalang": "teek-bah-lahng", "Tabi po": "Tah-bee poh", "Lola": "Loh-lah", "Paolo": "Pow-loh", "jeepney": "jeep-nee"}
