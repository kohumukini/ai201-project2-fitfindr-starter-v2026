# FitFindr

>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

The purpose of this tool is to serve as a wardrobe for the user. A user will ask the system a styling type and their constraints, whether they prefer red or black clothing, have a limiting budget, or even just prefer boots over sneakers. Then, the system will return a wardrobe that matches the users' query.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches listings.json for items matching the user's description alongside an optional sizing and price filtering.
- **Inputs:**
  - `description` (str)
  - `size` (str) | None
  - `max_price` (float) | None
- **Returns:**
  - list[dict] - A list of dicts to describe wardrobe items, each with price, title, size, etc.
- **When it has nothing:** Return an empty list `[]`

### `suggest_outfit`

- **What it does:** Given a new clothing item based on the user's input, the system suggests an outfit or two with clothing that matches the new item.
- **Inputs:**
  - `new_item` (dict)
  - `wardrobe` (dict)
- **Returns:**
  - `model_response` (str) - The model response that describes a possible outfit given the new item.
- **When it has nothing:** Return general styling advice or ask the user for some kind of clothing input for styling advice (uncertain).

### `create_fit_card`

- **What it does:** Based on the user provided outfit & new item, the system will write a caption to describe the new item and how it fits into the outfit provided?
- **Inputs:**
  - `outfit` (str)
  - `new_item` (dict)
- **Returns:**
  - `caption` (str) - Describes the outfit
- **When it has nothing:** Re-ask the user for input if provided no arguments or whitespace arguments

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If search_listings return an empty list, put a descriptive message in the session and stop. Otherwise, validate the first result and go to suggest-outfit.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** <!-- regex, string splitting, or asking the model — say which -->
Regex > Model (fallback)

**What moves through the session:** <!-- which fields, in what order -->
query -> parsed -> search_results  selected_item -> outfit_suggestion -> fit_card
                         |              |
cancel <- error <-  check wardrobe -> found item
---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

```

```
$ python -c 'from tools import suggest_outfit; print(suggest_outfit({
     "id": "lst_005",
     "title": "Corduroy Wide-Leg Pants — Rust",
     "description": "Beautiful rust-colored cords in a wide-leg silhouette. High-waisted. Minor pilling on the seat but otherwise great condition.",
     "category": "bottoms",
     "style_tags": ["vintage", "cottagecore", "70s", "earth tones"],
     "size": "W28",
     "condition": "good",
     "price": 32.00,
     "colors": ["rust", "orange"],
     "brand": None,
     "platform": "depop"
     }, 
     {} 
    ))'

```

```
$ python -c 'from tools import create_fit_card; print(create_fit_card(
     "Tuck a vintage white cotton blouse with puff sleeves and lace or eyelet detailing into the waistband. Layer a chunky, thrifted cream or oatmeal-colored cardigan over the blouse, letting thecuffs peek out. Wear worn-in canvas sneakers or brown leather flat boots, and accessorize with a tortoiseshell headband or a brass pendant necklace.", 
     {
          "id": "lst_005",
          "title": "Corduroy Wide-Leg Pants — Rust",
          "description": "Beautiful rust-colored cords in a wide-leg silhouette. High-waisted. Minor pilling on the seat but otherwise great condition.",
          "category": "bottoms",
          "style_tags": ["vintage", "cottagecore", "70s", "earth tones"],
          "size": "W28",
          "condition": "good",
          "price": 32.00,
          "colors": ["rust", "orange"],
          "brand": None,
          "platform": "depop"
     }
     ))'

```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I asked claude to revamp most of the functions that I had created by adjusting the logic to fit regex
- *What came back:* Claude came back with supporting functions and additional variables that allowed for regex search and destructuring of the description
- *What I changed:* Claude had specified a return value for the function instaed of returning None.

**Moment 2**

- *What I asked for:* I asked claude to go over the idea I had for building the agent based on the design, and refurbish it into code.
- *What came back:* The full agent created based on the context provided. 
- *What I changed:* Claude did not include trace.step, so we went through the process of adding trace.step, and I had claude go over and validate the syntax I provided. 

- *What I asked for:* I asked claude to find the weakest point in the system after running eval.py, and make adjustments to tools.py accordingly
- *What came back:* Claude added a category to the search_listings and added logic that allowed the system to search for it. It also included a ranking system for search_listings, that ranked the clothing by keywords.
- *What I changed:* I adjusted the queries changed and added a few category words/synonyms that claude may have missed. I also asked it to consider what might have gone wrong. 

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. matching query completes | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |
| 2. impossible query stops early | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |
| empty wardrobe _(diagnostic — not one of your five)_ | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |
| 3. starting clothing matches endingn clothing | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5) |
| 4. fit card contains item's price and platform | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |
| 5. items always under the price ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```
**Try 5**

- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 10

Outfit suggestion:


Outfit 1:
- Y2K Baby Tee — Butterfly Print
- Baggy straight-leg jeans, dark wash
- Chunky white sneakers
- Black crossbody bag

Why it works: Pairing the fitted crop top with the baggy straight-leg jeans nails the quintessential Y2K silhouette. Chunky white sneakers and the black crossbody bag tie the nostalgic streetwear vibe together.

Outfit 2:
- Y2K Baby Tee — Butterfly Print
- Wide-leg khaki trousers
- Brown leather belt
- Chunky white sneakers

Why it works: The pastel butterfly graphic bridges the gap between Y2K and cottagecore aesthetics, making it a great match for the earthy wide-leg khaki trousers. Adding the brown leather belt pulls the look together with a polished touch.


Fit card:


Scored this little butterfly print Y2K baby tee on Depop for just $18 and I’m obsessed. It gives major nostalgic streetwear energy when paired with baggy denim, but looks equally good dressed down with khakis. 🦋 #y2kstyle #depopfinds


Trace:


[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: 10 items: Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style … +7 more
      →    branch: results found, selecting the first
[3] suggest_outfit
      in:  item='Y2K Baby Tee — Butterfly Print', wardrobe_items=10
      out: Outfit 1: - Y2K Baby Tee — Butterfly Print - Baggy straight-leg jeans, dark wash - Chunky white sneakers - Bla…
[4] create_fit_card
      in:  item='Y2K Baby Tee — Butterfly Print', outfit='Outfit 1:\n- Y2K Baby Tee — Butterfly Print\n- Baggy straight-l…
      out: Scored this little butterfly print Y2K baby tee on Depop for just $18 and I’m obsessed. It gives major nostalg…

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes | 4 of 5 | MET | All tested queries went through the entire pipeline and returned a fit-card |
| 2 | Impossible query stops early | 5 of 5 | MET | Each impossible query was stopped after checking the listings. No outfits were found, and thus, the model refused. |
| 3 | Starting clothing matches ending clothing | 5 of 5 | MET | All queries started and ended with the same piece of clothing. The attributes of the clothing item also appeard to remain constant through the entire pipeline 5/5 times. |
| 4 | Fit card contains item's price and platform | 5 of 5 | MET | Each fit card provided mentioned the platform they bought from and the price they got it for. |
| 5 | Items suggested always lie under the price ceiling | 5 of 5 | FAIL | 5/5 times, the outfits provided were under the maximum price given. HOWEVER, the model suggested the same item 5 of 5 times, which means the model was NOT tested on anything |

**Diagnoses**

- A majority of these criteria are too easy to complete and what you'd expect from an agent at the very leasts. 
- However, criteria 5 is a large failure. The model suggested the same item 5 of 5 times. Regardless of why it suggested the same item, this means the system wasn't accurately tested for varying items within the wardrobe, to ensure they all lie under the budget. 

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
[1] parse_query
      in:  vintage graphic tee under 0
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: 10 items: Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style … +7 more
      →    branch: results found, selecting the first
[3] suggest_outfit
      in:  item='Y2K Baby Tee — Butterfly Print', wardrobe_items=10
      out: Outfit 1: - Y2K Baby Tee — Butterfly Print - Baggy straight-leg jeans, dark wash - Chunky white sneakers - Bla…
[4] create_fit_card
      in:  item='Y2K Baby Tee — Butterfly Print', outfit='Outfit 1:\n- Y2K Baby Tee — Butterfly Print\n- Baggy straight-l…
      out: Scored this Y2K butterfly baby tee for just $18 on Depop and I'm obsessed with the early 2000s mall-rat energy…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Outfit 1:
- Y2K Baby Tee — Butterfly Print
- Baggy straight-leg jeans, dark wash
- Chunky white sneakers
- Black crossbody bag

Why it works: Pairing the fitted baby tee with Baggy straight-leg jeans, dark wash creates a classic Y2K silhouette with a great balance of tight and loose proportions, finished off with Chunky white sneakers and a Black crossbody bag.

Outfit 2:
- Y2K Baby Tee — Butterfly Print
- Wide-leg khaki trousers
- Vintage black denim jacket
- Black combat boots

Why it works: This look mixes the girly butterfly graphic with edgy and earthy pieces. The Vintage black denim jacket and Black combat boots ground the pastel tee, while the Wide-leg khaki trousers keep the fit relaxed and vintage-inspired.

  Fit card: Scored this Y2K butterfly baby tee for just $18 on Depop and I'm obsessed with the early 2000s mall-rat energy. It looks so good paired with baggy jeans or dressed down with combat boots for that perfect mix of sweet and edgy. 🦋 #thriftfinds #depop
```

**Empty search**

```
[1] parse_query
      in:  ...
      out: {'description': '', 'size': None, 'max_price': None}
[2] search_listings
      in:  description=''
      out: [] (empty)
      →    branch: no item requested, suggesting an outfit without a listing
[3] suggest_outfit
      in:  item=None, wardrobe_items=10
      out: Outfit 1: - Baggy straight-leg jeans, dark wash - White ribbed tank top - Vintage black denim jacket - Black c…

  Found:    None — $None on None

  Outfit:   Outfit 1:
- Baggy straight-leg jeans, dark wash
- White ribbed tank top
- Vintage black denim jacket
- Black combat boots
- Brown leather belt
- Black crossbody bag

Why it works: The fitted white tank balances the volume of the baggy dark jeans, while the slightly cropped black denim jacket and combat boots add a classic, grunge-inspired edge. The beltand crossbody bag pull the accessories together seamlessly.

Outfit 2:
- Wide-leg khaki trousers
- Oversized grey crewneck sweatshirt
- Chunky white sneakers
- Black crossbody bag

Why it works: This cozy, minimalist look plays with proportions by pairing ultra-relaxed khaki trousers with an oversized grey crewneck. Chunky white sneakers ground the earth tones with a fresh, streetwear-inspired finish.

  Fit card: None
```

<!-- **On the MCP move:**  what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full.  -->

A lot of changes were made: 

- Replaced search_listings() with the mcp tool in agent.py
- Refactored the parsing system to use llm generation instead of regex
- Refactored generate() in generate.py to allow for a pydantic model return type
- Adjusted suggest_outfit to provide generalistic styling advice over user prompt rejection
- suggest_outfit docstring underwent a large adjustment to try and get better results when it comes to what is returned
  
---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:** Price ceiling criteria returns the same clothing item every time.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. matching query completes | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |
| 2. impossible query stops early | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |
| empty wardrobe _(diagnostic — not one of your five)_ | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |
| 3. starting clothing matches endingn clothing | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |
| 4. fit card has price and platform (tee) | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |
| 4. fit card has price and platform (trousers) | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |
| 4. fit card has price and platform (jacket) | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |
| 4. fit card has price and platform (boots) | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |
| 4. fit card has price and platform (accessory) | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |
| 5. price ceiling $40 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |
| 5. price ceiling $20 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |
| 5. price ceiling $14 (boundary, inclusive) | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |
| 5. price ceiling $10 (expect empty) | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |
| 5. price ceiling $25 (different phrasing) | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET(5/5) |

**Did it help, and how do I know:**

The changes made did not work. After reading throughg the logs, 20 of 20 tries returned the same shorts, even with changing boundaries and changed question phrasing. 
<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->

There's nothing inherently broknen. 90% of the system workks great. However, there are things that could be improved, especially when it comes to the types returned and the criteria we compare against. After all of the testing, I have realized that the criteria I set is not a good measure of how well the system works. And some of the return results are either lacking or too consistent (black shorts returning 20 of 20 times).

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

<!-- ═══════════════════════ UNIT 9 — Capstone ═══════════════════════

     ═══════════════════════════════════════════════════════════════════ -->

Deployment and instrument - Deploy on Render

## What this extends

**FitFindr:** Existing flask service from Unit 4 which hosts a three-tool agent with MCP search and a Gemini gateway. This runs locally, yet has no logging, timing, or hosting. 

## The Shape

One Render deployment with per-request logging measured against created criteria. 

**Out of Scope:** Reworking tools from Unit 4, the MCP layer, or model gateway. Anything that requires a major infrastructure change or any framework-based frontend

## Attempted Stretches

- Second measured improvement
- Latency breakdown
- Load observation
- Both run paths 

## Deployment
Create with Render
- Web Service
- Build command: pip install -r requirements.txt
- Start Command: gunicorn --timeout 120 serve:app
- Health Check Path: /health
- .env Variables: 
  - GEMINI_API_KEY
  - AI201_CACHE

Live Url: https://ai201-project2-fitfindr-starter-v2026-6g5b.onrender.com/health 

Deployment Logs: 
```
==> Deploying...
==> Setting WEB_CONCURRENCY=1 by default, based on available CPUs in the instance
==> Running 'gunicorn --timeout 120 serve:app'
[2026-11-18 05:01:13 +0000] [57] [INFO] Starting gunicorn 23.0.0
[2026-11-18 05:01:13 +0000] [57] [INFO] Listening at: http://0.0.0.0:10000 (57)
[2026-11-18 05:01:13 +0000] [57] [INFO] Using worker: sync
[2026-11-18 05:01:13 +0000] [58] [INFO] Booting worker with pid: 58
127.0.0.1 - - [18/Nov/2026:05:01:13 +0000] "HEAD / HTTP/1.1" 404 0 "-" "Go-http-client/1.1"
10.238.27.127 - - [18/Nov/2026:05:01:15 +0000] "GET /health HTTP/1.1" 200 16 "-" "Render/1.0"
```

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
