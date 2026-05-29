"""Acceptance tests for the pin/unpin feature."""


def _seed(app, n=2):
    app.notes.clear()
    for i in range(n):
        app.notes.append({"title": f"Note {i}", "body": f"Body {i}", "tags": []})


# ---------------------------------------------------------------------------
# Route behaviour
# ---------------------------------------------------------------------------

def test_pin_redirects(client, app):
    _seed(app, 1)
    r = client.post("/notes/0/pin")
    assert r.status_code in (302, 303)


def test_pin_get_returns_405(client, app):
    _seed(app, 1)
    r = client.get("/notes/0/pin")
    assert r.status_code == 405


def test_pin_nonexistent_returns_404(client, app):
    _seed(app, 1)
    r = client.post("/notes/99/pin")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# State toggling
# ---------------------------------------------------------------------------

def test_pin_sets_is_pinned_true(client, app):
    _seed(app, 1)
    client.post("/notes/0/pin")
    assert app.notes[0]["is_pinned"] is True


def test_pin_twice_toggles_back_to_unpinned(client, app):
    _seed(app, 1)
    client.post("/notes/0/pin")
    client.post("/notes/0/pin")
    assert app.notes[0]["is_pinned"] is False


def test_new_note_starts_unpinned(client, app):
    app.notes.clear()
    client.post("/notes/new", data={"title": "T", "body": "B"})
    assert app.notes[0].get("is_pinned") is False


# ---------------------------------------------------------------------------
# Home page rendering
# ---------------------------------------------------------------------------

def test_pinned_section_appears_when_note_pinned(client, app):
    _seed(app, 1)
    client.post("/notes/0/pin")
    r = client.get("/")
    assert b"Pinned Notes" in r.data


def test_pinned_section_absent_when_no_pinned_notes(client, app):
    _seed(app, 2)
    r = client.get("/")
    assert b"Pinned Notes" not in r.data


def test_pinned_note_appears_before_unpinned_note(client, app):
    _seed(app, 2)
    client.post("/notes/1/pin")  # pin Note 1
    r = client.get("/")
    html = r.data.decode()
    assert html.index("Note 1") < html.index("Note 0")


def test_home_has_pin_button_for_each_note(client, app):
    _seed(app, 2)
    r = client.get("/")
    html = r.data.decode()
    assert html.count("/pin") == 2


def test_existing_notes_without_is_pinned_still_render(client, app):
    app.notes.clear()
    app.notes.append({"title": "Legacy", "body": "Old note", "tags": []})
    r = client.get("/")
    assert r.status_code == 200
    assert b"Legacy" in r.data
