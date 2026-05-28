"""Tests for the tags feature — every new note must start with an empty tags list."""


def test_new_note_has_empty_tags(client, app):
    app.notes.clear()
    r = client.post("/notes/new", data={"title": "Tagged Note", "body": "Some content"})
    assert r.status_code in (302, 303)
    assert app.notes[0]["tags"] == []
