"""JOIN challenges for intermediate learners."""

from backend.models.challenge import (
    Challenge,
    ChallengeCategory,
    Difficulty,
    ValidationRule,
    ValidationType,
)

# Challenge: Inner Join
JOIN_001 = Challenge(
    id="join_001",
    title="Employees and Departments",
    description="""
# Employees and Departments

You have two tables:
- `employees`: id, name, salary, depid
- `department`: depid, name

Write a query using INNER JOIN to show each employee's name alongside their department name.

Select columns as `e.name` (employee name) and `d.name` (department name).
""",
    category=ChallengeCategory.JOINS,
    difficulty=Difficulty.INTERMEDIATE,
    xp_reward=25,
    setup_sql=[
        "CREATE TABLE department (depid INTEGER PRIMARY KEY, name TEXT)",
        "INSERT INTO department (depid, name) VALUES (1, 'Engineering')",
        "INSERT INTO department (depid, name) VALUES (2, 'Sales')",
        "INSERT INTO department (depid, name) VALUES (3, 'Marketing')",
        "CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, salary INTEGER, depid INTEGER)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (1, 'Alice', 100000, 1)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (2, 'Bob', 80000, 2)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (3, 'Carol', 90000, 1)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (4, 'Dave', 75000, 2)",
    ],
    validation_rules=[
        ValidationRule(
            type=ValidationType.ROW_COUNT,
            expected_value=4
        ),
        ValidationRule(
            type=ValidationType.CONTAINS_ROWS,
            expected_value=[
                {"e.name": "Alice", "d.name": "Engineering"},
                {"e.name": "Bob", "d.name": "Sales"},
                {"e.name": "Carol", "d.name": "Engineering"},
                {"e.name": "Dave", "d.name": "Sales"},
            ]
        ),
    ],
    hints=[
        "Use table aliases: employees e, department d",
        "JOIN connects tables using ON clause",
        "The join condition: e.depid = d.depid"
    ],
    expected_query="""
        SELECT e.name, d.name
        FROM employees e
        INNER JOIN department d ON e.depid = d.depid
    """,
    concept_explanation="INNER JOIN returns only rows where there's a match in both tables based on the join condition."
)

# Challenge: Left Join
JOIN_002 = Challenge(
    id="join_002",
    title="All Employees with Departments",
    description="""
# All Employees with Departments

Some employees might not have a department assigned (depid could be NULL or reference a non-existent department).

Write a query using LEFT JOIN to show ALL employees and their department names.
Employees without a department should still appear with NULL for the department name.

Select `e.name` and `d.name`.
""",
    category=ChallengeCategory.JOINS,
    difficulty=Difficulty.INTERMEDIATE,
    xp_reward=30,
    setup_sql=[
        "CREATE TABLE department (depid INTEGER PRIMARY KEY, name TEXT)",
        "INSERT INTO department (depid, name) VALUES (1, 'Engineering')",
        "INSERT INTO department (depid, name) VALUES (2, 'Sales')",
        "CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, salary INTEGER, depid INTEGER)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (1, 'Alice', 100000, 1)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (2, 'Bob', 80000, 2)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (3, 'Carol', 90000, 1)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (4, 'Eve', 70000, 99)",  # Non-existent dept
    ],
    validation_rules=[
        ValidationRule(
            type=ValidationType.ROW_COUNT,
            expected_value=4
        ),
    ],
    hints=[
        "LEFT JOIN keeps all rows from the left table",
        "Use LEFT OUTER JOIN or just LEFT JOIN",
        "Unmatched rows will have NULL for right table columns"
    ],
    expected_query="""
        SELECT e.name, d.name
        FROM employees e
        LEFT JOIN department d ON e.depid = d.depid
    """,
    concept_explanation="LEFT JOIN returns all rows from the left table, and matched rows from the right table. NULL is used when there's no match."
)

# Challenge: Join with Filter
JOIN_003 = Challenge(
    id="join_003",
    title="High-Paid Engineers",
    description="""
# High-Paid Engineers

Find all employees in the Engineering department who earn more than 85000.

Select `e.name`, `e.salary`, and `d.name`.
""",
    category=ChallengeCategory.JOINS,
    difficulty=Difficulty.INTERMEDIATE,
    xp_reward=30,
    setup_sql=[
        "CREATE TABLE department (depid INTEGER PRIMARY KEY, name TEXT)",
        "INSERT INTO department (depid, name) VALUES (1, 'Engineering')",
        "INSERT INTO department (depid, name) VALUES (2, 'Sales')",
        "INSERT INTO department (depid, name) VALUES (3, 'Marketing')",
        "CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, salary INTEGER, depid INTEGER)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (1, 'Alice', 100000, 1)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (2, 'Bob', 80000, 2)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (3, 'Carol', 90000, 1)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (4, 'Dave', 75000, 1)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (5, 'Eve', 95000, 2)",
    ],
    validation_rules=[
        ValidationRule(
            type=ValidationType.EXACT_MATCH,
            expected_value=[
                {"e.name": "Alice", "e.salary": 100000, "d.name": "Engineering"},
                {"e.name": "Carol", "e.salary": 90000, "d.name": "Engineering"},
            ],
            order_matters=False
        ),
    ],
    hints=[
        "First JOIN the tables",
        "Then add WHERE to filter results",
        "You need two conditions: department name AND salary"
    ],
    expected_query="""
        SELECT e.name, e.salary, d.name
        FROM employees e
        INNER JOIN department d ON e.depid = d.depid
        WHERE d.name = 'Engineering' AND e.salary > 85000
    """,
)

# Challenge: Cross Join
JOIN_004 = Challenge(
    id="join_004",
    title="All Combinations",
    description="""
# All Combinations

You have a `colors` table and a `sizes` table.

Write a query using CROSS JOIN to generate all possible color-size combinations.
Select `c.name` (color) and `s.name` (size).
""",
    category=ChallengeCategory.JOINS,
    difficulty=Difficulty.INTERMEDIATE,
    xp_reward=25,
    setup_sql=[
        "CREATE TABLE colors (id INTEGER PRIMARY KEY, name TEXT)",
        "INSERT INTO colors (id, name) VALUES (1, 'Red')",
        "INSERT INTO colors (id, name) VALUES (2, 'Blue')",
        "CREATE TABLE sizes (id INTEGER PRIMARY KEY, name TEXT)",
        "INSERT INTO sizes (id, name) VALUES (1, 'Small')",
        "INSERT INTO sizes (id, name) VALUES (2, 'Medium')",
        "INSERT INTO sizes (id, name) VALUES (3, 'Large')",
    ],
    validation_rules=[
        ValidationRule(
            type=ValidationType.ROW_COUNT,
            expected_value=6  # 2 colors x 3 sizes
        ),
    ],
    hints=[
        "CROSS JOIN produces the Cartesian product",
        "No ON clause is needed for CROSS JOIN",
        "Result will have rows from left × rows from right"
    ],
    expected_query="SELECT c.name, s.name FROM colors c CROSS JOIN sizes s",
    concept_explanation="CROSS JOIN produces all possible combinations of rows from both tables. If table A has 2 rows and table B has 3 rows, result has 6 rows."
)


# Export all challenges
JOIN_CHALLENGES = [
    JOIN_001,
    JOIN_002,
    JOIN_003,
    JOIN_004,
]
