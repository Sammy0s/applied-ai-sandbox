"""Tiny Flask app — applied-ai-sandbox.

Each task in tasks/ asks you to add or fix one piece. The tests in tests/
describe exactly what "done" means.
"""
from __future__ import annotations

from flask import Flask, render_template, request, redirect, url_for


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "sandbox-not-a-real-secret"

    # In-memory store for the sandbox. Resets on every restart, which is
    # fine for practice. Real apps use a database.
    app.notes: list[dict] = []  # type: ignore[attr-defined]

    @app.route("/")
    def home():
        return render_template("home.html", notes=app.notes)

    def sanitize_tags(tag_list):
        seen = []
        for t in tag_list:
            t = t.strip()
            if t and t not in seen:
                seen.append(t)
        return seen

    @app.route("/notes/new", methods=["GET", "POST"])
    def new_note():
        if request.method == "POST":
            title        = (request.form.get("title") or "").strip()
            body         = (request.form.get("body") or "").strip()
            tags         = sanitize_tags(request.form.getlist("tags"))
            new_tag      = (request.form.get("tag_name") or "").strip()
            new_tag_mode = request.form.get("newTag") == "true"
            tag_error    = None

            if new_tag_mode:
                if not new_tag:
                    tag_error = "Tag name cannot be blank"
                elif new_tag in tags:
                    tag_error = "Tag already added"
                else:
                    tags.append(new_tag)
                return render_template("new_note.html", title=title, body=body, tags=tags, tag_error=tag_error)

            if not title:
                error = "Title is required"
            elif not body:
                error = "Body is required"
            else:
                app.notes.append({"title": title, "body": body, "tags": tags})
                return redirect(url_for("home"))
            return render_template("new_note.html", error=error, title=title, body=body, tags=tags)
        return render_template("new_note.html", tags=[])

    # TASK 02 will add a /notes/<idx>/delete route here.

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
