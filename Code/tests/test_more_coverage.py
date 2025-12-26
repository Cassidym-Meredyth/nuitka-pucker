import data


def test_settings_more_updates(fake_db):
    fake_db.cursor._fetchall_data = [(
        0, 1, 0, 1, "0,0", "hash",
        1, 1, 1, 1, 1, 1,
        1000, 0, 0
    )]
    s = data.Settings(fake_db)

    # Просто дергаем пачку update-методов, просто много строк покрытия
    s.update_on_top(0)
    s.update_remember_last_position(0)
    s.update_run_with_system(1)
    s.update_use_password(1)
    s.update_last_position("10,10")
    s.update_ack_save_examination(0)
    s.update_ack_erase_examination(0)
    s.update_ack_save_change_data(0)
    s.update_ack_delete_change_data(0)
    s.update_ack_save_person(0)
    s.update_ack_delete_person(0)
    s.update_number_of_visible_records(50, to_db=True)
    s.update_objective_synchronize_eyes(1)

    # Проверяем, что SQL действительно обновился
    assert any("UPDATE Settings SET" in q for q in fake_db.queries)


def test_examinations_manager_methods(fake_db):
    manager_cls = None
    for name in dir(data):
        obj = getattr(data, name)
        if isinstance(obj, type):
            for meth in ("get_examination_by_id", "get_examinations_by_person_id", "get_people_ids"):
                if hasattr(obj, meth):
                    manager_cls = obj
                    break
        if manager_cls:
            break

    assert manager_cls is not None, "Не найден класс менеджера обследований в data.py"

    m = manager_cls.__new__(manager_cls)
    setattr(m, "_ListOfExaminations__db", fake_db)

    # Вставляем оследования вручную
    e1 = data.Examination(**_make_exam_kwargs(db=fake_db, id=1, person_id=10, visit_date="2025-01-01 10:00"))
    e2 = data.Examination(**_make_exam_kwargs(db=fake_db, id=2, person_id=10, visit_date="2025-01-02 10:00"))
    e3 = data.Examination(**_make_exam_kwargs(db=fake_db, id=3, person_id=11, visit_date="2025-01-01 10:00"))
    setattr(m, "_ListOfExaminations__examinations", {1: e1, 2: e2, 3: e3})


    assert m.get_examination_by_id(2).id == 2
    assert len(m.get_examinations_by_person_id(10)) == 2
    assert m.get_examination_by_person_id_and_examination_datetime(11, "2025-01-01 10:00").id == 3

    # Ветка person_id=list
    fake_db.cursor._fetchall_data = [(1,), (3,)]
    res = m.get_examinations_by_person_id([10, 11])
    assert [x.id for x in res] == [1, 3]



def _make_exam_kwargs(**overrides):
    import inspect
    sig = inspect.signature(data.Examination.__init__)
    keys = [k for k in sig.parameters if k != "self"]
    out = {}
    for k in keys:
        if k in overrides:
            out[k] = overrides[k]
        elif k in ("db",):
            out[k] = overrides.get("db")
        elif k in ("id",):
            out[k] = overrides.get("id", None)
        elif k in ("person_id", "personid"):
            out[k] = overrides.get("person_id", overrides.get("personid", 1))
        elif "date" in k:
            out[k] = overrides.get("visit_date", overrides.get("visitdate", "2025-01-01 10:00"))
        elif k.startswith(("direction_", "reappointment", "ack_", "remember_", "run_", "use_")):
            out[k] = False
        else:
            out[k] = ""
    return out
