from data import Templates, Settings

def test_settings_update_on_top(fake_db):
    fake_db.cursor._fetchall_data = [(0, 1, 0, 1, "0,0", "hash", 1, 1, 1, 1, 1, 1, 1000, 0, 0)]
    s = Settings(fake_db)
    s.update_on_top(1)
    assert "UPDATE Settings SET On_top = 1" in fake_db.queries

def test_templates_update_template_index_fix(fake_db):
    fake_db.cursor._fetchall_data = [
        (1, "eye_position", "ортофория"),
        (2, "eye_position", "экзофория"),
    ]
    t = Templates(fake_db)
    t.update_template(2, "eye_position", "NEW")
    assert t.eye_position[1][1] == "NEW"
