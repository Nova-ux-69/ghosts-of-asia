# Ghosts of Asia — Daily Shorts Playbook

This repo is the production kit for Nova's YouTube channel. Every day, one new **episode** is made as **two vertical Shorts**:

- There are **two posting slots every day: 07:00 and 19:00 Singapore time** (Asia/Singapore). Each slot gets **one full episode: Part 1 and Part 2 together**, so viewers never wait (Nova's decision, 2026-11-22).
- **Part 1** goes public at the slot time (07:00 or 19:00). It has a hook and ends on a cliffhanger. NO "Part 2 is up now" text or voice anywhere (Nova, 2026-11-24).
- **Part 2** goes public **5 minutes later** (07:05 or 19:05), so it shows as the newest Short on the channel. It has a quick recap, the payoff, the legend explained, and a question for the comments.
- So there are **two new countries every day**. Two daily runs each make one episode for the next free slot.

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
10. **Make a cover image (thumbnail) for each part.** Viewers should see the country and part number at a glance. From the episode folder, run:

    `python3 ../../toolkit/thumbnail.py scenes_epNN p1 <scene> <t> "<COUNTRY>" "PART 1" "<3–6 word hook, *one word* in yellow>" epNN_part1_thumb.jpg [shift_px]`

    Do the same for p2 with "PART 2".
    - Pick the most intriguing frame: the mystery for Part 1, the ghost for Part 2.
    - Use `shift_px` (for example 420) so the ghost's face sits between the PART badge and the hook text, and isn't hidden.
    - Look at both covers before using them.
    - The series header (GHOSTS OF ASIA / COUNTRY / PART N) is also visible from frame 0 of the hook and recap scenes. Keep it that way, so the auto-picked cover works too.
11. **Check the final files.** Each part must be 1080×1920 and 40–75 seconds long. Look at 3 frames from each final MP4.
12. **Host the videos.** Copy the MP4s and the cover JPGs to `videos/` (`epNN_partN.mp4`, `epNN_partN_thumb.jpg`), then commit and push to `main`. The public URL is `https://raw.githubusercontent.com/Nova-ux-69/ghosts-of-asia/main/videos/<file>`. Confirm it loads with `curl -sI`.
13. **Schedule both parts in Metricool.** Use blogId `8271706` and timezone `Asia/Singapore`.
    - Set `providers=[{"network":"youtube"}]`.
    - Set `youtubeData`: `{"title": ..., "type": "short", "privacy": "public", "madeForKids": false, "isAiGeneratedContent": false, "category": "FILM_ANIMATION", "tags": [...]}`. `isAiGeneratedContent` is for realistic synthetic footage, and these are clearly animated cartoons.
    - Put the description in `text`. Put the video URL in `media`.
    - Set `videoThumbnailUrl` to the cover's raw GitHub URL. If Metricool rejects the post with `VIDEO_THUMBNAIL_NOT_APPLICABLE` (the channel isn't verified for custom Shorts thumbnails yet), schedule it again without `videoThumbnailUrl` and note it in LOG.md. The first frame still shows the country and part.
    - **Pick the target slot:** the first 07:00 or 19:00 slot that is at least 4 hours from now and is free in BOTH LOG.md and Metricool (`getScheduledPosts`). Never make a second episode for a slot that is taken.
    - Part 1 goes at the slot time (HH:00). Part 2 goes at HH:05 on the same day.
14. **Update `episodes/LOG.md`.** Add the date, episode, titles, Metricool planner URLs and any problems. Commit and push.
15. **Report to Nova** in 3–5 lines: what was made, when each part posts, and one growth tip from the data, if there is any.

If any step fails and can't be fixed, **don't post a broken video**. Write the problem in LOG.md and report it.

## 2. Story and retention rules (influencer playbook)

- **Hook in the first 2 seconds.** Open with a rule, a warning or a question, never with "Hello". Examples: "If you hear…, pray that…" or "In Japan, never answer this question…". Put the country name on screen immediately.
- **Open loops.** Part 1 must end on an unanswered question. Do NOT put "PART 2 IS UP NOW" on screen and do NOT say it in the narration (Nova removed it, 2026-11-24): end on the cliffhanger itself, then cut to black. Part 2 starts with a 5-second recap, so new viewers aren't lost.
- **Give the audience more information than the hero has.** Let viewers see the ghost before the character does. This builds tension and replays.
- **Use the rule-breaking structure** (inside the survival story of 2a). Show a warning, show someone breaking it, then show the consequence. This is the most shareable shape for folklore.
- **Teach something true.** Part 2 explains the real legend in simple words, with 2–3 facts. This makes the videos "authentic, original value", which protects monetization under YouTube's inauthentic-content policy.
- **Comment bait that's genuine.** End Part 2 with a question viewers want to answer, such as "Which country next?", "Would you turn around?" or "Have you heard this story from your grandma?".
- **Keep the language simple.** Use short sentences and big subtitles. Many viewers watch on mute or in their second language.
- **Never show gore.** Creepy is fine, but avoid disturbing images. This keeps the videos ad-friendly and out of the "off-putting content" category.
- **Pace.** Change the shot every 5–10 seconds, and put a visual change on every key line: zooms, glows, reveals.
- **Length.** Each part should be 45–65 seconds.

## 2a. SURVIVAL THRILLER story (Nova's request, 2026-11-24) — this comes first
Every episode is a **survival story**, not a lecture. The viewer should feel "would I make it out?" from start to finish.
- **A hero the viewer becomes.** One ordinary person (a student walking home, a night-shift worker, a tourist, a taxi driver), given a name and ONE goal in the first 10 seconds ("Ko Min just needs to get home before midnight").
- **Talk to the viewer as "you" at key moments** ("If you were Min, would you run?"). Second-person lines on choices make people stay.
- **A ticking clock.** Something runs out: the phone battery, the last bus, the candle, the time until sunrise, the fuel. Show it on screen (a battery icon, a clock, a candle getting shorter).
- **The survival rule from the legend.** Every legend has a rule that saves you (don't answer, hold your breath, don't look back, salt, a bell, sunrise). Show the rule early as a warning, so viewers watch for it.
- **Escalate in 3 steps.** Something small and wrong → proof it is real and following → trapped with no way out. Every 10–15 seconds the danger gets closer.
- **A wrong choice and a near miss.** The hero makes one mistake (looks back, answers, drops the charm) and only just escapes. Use a hiding scene: under a bed, in a cupboard, behind a tombstone, holding their breath while the ghost passes inches away.
- **Part 1 ends at the worst moment**: the hero is trapped and the ghost is right there. Last line: a choice for the viewer ("Run… or hide?"), then a hard cut to black on a scare hit. No "Part 2" line.
- **Part 2: the escape.** The hero uses the rule at the last second. Then a twist in the final 5 seconds (the ghost isn't gone, it followed someone else, or it's behind the viewer), THEN the true-legend facts and the comment question ("Would YOU have survived?").
- Keep it grounded: real places, real local details (food, street names, transport) so it feels like it could happen tonight.

## 2b. Make it SCARY (Nova's request, 2026-11-24)

Nova wants every episode scarier, with stronger sound. Push the fear as far as possible **without gore**: no blood, no wounds, no body horror. Those rules keep the videos ad-friendly and out of YouTube's "off-putting content" category.

**Scarier ghost design and motion**
- Make the ghost unnatural: too tall, limbs too long, head tilted at a wrong angle, glowing or pale eyes, a face mostly hidden or seen only for a split second.
- It moves wrong:
  - jerky "stop-motion" steps (skip frames)
  - it is suddenly closer each time the camera cuts back
  - a slow head turn toward the camera
  - a teleport with a glitch flicker
- Use at least **one false scare and one real jump scare per part**. The real one is a fast zoom to the ghost's face, a white or red flash for 2–3 frames, camera shake and a loud hit.
- Give the viewer more information than the hero: let them see the ghost in the background before the character does. A shape in the window, a figure behind a tree.
- Make it darker overall: deeper shadows, heavy vignette, flickering light sources, fog in front of the camera.

**Stronger sound (use `toolkit/sfx.py`)**
- Every build-up has a beat under it: `pulse_beat()` (drums that speed up) plus `heartbeat_accel()`.
- Right before the scare: `riser()`, then 0.3–0.5 s of **total silence**. Duck the drone too.
- On the scare: `braam()` + `sub_drop()` + `glitch()` + `dissonant_strings()`, loud. This is the loudest moment of the video, about 3 dB above the narration.
- **Dog howling in the background (Nova's request, 2026-11-24):** every part has distant dogs howling, from `dog_howl()` / `dog_pack()` in `toolkit/sfx.py`. Use `dog_pack(distance=0.7)` near the start (the "something is coming" signal), single far howls (`dog_howl(distance=0.6-0.8)`) every 15-20 s under the build-ups, and STOP the dogs suddenly right before a scare (sudden silence = the ghost is close). Keep them under the narration.
- Use `reverse_whisper()` for creepy moments. Keep a low drone with wind under everything, and nothing completely quiet except the pre-scare silence.
- The narration stays clear: duck the music under the voice, but not under the scare hits.

## 2c. Horror colour grade: red and deep black (Nova's request, 2026-11-24)

- **Paint every scene in a horror palette from the start.**
  - Near-black backgrounds (#050203 to #1a0508).
  - Blood-red and crimson light sources: lanterns, moon, glowing eyes, neon, candle glow.
  - Pale bone-white for the ghost.
  - Only small touches of other colours. Avoid big teal, green or blue areas unless the legend needs them, and then keep them dark.
- **Light like a horror film.** Use one strong red key light, hard shadows, rim light on the ghost, and a red moon or red sky glow when it fits.
- **After muxing each part, ALWAYS run the grade:** `bash ../../toolkit/grade.sh epNN_partN_raw.mp4 epNN_partN.mp4`. It crushes the blacks, pushes red into the shadows, pulls other colours down, and adds a vignette and film grain. Make the covers from graded frames too.
- **Check that the subtitles and the PART badge stay readable after the grade.** Phones are watched in daylight, so dark is good but invisible is not. Compare average brightness before and after: a graded frame should keep at least ~55% of the original. If a scene goes nearly black, paint it brighter instead of skipping the grade.

## 2d. Art style: "2.1D" — flat but creative (Nova's choice, 2026-11-24)
Nova prefers FLAT colours, but with more creativity and depth. Reference: `toolkit/demo25_myanmar.py` and `toolkit/depth.py`; see the test frame by running `STYLE=flat21 python3 toolkit/demo25_myanmar.py still test.png`.
- Characters and props: draw a mask, then `inflate_shade(mask, base_colour, radius=..., rim=(255,55,40))` from `toolkit/depth.py`, with `os.environ["STYLE"]="flat21"` set at the top of the render script. That gives flat colour + ONE shadow side + a thin red edge light. No glossy/3D look.
- Depth: 4–6 layers (sky, far, mid, ground, near, blurred foreground). Blur far layers a little with `dof()`, blur the foreground strongly (~9). Fog bands BETWEEN layers, not only at the bottom.
- Camera: every scene moves — slow push-in (zoom 1.0→1.08) plus parallax (layers shift by camera × depth: far 0.15, mid 0.35–0.6, ghost 0.8, near 1.0, foreground 1.6).
- Light: a strong light source in frame (moon, lantern, candle) with a soft glow; `god_rays()` through trees/windows where it fits; floating embers/dust with `bokeh_particles()`.
- Ghost: floats/sways, glowing eyes that pulse, a soft red aura behind the body; hair over the face. Still no gore.
- **Country flag at the start (Nova, 2026-11-24):** the hook (Part 1) and recap (Part 2) show the country's flag, waving, above the "GHOSTS OF ASIA / COUNTRY / PART" header, so viewers instantly know the country. Draw it in code (see `sg_flag()` / `flag_layer()` in episodes/ep08-singapore-tekong/scenes_ep8.py). Also show it on the explain and outro cards.
- Show one frame per scene before the full render and fix anything flat, empty or cluttered.

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
  - Then one teaser line ("Part 2 is up now on our channel 👻"), plus one true fact about the legend.
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
| 08 | Singapore | **Pulau Tekong: the lost recruit of Charlie Company + the bunk with a 3rd door.** Nova's #1 priority: "most scary, best story, best sound, best animation, best grade". See the brief in LOG.md (2026-11-24 03:50). |
| 09 | Cambodia | Ap (floating head with glowing organs below; show only a glowing head and a trail of light, never gore). Requested by Nova. |
| 10 | India | Chudail |
| 11 | Vietnam | Ma Da (water ghost) |
| 12 | Korea | Cheonyeo gwishin |
| 13 | Japan | Hanako-san of the toilet |
| 14 | Philippines | Tikbalang |
| 15 | Laos | Phi Pop |
| 16 | Indonesia | Kuntilanak (woman in white in a tree, laughing; frangipani smell; a nail in the neck in the legend - show NO nail/wound) |
| 17 | Thailand | Mae Nak of Phra Khanong (the ghost wife; the long arm reaching for a dropped lime) |
| 18 | Taiwan | Mosien / the little girl in red (the mountain spirit that leads hikers astray) |
| 19 | Malaysia | Toyol (the small child spirit that steals money; a jar, a bowl of marbles or a mirror as the trick) |
| 20 | Japan | Yuki-onna (the snow woman; a mountain hut in a blizzard) |
| 21 | Sri Lanka | Mohini (the woman in white with a baby on a lonely road) |
| 22 | Malaysia | Hantu Tinggi (the too-tall ghost; it grows taller the more you look up) |

(Rows 16-22 added 2026-11-26 by the run that made ep15, from the ideas in LOG.md; Nova can reorder them.)
