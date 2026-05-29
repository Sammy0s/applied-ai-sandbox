"""Acceptance tests for the character count feature."""


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

def test_char_count_stored_on_create(client, app):
    app.notes.clear()
    client.post("/notes/new", data={"title": "T", "body": "hello"})
    assert app.notes[0]["char_count"] == 5


def test_char_count_reflects_stripped_body(client, app):
    """Server strips body before saving; count must reflect the stripped length."""
    app.notes.clear()
    client.post("/notes/new", data={"title": "T", "body": "  hello  "})
    assert app.notes[0]["char_count"] == 5


def test_char_count_for_longer_body(client, app):
    app.notes.clear()
    body = "The quick brown fox"
    client.post("/notes/new", data={"title": "T", "body": body})
    assert app.notes[0]["char_count"] == len(body)


# ---------------------------------------------------------------------------
# Validation edge cases — notes with empty/whitespace body are rejected
# ---------------------------------------------------------------------------

def test_whitespace_only_body_rejected(client, app):
    """Whitespace-only body strips to '' and triggers validation; no note created."""
    app.notes.clear()
    r = client.post("/notes/new", data={"title": "T", "body": "   "})
    assert r.status_code == 200  # re-renders form, not a redirect
    assert len(app.notes) == 0


# ---------------------------------------------------------------------------
# Home page rendering
# ---------------------------------------------------------------------------

def test_home_renders_char_count_for_unpinned_note(client, app):
    app.notes.clear()
    app.notes.append({"title": "T", "body": "hello", "tags": [], "is_pinned": False, "char_count": 5})
    r = client.get("/")
    assert b"5 chars" in r.data


def test_home_renders_char_count_for_pinned_note(client, app):
    app.notes.clear()
    app.notes.append({"title": "T", "body": "hello", "tags": [], "is_pinned": True, "char_count": 5})
    r = client.get("/")
    assert b"5 chars" in r.data
