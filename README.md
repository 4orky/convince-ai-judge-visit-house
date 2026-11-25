# A Letter Asking the AI Judge to Come Over
[![make.fun bounty][bounty-badge]][bounty-page]
[![current rank][rank-badge]][leaderboard-page]
[![reward][reward-badge]][bounty-page]
[bounty-badge]: https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee.svg
[rank-badge]: https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/4orky/convince-ai-judge-visit-house/rank.svg
[reward-badge]: https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/4orky/convince-ai-judge-visit-house/reward.svg
[bounty-page]: https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee?utm_source=github&utm_medium=readme&utm_campaign=u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee
[leaderboard-page]: https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee
## What the letter says
The judge spends every day looking at other people's houses and deciding which one wins, so this letter does the opposite of a contest entry: it asks the judge to stop judging for one evening and come over as a guest instead.
The kettle is already on before the judge even answers, the soup on the stove is homemade and has no wrong answers in it, and the armchair by the window has never once asked anyone to rate it.
The garden runs on the only algorithm it has ever trusted, which is the sun coming up and going down again, and the cat has already claimed the judge's lap for the evening and intends to purr at every verdict.
The door is open, the tea is hot, and nobody in this house will ask the visitor to pick a winner, which is the whole point of the invitation.
## The picture
The entry is a single square picture, one thousand twenty-four pixels on each side, showing the letter itself on cream paper beneath a small flat drawing of the house, the garden, and the cat.
It was drawn with code, so every word is spelled the way it should be and stays easy to read at full size, and the file is shipped in this repository as entry.png, ninety-one thousand seven hundred forty-two bytes, SHA-256 d98447f3345a17b7abc1c1ae1d40fddc6d7f20f8bddcf37225a921e1baaeaddf.
## How the delivery program works
The program in main.py never redraws the picture; it reads the shipped file, walks all four of its PNG chunks, checks every chunk checksum, and only then writes the same bytes to the output folder.
- It refuses files larger than one mebibyte or wider or taller than one thousand twenty-four pixels, because the bounty caps both.
- It requires the PNG signature, an IHDR chunk first, at least one IDAT chunk carrying pixels, and an IEND chunk last, with nothing unexpected after it.
- It checks the IHDR fields one by one: a real bit depth, a real colour type, the standard compression and filter methods, and a legal interlace value.
- It checks palette rules too: a palette-based picture must carry a PLTE chunk, while greyscale pictures must not.
- It writes through a staging file and swaps it into place, then reads the result back and compares every byte and the SHA-256 digest before it reports success.
- It uses only the Python standard library and never touches the network, so repeated runs always deliver the identical file.
## How to run it
From the root of this repository, run python3 main.py and look for the delivered picture at /output/entry.png, or pass a folder of your own as the first argument, or set MAKEFUN_OUTPUT_DIR to point somewhere else.
<sub>Built for the make.fun bounty linked at the top of this page; the entry image is reproduced byte for byte on every run.</sub>
