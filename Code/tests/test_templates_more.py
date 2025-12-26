import data


def test_templates_add_update_delete(fake_db):
    fake_db.cursor._fetchall_data = [
        (1, "eye_position", "A"),
        (2, "eye_position", "B"),
    ]

    t = data.Templates(fake_db)

    # add_template - INSERT
    t.add_template("eye_position", "C")
    assert any("INSERT INTO Templates" in q for q in fake_db.queries)

    # update_template - UPDATE
    t.update_template(2, "eye_position", "B2")
    assert any("Update Templates SET" in q or "UPDATE Templates SET" in q for q in fake_db.queries)

    # delete_template - DELETE
    t.delete_template("eye_position", "B2")
    assert any("DELETE FROM Templates" in q for q in fake_db.queries)
