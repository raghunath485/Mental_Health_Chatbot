import sqlite3

import mood_database as db


def test_verify_user_accepts_legacy_plaintext_password(tmp_path, monkeypatch):
    test_db = tmp_path / "mood_history.db"
    monkeypatch.setattr(db, "DB_NAME", str(test_db))

    db.init_user_table()

    conn = sqlite3.connect(test_db)
    conn.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        ("legacy@example.com", "secret123"),
    )
    conn.commit()
    conn.close()

    user_id = db.verify_user("legacy@example.com", "secret123")
    assert user_id is not None

    conn = sqlite3.connect(test_db)
    upgraded_password = conn.execute(
        "SELECT password FROM users WHERE username = ?",
        ("legacy@example.com",),
    ).fetchone()[0]
    conn.close()

    assert upgraded_password != "secret123"
    assert upgraded_password.startswith("scrypt:")


def test_verify_user_matches_username_case_insensitively(tmp_path, monkeypatch):
    test_db = tmp_path / "mood_history.db"
    monkeypatch.setattr(db, "DB_NAME", str(test_db))

    db.init_user_table()
    ok, user_id, error = db.create_account("User@Example.com", "secret123")

    assert ok, error
    assert db.verify_user("user@example.com", "secret123") == user_id
