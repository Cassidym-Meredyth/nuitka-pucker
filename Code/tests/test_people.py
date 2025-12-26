from data import Person, People

def test_person_autoincrement_id(fake_db):
    fake_db.cursor._fetchall_data = [(1,), (2,), (10,)]
    p = Person(full_name="A", birthdate="2000-01-01", id=None, db=fake_db)
    assert p.id == 11

def test_people_search_by_id(fake_db):
    fake_db.cursor._fetchall_data = [(1, "Ivan", "2000-01-01")]
    people = People(fake_db)
    assert people.search(id=1).full_name == "Ivan"
    assert people.search(id=999) is None

def test_people_search_by_name_prefix(fake_db):
    fake_db.cursor._fetchall_data = [
        (1, "Ivan Petrov", "2000-01-01"),
        (2, "Ilya Sidorov", "2001-01-01"),
        (3, "Petr Ivanov", "1999-01-01"),
    ]
    people = People(fake_db)
    found = people.search(name="Iv")
    assert [p.id for p in found] == [1]

def test_people_add_person_calls_insert(fake_db):
    fake_db.cursor._fetchall_data = [(1,), (2,)]
    fake_db.cursor._fetchall_data = [] 
    people = People(fake_db)

    fake_db.cursor._fetchall_data = [(1,), (2,)]
    newp = people.add_person("New", "2010-10-10")
    assert newp.id == 3
    assert any("INSERT INTO People" in q for q in fake_db.queries)

def test_person_update_person_fix(fake_db):
    fake_db.cursor._fetchall_data = [(1,)]
    p = Person("Old", "2000", id=1, db=fake_db)
    p.update_person(1, "NewName", "2001")
    assert p.full_name == "NewName"
