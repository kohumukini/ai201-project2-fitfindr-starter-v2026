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

import config
import trace
from tools import suggest_outfit, create_fit_card
from generate import ModelUnavailable, generate
from mcp_client import call_tool
from pydantic import BaseModel
from typing import Literal

class ClothingInfo(BaseModel): 
    description: str = ""
    size: str | None = None
    max_price: float | None = None


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
        "wardrobe_only": False,      # True when no item was requested: style the wardrobe alone
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── query parsing ─────────────────────────────────────────────────────────────
def _parse_query(query: str) -> dict:
    """
    Split a plain-language request into the three inputs search_listings takes.

    Returns a dict with `description` (str, possibly empty), `size` (str or
    None) and `max_price` (float or None).
    """
    # The size vocabulary below mirrors the `size` field in data/listings.json.
    # search_listings matches sizes by exact token, so "medium" or "30" would
    # silently return nothing — the parser has to emit the listing's own form.
    system_instruction = """
        You are a search query parser for a clothing marketplace.
        Extract three things from the user's request:
        - description: the core item (cleaned of any price limit or size).
        - size: the clothing size if specified, otherwise null.
        - max_price: the maximum price as a number, otherwise null.

        Write size exactly as the marketplace lists it:
        - Tops and outerwear: S, M, L or XL. Convert words: small -> S,
          medium -> M, large -> L, extra large -> XL.
        - Shoes: "US 7", "US 8", "US 8.5" or "US 9". A bare shoe size like
          "size 9" -> "US 9".
        - Bottoms (waist): W27 to W32, e.g. "waist 30" or "30 inch" -> "W30".
        - One Size items: "One Size".
        If the requested size is not one of these (for example XXS), return it
        uppercased as typed. Never guess a size the user did not state.
        
        If the request names no clothing item (it is not clothing related, or
        only asks for outfit ideas), return an empty description.
    """

    model_response = generate(
        query,
        system_instruction,
        temperature=0.0,
        cache=True,
        response_schema=ClothingInfo,
    )
    return ClothingInfo.model_validate_json(model_response).model_dump()


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


# ── loop steps ────────────────────────────────────────────────────────────────
# Each step reads what it needs from the session, calls one tool, records the
# result back on the session, and logs one trace line.

def _step_parse(session: dict) -> None:
    session["parsed"] = _parse_query(session["query"])
    trace.step("parse_query", inputs=session["query"], returned=str(session["parsed"]))


def _step_search(session: dict) -> None:
    parsed = session["parsed"]

    # The branch: no clothing item in the request means there is nothing to
    # search for. Skip search and let suggest_outfit style the wardrobe alone,
    # or give general advice if the wardrobe is empty too.
    if not parsed["description"]:
        trace.step(
            "search_listings",
            inputs="description=''",
            returned=[],
            note="branch: no item requested, suggesting an outfit without a listing",
        )
        session["wardrobe_only"] = True
        return

    results = call_tool("search_listings", {
        "description": parsed["description"], 
        "size": parsed["size"], 
        "max_price": parsed["max_price"]
    })
    session["search_results"] = results

    # The branch: an empty result ends the run before suggest_outfit.
    trace.step(
        "search_listings",
        inputs=(
            f"description={parsed['description']!r}, "
            f"size={parsed['size']!r}, max_price={parsed['max_price']!r}"
        ),
        returned=results,
        note="branch: results found, selecting the first" if results
        else "branch: empty, stopping before suggest_outfit",
    )
    if results:
        session["selected_item"] = results[0]
    else:
        session["error"] = _no_results_message(parsed)


def _step_suggest(session: dict) -> None:
    item, wardrobe = session["selected_item"], session["wardrobe"]
    session["outfit_suggestion"] = suggest_outfit(item, wardrobe)
    trace.step(
        "suggest_outfit",
        inputs=(
            f"item={item['title'] if item else None!r}, "
            f"wardrobe_items={len((wardrobe or {}).get('items') or [])}"
        ),
        returned=session["outfit_suggestion"],
    )


def _step_fit_card(session: dict) -> None:
    item, outfit = session["selected_item"], session["outfit_suggestion"]
    session["fit_card"] = create_fit_card(outfit, item)
    trace.step(
        "create_fit_card",
        inputs=f"item={item['title']!r}, outfit={outfit!r}",
        returned=session["fit_card"],
    )


def _next_step(session: dict):
    """Pick the next step from what the session already holds."""
    if not session["parsed"]:
        return _step_parse
    if session["selected_item"] is None and not session["wardrobe_only"]:
        return _step_search
    if session["outfit_suggestion"] is None:
        return _step_suggest
    return _step_fit_card


def _is_done(session: dict) -> bool:
    """A wardrobe-only run has no item to caption, so it ends at the outfit."""
    if session["error"] is not None or session["fit_card"] is not None:
        return True
    return session["wardrobe_only"] and session["outfit_suggestion"] is not None


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

    Wardrobe-only rule: if the query names no clothing item but the wardrobe
    has items, skip the search, call suggest_outfit with item=None, and stop.
    There is no item to caption, so session["fit_card"] stays None and
    session["wardrobe_only"] is True.
    """
    trace.start_trace()
    session = new_session(query, wardrobe)

    try:
        iterations = 0
        while not _is_done(session):
            iterations += 1
            trace.check_iterations(iterations)
            _next_step(session)(session)

    except ModelUnavailable as exc:
        session["error"] = f"The model couldn't be reached, so the run stopped early. {exc}"
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

    if session["wardrobe_only"]:
        print(f"  outfit (wardrobe only): {session['outfit_suggestion']}")
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
