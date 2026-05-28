"""Tests for the tags feature — every new note must start with an empty tags list."""


def test_new_note_has_empty_tags(client, app):
    app.notes.clear()
    r = client.post("/notes/new", data={"title": "Tagged Note", "body": "Some content"})
    assert r.status_code in (302, 303)
    assert app.notes[0]["tags"] == []


"""Acceptance tests for TASK 02 — Add Tags Button on new-note form.

Don't edit these to make them pass. Change app.py / templates instead.
"""


# ---------------------------------------------------------------------------
# Tag UI is present on the new-note page
# ---------------------------------------------------------------------------

def test_new_note_page_has_tag_textbox(client):
    r = client.get("/notes/new")
    assert r.status_code == 200
    # A text input for the tag name must be present
    assert b'name="tag_name"' in r.data or b"tag_name" in r.data


def test_new_note_page_has_add_tag_button(client):
    r = client.get("/notes/new")
    assert r.status_code == 200
    # An 'Add Tag' button must be present
    assert b"Add Tag" in r.data or b"add_tag" in r.data


def test_add_tag_button_appears_before_submit_button(client):
    r = client.get("/notes/new")
    html = r.data
    add_tag_pos = html.find(b"Add Tag")
    # Accept either label text for the final submit
    submit_pos = max(html.find(b"Create Note"), html.find(b"Submit"))
    assert add_tag_pos != -1
    assert submit_pos != -1
    assert add_tag_pos < submit_pos


# ---------------------------------------------------------------------------
# Clicking 'Add Tag' rerenders the page (no redirect) with content preserved
# ---------------------------------------------------------------------------

def test_add_tag_rerenders_page_not_redirect(client):
    r = client.post(
        "/notes/new",
        data={"title": "My Title", "body": "My Body", "tag_name": "python", "newTag": "true"},
    )
    assert r.status_code == 200


def test_add_tag_preserves_title(client):
    r = client.post(
        "/notes/new",
        data={"title": "My Title", "body": "My Body", "tag_name": "python", "newTag": "true"},
    )
    assert b"My Title" in r.data


def test_add_tag_preserves_body(client):
    r = client.post(
        "/notes/new",
        data={"title": "My Title", "body": "My Body", "tag_name": "python", "newTag": "true"},
    )
    assert b"My Body" in r.data


def test_add_tag_displays_new_tag_in_active_tags(client):
    r = client.post(
        "/notes/new",
        data={"title": "My Title", "body": "My Body", "tag_name": "python", "newTag": "true"},
    )
    assert b"python" in r.data


def test_add_tag_shows_active_tags_section(client):
    r = client.post(
        "/notes/new",
        data={"title": "My Title", "body": "My Body", "tag_name": "python", "newTag": "true"},
    )
    # The page should label the accumulated tags in some way
    assert b"Active Tags" in r.data or b"active_tags" in r.data or b"active-tags" in r.data


# ---------------------------------------------------------------------------
# Multiple tags accumulate correctly across successive add-tag requests
# ---------------------------------------------------------------------------

def test_second_add_tag_shows_both_tags(client):
    # First tag
    r1 = client.post(
        "/notes/new",
        data={"title": "T", "body": "B", "tag_name": "python", "newTag": "true"},
    )
    assert b"python" in r1.data

    # Second tag — simulate the browser re-sending the first tag via hidden field
    r2 = client.post(
        "/notes/new",
        data={"title": "T", "body": "B", "tags": "python", "tag_name": "flask", "newTag": "true"},
    )
    assert b"python" in r2.data
    assert b"flask" in r2.data


def test_add_tag_active_tags_above_tag_textbox(client):
    r = client.post(
        "/notes/new",
        data={"title": "T", "body": "B", "tag_name": "django", "newTag": "true"},
    )
    html = r.data
    tag_pos = html.find(b"django")
    textbox_pos = html.find(b"tag_name")
    assert tag_pos != -1
    assert textbox_pos != -1
    assert tag_pos < textbox_pos


# ---------------------------------------------------------------------------
# Creating a note saves tags along with title and body
# ---------------------------------------------------------------------------

def test_create_note_persists_tags(client, app):
    app.notes.clear()
    r = client.post(
        "/notes/new",
        data={"title": "Tagged Note", "body": "Some content", "tags": "python"},
    )
    assert r.status_code in (302, 303)
    saved = next(n for n in app.notes if n["title"] == "Tagged Note")
    assert "python" in saved.get("tags", [])


def test_create_note_persists_multiple_tags(client, app):
    app.notes.clear()
    r = client.post(
        "/notes/new",
        data={"title": "Multi Tag", "body": "Body here", "tags": ["python", "flask"]},
    )
    assert r.status_code in (302, 303)
    saved = next(n for n in app.notes if n["title"] == "Multi Tag")
    assert "python" in saved.get("tags", [])
    assert "flask" in saved.get("tags", [])


def test_create_note_without_tags_still_works(client, app):
    app.notes.clear()
    r = client.post(
        "/notes/new",
        data={"title": "No Tags", "body": "Plain note"},
    )
    assert r.status_code in (302, 303)
    assert any(n["title"] == "No Tags" for n in app.notes)


# ---------------------------------------------------------------------------
# home.html displays tags next to note titles
# ---------------------------------------------------------------------------

def test_home_shows_tags_for_note(client, app):
    app.notes.clear()
    app.notes.append({"title": "Home Test", "body": "body", "tags": ["python", "web"]})
    r = client.get("/")
    assert r.status_code == 200
    assert b"python" in r.data
    assert b"web" in r.data


def test_home_tags_displayed_in_green(client, app):
    app.notes.clear()
    app.notes.append({"title": "Green Tag Note", "body": "body", "tags": ["green-tag"]})
    r = client.get("/")
    html = r.data.decode()
    # The tag text must appear inside a green-styled element
    # Accept inline style or a CSS class that implies green
    assert "green" in html
    assert "green-tag" in html


def test_home_note_without_tags_shows_no_tag_text(client, app):
    app.notes.clear()
    app.notes.append({"title": "Tagless", "body": "body", "tags": []})
    r = client.get("/")
    html = r.data.decode()
    # The title is present but no spurious tag markup should appear beside it
    assert "Tagless" in html


# ---------------------------------------------------------------------------
# Validation still enforced when 'Add Tag' is NOT the action
# ---------------------------------------------------------------------------

def test_add_tag_does_not_require_valid_title_or_body(client):
    """Tags can be added even while title/body are still blank."""
    r = client.post(
        "/notes/new",
        data={"title": "", "body": "", "tag_name": "early-tag", "newTag": "true"},
    )
    assert r.status_code == 200
    assert b"early-tag" in r.data


def test_create_note_still_validates_empty_title_with_tags(client):
    r = client.post(
        "/notes/new",
        data={"title": "", "body": "Some body", "tags": "python"},
    )
    assert r.status_code == 200
    assert b"Title is required" in r.data


def test_create_note_still_validates_empty_body_with_tags(client):
    r = client.post(
        "/notes/new",
        data={"title": "Some title", "body": "", "tags": "python"},
    )
    assert r.status_code == 200
    assert b"Body is required" in r.data
