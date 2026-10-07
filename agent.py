"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
import re
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── query parsing ─────────────────────────────────────────────────────────────

_PRICE_RE = re.compile(
    r"(?:\b(?:under|below|less than|up to|at most|no more than|max(?:imum)?)\s*)"
    r"\$?\s*(\d+(?:\.\d+)?)(?:\s*(?:dollars|bucks|usd))?"
    r"|\$\s*(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)

_SIZE_RE = re.compile(
    r"\bsize\s*:?\s+"
    r"(us\s*\d+(?:\.\d+)?"
    r"|w\d+(?:\s*l\d+)?"
    r"|\d+(?:\.\d+)?"
    r"|x{0,3}[sml](?:/x{0,3}[sml])?)\b",
    re.IGNORECASE,
)

_EDGE_WORDS = (
    r"(?:and|in|for|a|an|the|with|looking|find|want|need|i|i'm|im|me|my|some|"
    r"under|below|size)"
)
_EDGE_RE = re.compile(
    rf"^(?:{_EDGE_WORDS}\s+)+|(?:\s+{_EDGE_WORDS})+$", re.IGNORECASE
)


def _parse_query(query: str) -> dict:
    """
    Split a plain-language request into the three inputs search_listings takes.

    Returns a dict with `description` (str, possibly empty), `size` (str or
    None) and `max_price` (float or None).
    """
    text = query or ""

    max_price = None
    price_match = _PRICE_RE.search(text)
    if price_match:
        max_price = float(price_match.group(1) or price_match.group(2))
        text = text[: price_match.start()] + " " + text[price_match.end():]

    size = None
    size_match = _SIZE_RE.search(text)
    if size_match:
        size = re.sub(r"\s+", " ", size_match.group(1)).strip()
        text = text[: size_match.start()] + " " + text[size_match.end():]

    text = re.sub(r"[,;]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" .!?")
    description = _EDGE_RE.sub("", text).strip(" .!?")

    return {"description": description, "size": size, "max_price": max_price}


def _no_results_message(parsed: dict) -> str:
    if not parsed["description"]:
        return (
            "I couldn't find an item description in your request. Tell me what "
            "you're looking for, for example: 'vintage graphic tee under $30, "
            "size M'."
        )

    ideas = []
    if parsed["size"]:
        ideas.append(f"dropping the size filter ({parsed['size']})")
    if parsed["max_price"] is not None:
        ideas.append(f"raising your budget above ${parsed['max_price']:.2f}")
    ideas.append(f"trying different or fewer keywords than '{parsed['description']}'")

    return "No listings matched your request. Try " + ", or ".join(ideas) + "."


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    Branch rule: if search_listings returns an empty list, put a message in
    session["error"] and return before suggest_outfit is ever called.
    Otherwise take the first result and continue to suggest_outfit, then
    create_fit_card.
    """
    trace.start_trace()
    session = new_session(query, wardrobe)
    count = 0

    try:
        while session["fit_card"] is None:
            count += 1
            trace.check_iterations(count)

            if not session["parsed"]:
                session["parsed"] = _parse_query(query)
                trace.step("parse_query", inputs=query, returned=str(session["parsed"]))

            elif session["selected_item"] is None:
                parsed = session["parsed"]
                session["search_results"] = search_listings(
                    parsed["description"],
                    size=parsed["size"],
                    max_price=parsed["max_price"],
                )
                empty = not session["search_results"]
                trace.step(
                    "search_listings",
                    inputs=(
                        f"description={parsed['description']!r}, "
                        f"size={parsed['size']!r}, max_price={parsed['max_price']!r}"
                    ),
                    returned=session["search_results"],
                    note="branch: empty, stopping before suggest_outfit" if empty
                    else "branch: results found, selecting the first",
                )
                if empty:
                    session["error"] = _no_results_message(parsed)
                    return session
                session["selected_item"] = session["search_results"][0]

            elif session["outfit_suggestion"] is None:
                session["outfit_suggestion"] = suggest_outfit(
                    session["selected_item"], session["wardrobe"]
                )

                trace.step(
                    "suggest_outfit",
                    inputs=(
                        f"item={session['selected_item']['title']!r}, "
                        f"wardrobe_items={len((session['wardrobe'] or {}).get('items') or [])}"
                    ),
                    returned=session["outfit_suggestion"],
                )

            else:
                session["fit_card"] = create_fit_card(
                    session["outfit_suggestion"], session["selected_item"]
                )
                trace.step(
                    "create_fit_card",
                    inputs=(
                        f"item={session['selected_item']['title']!r}, "
                        f"outfit={session['outfit_suggestion']!r}"
                    ),
                    returned=session["fit_card"],
                )

    except ModelUnavailable as exc:
        session["error"] = (
            "The model couldn't be reached, so the run stopped early. "
            f"{exc}"
        )
        trace.step(
            "model_unavailable",
            returned=str(exc),
            note="stopping; later session fields stay None",
        )

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
