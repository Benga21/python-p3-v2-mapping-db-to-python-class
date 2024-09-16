from lib.__init__ import CONN, CURSOR
from  lib.department import Department
import pytest


class TestDepartment:
    '''Class Department in department.py'''

    @pytest.fixture(autouse=True)
    def drop_tables(self):
        '''Drop tables prior to each test.'''
        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CURSOR.execute("DROP TABLE IF EXISTS departments")
        CONN.commit()

    def test_creates_table(self):
        '''Contains method "create_table()" that creates table "departments" if it does not exist.'''
        Department.create_table()

        # Check if the table was created successfully
        result = CURSOR.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='departments'").fetchone()
        assert result is not None, "Table 'departments' was not created."

    def test_drops_table(self):
        '''Contains method "drop_table()" that drops table "departments" if it exists.'''
        # Create the table first
        Department.create_table()

        Department.drop_table()

        # Check if the table was dropped successfully
        result = CURSOR.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='departments'").fetchone()
        assert result is None, "Table 'departments' was not dropped."

    def test_saves_department(self):
        '''Contains method "save()" that saves a Department instance to the db and assigns the instance an id.'''
        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()

        sql = "SELECT * FROM departments"
        row = CURSOR.execute(sql).fetchone()

        assert row is not None, "No rows found in 'departments' table."
        assert (row[0], row[1], row[2]) == (department.id, "Payroll", "Building A, 5th Floor"), \
            "Saved department data does not match expected values."

    def test_creates_department(self):
        '''Contains method "create()" that creates a new row in the db using parameter data and returns a Department instance.'''
        Department.create_table()
        department = Department.create("Payroll", "Building A, 5th Floor")

        sql = "SELECT * FROM departments"
        row = CURSOR.execute(sql).fetchone()

        assert row is not None, "No rows found in 'departments' table."
        assert (row[0], row[1], row[2]) == (department.id, "Payroll", "Building A, 5th Floor"), \
            "Created department data does not match expected values."

    def test_updates_row(self):
        '''Contains a method "update()" that updates an instance's corresponding db row to match its new attribute values.'''
        Department.create_table()

        department1 = Department.create("Human Resources", "Building C, East Wing")
        id1 = department1.id
        department2 = Department.create("Marketing", "Building B, 3rd Floor")
        id2 = department2.id

        # Assign new values for name and location
        department2.name = "Sales and Marketing"
        department2.location = "Building B, 4th Floor"

        # Persist the updated name and location values
        department2.update()

        # Check department1 is unchanged
        department = Department.find_by_id(id1)
        assert department is not None, "Department with id1 not found."
        assert (department.id, department.name, department.location) == \
               (id1, "Human Resources", "Building C, East Wing"), \
            "Department1 was updated unexpectedly."

        # Check department2 is updated
        department = Department.find_by_id(id2)
        assert department is not None, "Department with id2 not found."
        assert (department.id, department.name, department.location) == \
               (id2, "Sales and Marketing", "Building B, 4th Floor"), \
            "Department2 was not updated correctly."

    def test_deletes_row(self):
        '''Contains a method "delete()" that deletes the instance's corresponding db row.'''
        Department.create_table()

        department1 = Department.create("Human Resources", "Building C, East Wing")
        id1 = department1.id
        department2 = Department.create("Sales and Marketing", "Building B, 4th Floor")
        id2 = department2.id

        department2.delete()

        # Check department1 is unchanged
        department = Department.find_by_id(id1)
        assert department is not None, "Department with id1 not found."
        assert (department.id, department.name, department.location) == \
               (id1, "Human Resources", "Building C, East Wing"), \
            "Department1 was deleted unexpectedly."

        # Check department2 is deleted
        department = Department.find_by_id(id2)
        assert department is None, "Department with id2 was not deleted."

    def test_instance_from_db(self):
        '''Contains method "instance_from_db()" that takes a table row and returns a Department instance.'''
        Department.create_table()
        Department.create("Payroll", "Building A, 5th Floor")

        sql = "SELECT * FROM departments"
        row = CURSOR.execute(sql).fetchone()
        department = Department.instance_from_db(row)

        assert (row[0], row[1], row[2]) == (department.id, department.name, department.location), \
            "Department instance from DB does not match row data."

    def test_gets_all(self):
        '''Contains method "get_all()" that returns a list of Department instances for every row in the db.'''
        Department.create_table()

        department1 = Department.create("Human Resources", "Building C, East Wing")
        department2 = Department.create("Marketing", "Building B, 3rd Floor")

        departments = Department.get_all()

        assert len(departments) == 2, "The number of departments retrieved does not match the expected count."
        assert (departments[0].id, departments[0].name, departments[0].location) == \
               (department1.id, "Human Resources", "Building C, East Wing"), \
            "First department in the list does not match."
        assert (departments[1].id, departments[1].name, departments[1].location) == \
               (department2.id, "Marketing", "Building B, 3rd Floor"), \
            "Second department in the list does not match."

    def test_finds_by_id(self):
        '''Contains method "find_by_id()" that returns a Department instance corresponding to the db row retrieved by id.'''
        Department.create_table()
        department1 = Department.create("Human Resources", "Building C, East Wing")
        department2 = Department.create("Marketing", "Building B, 3rd Floor")

        department = Department.find_by_id(department1.id)
        assert (department.id, department.name, department.location) == \
               (department1.id, "Human Resources", "Building C, East Wing"), \
            "Department with id1 not found or incorrect."

        department = Department.find_by_id(department2.id)
        assert (department.id, department.name, department.location) == \
               (department2.id, "Marketing", "Building B, 3rd Floor"), \
            "Department with id2 not found or incorrect."

        department = Department.find_by_id(0)
        assert department is None, "Find by non-existent id should return None."

    def test_finds_by_name(self):
        '''Contains method "find_by_name()" that returns a Department instance corresponding to the db row retrieved by name.'''
        Department.create_table()
        department1 = Department.create("Human Resources", "Building C, East Wing")
        department2 = Department.create("Marketing", "Building B, 3rd Floor")

        department = Department.find_by_name("Human Resources")
        assert (department.id, department.name, department.location) == \
               (department1.id, "Human Resources", "Building C, East Wing"), \
            "Department with name 'Human Resources' not found or incorrect."

        department = Department.find_by_name("Marketing")
        assert (department.id, department.name, department.location) == \
               (department2.id, "Marketing", "Building B, 3rd Floor"), \
            "Department with name 'Marketing' not found or incorrect."

        department = Department.find_by_name("Unknown")
        assert department is None, "Find by non-existent name should return None."