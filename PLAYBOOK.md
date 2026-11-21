# Ghosts of Asia — Daily Shorts Playbook

This repo is the production kit for Nova's YouTube channel. Every day, one new **episode** is made as **two vertical Shorts**:

- **Part 1** goes public at **7:00 AM Singapore time** (Asia/Singapore). It has a hook and ends on a cliffhanger.
- **Part 2** goes public at **7:00 PM the same day**. It has a recap, the payoff, the legend explained, and a question for the comments.

Nova's goal is to grow the channel and succeed on YouTube. Ghost stories from Asia come first, and other topics may come later. Every episode should be made the way a top Shorts creator would make it.

---

## 1. Daily run checklist

1. **Set up.** Run `bash toolkit/setup.sh`.
2. **Read `episodes/LOG.md`.** It shows what's already posted, what's scheduled, and what's next in the backlog. Never repeat a ghost unless LOG.md says an audience request asked for it.
3. **Research the legend.** Run 1–3 web searches and use only well-sourced folklore facts. Write 2–3 true facts into the episode notes.
4. **Write the script** in `episodes/epNN-country-ghost/script_v.py`. Copy the structure from ep02 and follow the story rules in section 2.
5. **Record the narration.** From the episode folder, run `python3 ../../toolkit/gen_voice.py`. This writes `p1/`, `p2/`, `timing.json` and the voice files.
6. **Make the art.**
   - Copy `episodes/ep02-thailand-nang-tani/` as the starting point.
   - Write a **new ghost design** (`art_epNN.py`) and **new scenes** (`scenes_epNN.py`).
   - Each episode needs its own setting, palette, props and ghost silhouette. Never ship the same scenes with a new name. See section 3.
7. **Build the sound.** Adapt `sound_epNN.py`, then run `python3 sound_epNN.py p1` and `python3 sound_epNN.py p2`.
8. **Check the stills before the full render.** Run `python3 render_epNN.py p1 stills '[["hook",[5]], ...]'` and look at one frame per scene as a contact sheet. Fix anything ugly, cropped or unreadable.
9. **Render both parts.** Do it in parallel:
   - `python3 render_epNN.py p1 <scene ids...>` and the same for p2.
   - Concatenate with the ffmpeg concat demuxer.
   - Mux `pN/mix.wav` using `-af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 192k`.
   - Re-encode the final file with `-crf 25 -preset veryfast -movflags +faststart` so each part is **under 45 MB**.
10. **Check the final files.** Each part must be 1080×1920 and 40–75 seconds long. Look at 3 frames from each final MP4.
11. **Host the videos.** Copy the MP4s to `videos/epNN_partN.mp4`, then commit and push to `main`. The public URL is `https://raw.githubusercontent.com/Nova-ux-69/ghosts-of-asia/main/videos/<file>`. Confirm it loads with `curl -sI`.
12. **Schedule both parts in Metricool.** Use blogId `8271706` and timezone `Asia/Singapore`.
    - Set `providers=[{"network":"youtube"}]`.
    - Set `youtubeData`: `{"title": ..., "type": "short", "privacy": "public", "madeForKids": false, "isAiGeneratedContent": false, "category": "FILM_ANIMATION", "tags": [...]}`. `isAiGeneratedContent` is for realistic synthetic footage, and these are clearly animated cartoons.
    - Put the description in `text`. Put the video URL in `media`.
    - Part 1 goes at 07:00 and Part 2 at 19:00 on the same day: the first day in LOG.md that has no episode yet (normally tomorrow).
13. **Update `episodes/LOG.md`.** Add the date, episode, titles, Metricool planner URLs and any problems. Commit and push.
14. **Report to Nova** in 3–5 lines: what was made, when each part posts, and one growth tip from the data, if there is any.

If any step fails and can't be fixed, **don't post a broken video**. Write the problem in LOG.md and report it.

## 2. Story and retention rules (influencer playbook)

- **Hook in the first 2 seconds.** Open with a rule, a warning or a question, never with "Hello". Examples: "If you hear…, pray that…" or "In Japan, never answer this question…". Put the country name on screen immediately.
- **Open loops.** Part 1 must end on an unanswered question, with "PART 2 TONIGHT" on screen. Part 2 starts with a 5-second recap, so new viewers aren't lost.
- **Give the audience more information than the hero has.** Let viewers see the ghost before the character does. This builds tension and replays.
- **Use the rule-breaking structure.** Show a warning, show someone breaking it, then show the consequence. This is the most shareable shape for folklore.
- **Teach something true.** Part 2 explains the real legend in simple words, with 2–3 facts. This makes the videos "authentic, original value", which protects monetization under YouTube's inauthentic-content policy.
- **Comment bait that's genuine.** End Part 2 with a question viewers want to answer, such as "Which country next?", "Would you turn around?" or "Have you heard this story from your grandma?".
- **Keep the language simple.** Use short sentences and big subtitles. Many viewers watch on mute or in their second language.
- **Never show gore.** Creepy is fine, but avoid disturbing images. This keeps the videos ad-friendly and out of the "off-putting content" category.
- **Pace.** Change the shot every 5–10 seconds, and put a visual change on every key line: zooms, glows, reveals.
- **Length.** Each part should be 45–65 seconds.

## 3. Visual rules (avoid "template" content)

- **Use the same series brand every time:**
  - the Inter + Lora fonts
  - the "GHOSTS OF ASIA" label
  - the country name in big serif type
  - the PART pill
  - subtitles in the safe zone (box top at y=1320; keep everything important between y=200 and y=1500)
- **Change everything else each episode:**
  - colour palette
  - setting (village, city, school, forest, sea, temple)
  - architecture and props from that country
  - the ghost's design and colour
  - the camera moves
- **Keep the ghost design true to the legend.** For example: Pontianak has white dress and long hair; Nang Tani has a green Thai dress and floats; Kuchisake-onna wears a mask and long coat; Pocong is wrapped in a shroud and hops; Jiangshi wears Qing robes and a paper talisman and hops.

## 4. Captions, titles and hashtags (write fresh every time)

- **Title (max ~70 characters).** Combine curiosity with the series name, for example `Never answer if she asks this 😶 | Ghosts of Asia: Japan (Part 1)`. Vary the formula: warning / "why you should never…" / "the ghost that…" / a question.
- **Description.**
  - Lines 1–2 are a mini-hook in story voice.
  - Then one teaser line ("Part 2 drops tonight at 7pm"), plus one true fact about the legend.
  - Then the series line, then 6–9 hashtags: `#shorts` + `#horrorstories` + the ghost name + the country + `#asianfolklore` + `#ghoststory` + 1–3 trending or relevant ones.
- **Part 2's description links to Part 1** using the URL from LOG.md.
- **Pinned comment idea** (save it in LOG.md for Nova): a poll-style question for the audience.

## 5. Growth loop

- Post at fixed times every day. Consistency trains the algorithm and the audience.
- Every Sunday, check Metricool's YouTube analytics (`getAnalyticsDataByMetrics`). Note which hooks and countries got the most views and the best average view duration, then lean into those.
- If a country does well, follow up with "Ghosts of [country] Part 2: another legend".
- When a commenter asks for a country, prioritise it and mention it: "You asked for Vietnam…".

## 6. Backlog (in order; update LOG.md when you use one)

| # | Country | Ghost |
|---|---|---|
| 03 | Japan | Kuchisake-onna (slit-mouthed woman; show a mask, never gore) |
| 04 | Philippines | Manananggal |
| 05 | Indonesia | Pocong |
| 06 | China | Jiangshi (hopping corpse) |
| 07 | Myanmar | Ma Phae Wah |
| 08 | India | Chudail |
| 09 | Vietnam | Ma Da (water ghost) |
| 10 | Korea | Cheonyeo gwishin |
| 11 | Japan | Hanako-san of the toilet |
| 12 | Philippines | Tikbalang |
| 13 | Cambodia | Ap |
| 14 | Laos | Phi Pop |
