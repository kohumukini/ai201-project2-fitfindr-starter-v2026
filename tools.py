"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

# Words that carry no search signal. Without this, "a" or "for" in a query
# would match nearly every description and swamp the real keywords.
_STOPWORDS = frozenset(
    "a an and the for in of on or to with under over below above than "
    "me my i want need looking find some any".split()
)


# A query word that names a garment type restricts results to that category.
# Keys are post-_tokenize forms (plural "s" already stripped).
_CATEGORY_WORDS = {
    "bottom": "bottoms", "pant": "bottoms", "trouser": "bottoms",
    "jean": "bottoms", "short": "bottoms", "skirt": "bottoms",
    "top": "tops", "tee": "tops", "shirt": "tops", "hoodie": "tops",
    "jacket": "outerwear", "coat": "outerwear",
    "shoe": "shoes", "boot": "shoes", "sneaker": "shoes",
}

# Fit words that rarely appear verbatim in listings, mapped to words that do.
_SYNONYMS = {
    "relaxed": {"relaxed", "baggy", "wide", "oversized", "loose", "straight"},
    "fitted": {"fitted", "slim", "tight", "skinny"},
}


def _tokenize(text: str) -> set[str]:
    """
    Lowercase `text` and split it into a set of word tokens.

    Splitting on anything that isn't a letter or digit handles "S/M",
    "W30 L30", "XL (oversized)" and "Black/Red" uniformly, so sizes and
    keywords share one code path. A set gives O(1) membership tests and
    ignores repeated words. A trailing "s" is stripped from longer words so
    "tees" matches "tee" and "jeans" matches "jean" — applied to both the
    query and the listing, so the two sides always agree.
    """
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {
        (w[:-1] if len(w) > 3 and w.endswith("s") else w)
        for w in words
        if w not in _STOPWORDS
    }


def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
    platform: str | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.
        platform:    preferred platform (e.g. "poshmark"). A ranking boost, not
                     a filter — other platforms can still be returned.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    listings = load_listings()

    query_terms = _tokenize(description)
    size_tokens = _tokenize(size) if size else set()

    if not query_terms:
        return []

    categories = {_CATEGORY_WORDS[t] for t in query_terms if t in _CATEGORY_WORDS}

    scored = []
    for listing in listings:

        if max_price is not None and listing["price"] > max_price:
            continue
        if categories and listing["category"] not in categories:
            continue
        if size_tokens and not size_tokens <= _tokenize(listing["size"]):
            continue

        # 3. Score what's left by keyword overlap with `description`.
        #    Terms found in the title, tags, category, colors or brand are
        #    strong signals (2 points); a term found only in the free-text
        #    description is weaker (1 point). That puts "vintage graphic tee"
        #    ahead of a listing that merely mentions a tee in passing.
        #    `brand` is None for most listings, so `or ""` guards the join.
        key_terms = _tokenize(
            " ".join(
                [
                    listing["title"],
                    listing["category"],
                    " ".join(listing["style_tags"]),
                    " ".join(listing["colors"]),
                    listing["brand"] or "",
                ]
            )
        )
        desc_terms = _tokenize(listing["description"])
        hits = []
        for term in query_terms:
            options = _SYNONYMS.get(term, {term})
            hits.append(2 if options & key_terms else 1 if options & desc_terms else 0)

        # Coverage (share of query terms matched) dominates, so a listing that
        # matches "black" AND "relaxed" beats one matching only "black".
        score = 10 * sum(1 for h in hits if h) / len(hits) + sum(hits)

        # 4. Drop anything scoring zero.
        #    A listing that passed the filters but shares no words with the
        #    query is not a match; returning it would make the search look
        #    random and would stop the loop's empty-result branch from firing.
        if score > 0:
            if platform and listing["platform"].lower() == platform.lower():
                score += 1  # soft preference; a better content match still wins
            scored.append((score, listing))

    # 5. Sort by score, highest first, and return the listing dicts —
    #    at most config.SEARCH_RESULT_LIMIT of them.
    #    Cheaper price breaks ties (a thrift shopper's natural preference) and
    #    makes the order deterministic, which matters for repeatable evals.
    scored.sort(key=lambda pair: (-pair[0], pair[1]["price"]))
    return [listing for _, listing in scored[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def _describe_listing(item: dict) -> str:
    brand = item.get("brand")
    lines = [
        f"Title: {item['title']}",
        f"Category: {item['category']}",
        f"Colors: {', '.join(item.get('colors') or [])}",
        f"Style tags: {', '.join(item.get('style_tags') or [])}",
        f"Description: {item['description']}",
    ]
    if brand:
        lines.insert(1, f"Brand: {brand}")
    return "\n".join(lines)


def _format_wardrobe(items: list[dict]) -> str:
    rows = []
    for piece in items:
        row = f"- {piece['name']} ({piece['category']}; {', '.join(piece.get('colors') or [])}"
        if piece.get("style_tags"):
            row += f"; {', '.join(piece['style_tags'])}"
        row += ")"
        if piece.get("notes"):
            row += f" — {piece['notes']}"
        rows.append(row)
    return "\n".join(rows)


def suggest_outfit(new_item: dict | None, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering — or None
                  when the user didn't ask for a specific piece. With None, the
                  outfits are built from the wardrobe alone.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.
        With neither an item nor wardrobe items, return general styling
        advice, the same as the empty-wardrobe case.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    items = (wardrobe or {}).get("items") or []

    if new_item is None:
        if not items:
            system = (
                "You are a thrift-store stylist. Give concrete, practical "
                "styling advice in plain text, with no preamble."
            )
            prompt = (
                "I haven't picked out a piece to buy and I haven't told you "
                "what's in my wardrobe. Give me general styling advice: one "
                "or two versatile outfits made of easy-to-find secondhand "
                "pieces (for example 'straight-leg jeans' or 'white "
                "sneakers'), and a tip or two for thrifting them. Keep it "
                "under 150 words."
            )
        else:
            system = (
                "You are a thrift-store stylist. Only combine items from the "
                "user's wardrobe list, and name them exactly as listed. "
                "Never invent pieces the user doesn't own. Plain text, no "
                "preamble."
            )
            prompt = (
                "My wardrobe:\n"
                f"{_format_wardrobe(items)}\n\n"
                "Suggest one or two outfits I can put together from these "
                "pieces alone. Say briefly why each works. Keep it under 200 "
                "words."
            )
        response = generate(prompt, system=system).strip()
        return response or "No styling suggestion came back. Try again in a moment."

    item_block = _describe_listing(new_item)

    if not items:
        system = (
            "You are a thrift-store stylist. Give concrete, practical styling "
            "advice in plain text, with no preamble."
        )
        prompt = (
            "I'm thinking of buying this secondhand piece:\n\n"
            f"{item_block}\n\n"
            "I haven't told you what's in my wardrobe. Suggest one or two "
            "outfits built around it, describing the kinds of pieces that "
            "would pair well (for example 'straight-leg jeans' or 'white "
            "sneakers'). Keep it under 150 words."
        )
    else:
        system = (
            "You are a thrift-store stylist. Only combine the new piece with "
            "items from the user's wardrobe list, and name those items "
            "exactly as listed. Never invent pieces the user doesn't own. "
            "Plain text, no preamble."
        )
        prompt = (
            "I'm thinking of buying this secondhand piece:\n\n"
            f"{item_block}\n\n"
            "My wardrobe:\n"
            f"{_format_wardrobe(items)}\n\n"
            "Suggest one or two outfits that combine the new piece with "
            "items I already own. Say briefly why each works. Keep it under "
            "200 words."
        )

    response = generate(prompt, system=system).strip()
    if not response:
        return (
            f"No styling suggestion came back for {new_item['title']}. "
            "Try again in a moment."
        )
    return response


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not isinstance(outfit, str) or not outfit.strip():
        return (
            "No outfit was provided, so there's nothing to write a fit card "
            "about. Run suggest_outfit first and pass its result in."
        )

    system = (
        "You write short social-media captions for thrift finds. Sound like a "
        "real person posting, not a product listing. Plain text only."
    )
    prompt = (
        "Write a caption of two to four sentences about this thrift find.\n\n"
        f"Item: {new_item['title']}\n"
        f"Price: ${new_item['price']:.2f}\n"
        f"Platform: {new_item['platform']}\n"
        f"Outfit it's styled in: {outfit.strip()}\n\n"
        "Rules: mention the item, the price and the platform once each; be "
        "specific about the vibe; no more than one emoji; at most two "
        "hashtags. The user is the buyer, not the seller"
    )

    response = generate(prompt, system=system).strip()
    if not response:
        return (
            f"No caption came back for {new_item['title']}. Try again in a "
            "moment."
        )
    return response
