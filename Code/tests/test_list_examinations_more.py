import data
from tests.conftest import FakeDB


def make_exam_kwargs_from_sig(**overrides):
    import inspect
    sig = inspect.signature(data.Examination.__init__)
    keys = [k for k in sig.parameters if k != "self"]
    base = {}
    for k in keys:
        if k in overrides:
            base[k] = overrides[k]
        elif k in ("id",):
            base[k] = None
        elif k in ("db",):
            base[k] = overrides.get("db")
        elif k in ("person_id", "personid"):
            base[k] = 1
        elif "date" in k:
            base[k] = "2025-01-01 10:00"
        elif k.startswith(("is_", "has_", "ack_", "remember_", "run_", "use_", "direction_", "reappointment")):
            base[k] = False
        elif k.endswith("_id") or k == "id":
            base[k] = 1
        else:
            base[k] = 0 if isinstance(base.get(k, ""), int) else ""
            base[k] = "" 
    base.update(overrides)
    return base


def test_list_of_examinations_add_calls_insert(fake_db):
    loe = data.ListOfExaminations(fake_db)

    # Подготовим lastid для Examination(id=None)
    fake_db.cursor._fetchall_data = [(1,), (2,)]
    loe.add_examination(
        person_id=1,
        eyesight_without_od=1.0,
        eyesight_without_os=1.0,
        eyesight_with_od=1.0,
        eyesight_with_od_sph=0.0,
        eyesight_with_od_cyl=0.0,
        eyesight_with_od_ax=0,
        eyesight_with_os=1.0,
        eyesight_with_os_sph=0.0,
        eyesight_with_os_cyl=0.0,
        eyesight_with_os_ax=0,
        schiascopy_od="Em",
        schiascopy_os="Em",
        glasses_od_sph=0.0,
        glasses_od_cyl=0.0,
        glasses_od_ax=0,
        glasses_os_sph=0.0,
        glasses_os_cyl=0.0,
        glasses_os_ax=0,
        glasses_dpp=0,
        diagnosis_subscription="",
        visit_date="2025-01-01 10:00",
        complaints="",
        disease_anamnesis="",
        life_anamnesis="",
        eyesight_type="",
        relative_accommodation_reserve=0.0,
        schober_test="",
        pupils="",
        od_eye_position="",
        od_oi="",
        od_eyelid="",
        od_lacrimal_organs="",
        od_conjunctiva="",
        od_discharge="",
        od_iris="",
        od_anterior_chamber="",
        od_refractive_medium="",
        od_optic_disk="",
        od_vessels="",
        od_macular_reflex="",
        od_visible_periphery="",
        od_diagnosis="",
        od_icd_code="",
        os_eye_position="",
        os_oi="",
        os_eyelid="",
        os_lacrimal_organs="",
        os_conjunctiva="",
        os_discharge="",
        os_iris="",
        os_anterior_chamber="",
        os_refractive_medium="",
        os_optic_disk="",
        os_vessels="",
        os_macular_reflex="",
        os_visible_periphery="",
        os_diagnosis="",
        os_icd_code="",
        recommendations="",
        direction_to_aokb=False,
        reappointment=False,
        reappointment_time="",
    )
    assert any("INSERT INTO Examinations" in q for q in fake_db.queries)


def test_examination_update_sends_update(fake_db):
    e = data.Examination(**make_exam_kwargs_from_sig(db=fake_db, id=5))
    e.update_data_in_database()
    assert any("UPDATE Examinations SET" in q for q in fake_db.queries)


def test_examination_delete_cascades_to_people(fake_db):
    # fetchone: сначала Personid, потом Count(Id)
    fake_db.cursor._fetchone_data = (7,)

    seq = [(7,), (0,)]
    def fetchone_seq(): # подмена fetchone
        return seq.pop(0)
    fake_db.cursor.fetchone = fetchone_seq

    # заглушка People
    class DummyPeople:
        def __init__(self):
            self.deleted = []
        def delete_person(self, pid):
            self.deleted.append(pid)

    people = DummyPeople()

    e = data.Examination(**make_exam_kwargs_from_sig(db=fake_db, id=5))
    e.delete_examination_from_database(people=people)

    assert any("DELETE FROM Examinations" in q for q in fake_db.queries)
    assert people.deleted == [7]
