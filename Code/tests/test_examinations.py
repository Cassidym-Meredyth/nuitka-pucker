import inspect

from data import Examination, ExaminationTemplates


def make_exam_kwargs(**overrides):
    sig = inspect.signature(Examination.__init__)
    params = [p for p in sig.parameters.keys() if p != "self"]

    defaults = {
        "id": None,
        "db": None,
        "person_id": 1,
        "personid": 1,
        "visit_date": "2025-01-01 10:00",
        "visitdate": "2025-01-01 10:00",
        "direction_to_aokb": False,
        "directiontoaokb": False,
        "reappointment": False,
        "reappointment_time": "",
        "reappointmenttime": "",
    }

    kwargs = {}
    for name in params:
        if name in overrides:
            kwargs[name] = overrides[name]
        elif name in defaults:
            kwargs[name] = defaults[name]
        else:
            low = name.lower()
            if "date" in low:
                kwargs[name] = "2025-01-01 10:00"
            elif low.startswith(("is_", "has_", "use_", "ack_", "remember_", "run_", "direction_", "reappointment")):
                kwargs[name] = False
            elif low == "id" or low.endswith("_id"):
                kwargs[name] = 1
            elif any(k in low for k in ("ax", "axis", "count", "number")):
                kwargs[name] = 0
            elif any(k in low for k in ("with", "without", "sph", "cyl", "reserve", "dpp", "acuity")):
                kwargs[name] = 0.0
            else:
                kwargs[name] = ""

    kwargs.update(overrides)
    return kwargs


def test_examination_autoincrement_id(fake_db):
    fake_db.cursor._fetchall_data = [(1,), (2,), (10,)]
    e = Examination(**make_exam_kwargs(id=None, db=fake_db))
    assert e.id == 11


def test_examination_add_to_database_sends_insert(fake_db):
    e = Examination(**make_exam_kwargs(id=5, db=fake_db, person_id=7))

    if hasattr(e, "add_examination_to_database"):
        e.add_examination_to_database()
    elif hasattr(e, "addexaminationtodatabase"):
        e.addexaminationtodatabase()
    else:
        raise AttributeError("Examination has no add_*_to_database method")

    assert any("INSERT INTO Examinations" in q for q in fake_db.queries)


def test_examination_templates_get_template():
    et = ExaminationTemplates.__new__(ExaminationTemplates)
    et._ExaminationTemplates__templates = {"demo": "VALUE"}

    assert et.get_template("demo") == "VALUE"
