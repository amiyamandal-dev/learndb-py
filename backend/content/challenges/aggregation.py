"""Aggregation challenges for intermediate to advanced learners."""

from backend.models.challenge import (
    Challenge,
    ChallengeCategory,
    Difficulty,
    ValidationRule,
    ValidationType,
)

# Challenge: COUNT
AGG_001 = Challenge(
    id="agg_001",
    title="Count the Fruits",
    description="""
# Count the Fruits

Write a query to count the total number of fruits in the `fruits` table.

Select the count with alias `total_count`.

**Hint:** Use the COUNT() aggregate function.
""",
    category=ChallengeCategory.AGGREGATION,
    difficulty=Difficulty.BEGINNER,
    xp_reward=15,
    setup_sql=[
        "CREATE TABLE fruits (id INTEGER PRIMARY KEY, name TEXT, avg_weight INTEGER)",
        "INSERT INTO fruits (id, name, avg_weight) VALUES (1, 'apple', 200)",
        "INSERT INTO fruits (id, name, avg_weight) VALUES (2, 'orange', 140)",
        "INSERT INTO fruits (id, name, avg_weight) VALUES (3, 'banana', 118)",
        "INSERT INTO fruits (id, name, avg_weight) VALUES (4, 'grape', 5)",
        "INSERT INTO fruits (id, name, avg_weight) VALUES (5, 'watermelon', 10000)",
    ],
    validation_rules=[
        ValidationRule(
            type=ValidationType.EXACT_MATCH,
            expected_value=[
                {"total_count": 5},
            ]
        ),
    ],
    hints=[
        "COUNT(column_name) counts non-null values",
        "COUNT(id) will count all rows since id is never null",
        "Use AS to create an alias for the result"
    ],
    expected_query="SELECT COUNT(id) AS total_count FROM fruits",
    concept_explanation="COUNT() is an aggregate function that counts rows. COUNT(column) counts non-null values, COUNT(*) counts all rows."
)

# Challenge: SUM and AVG
AGG_002 = Challenge(
    id="agg_002",
    title="Average Weight",
    description="""
# Average Weight

Calculate the average weight of all fruits.

Select the result as `avg_weight`.
""",
    category=ChallengeCategory.AGGREGATION,
    difficulty=Difficulty.BEGINNER,
    xp_reward=15,
    setup_sql=[
        "CREATE TABLE fruits (id INTEGER PRIMARY KEY, name TEXT, weight INTEGER)",
        "INSERT INTO fruits (id, name, weight) VALUES (1, 'apple', 200)",
        "INSERT INTO fruits (id, name, weight) VALUES (2, 'orange', 140)",
        "INSERT INTO fruits (id, name, weight) VALUES (3, 'banana', 160)",
    ],
    validation_rules=[
        # AVG of 200, 140, 160 = 500/3 = 166.67
        ValidationRule(
            type=ValidationType.ROW_COUNT,
            expected_value=1
        ),
    ],
    hints=[
        "AVG() calculates the average of a column",
        "AVG(weight) will give you the average weight",
        "Use AS for the alias"
    ],
    expected_query="SELECT AVG(weight) AS avg_weight FROM fruits",
)

# Challenge: GROUP BY
AGG_003 = Challenge(
    id="agg_003",
    title="Employees per Department",
    description="""
# Employees per Department

Count how many employees are in each department.

Select `depid` and the count as `emp_count`, grouped by department.
""",
    category=ChallengeCategory.AGGREGATION,
    difficulty=Difficulty.INTERMEDIATE,
    xp_reward=25,
    setup_sql=[
        "CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, salary INTEGER, depid INTEGER)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (1, 'Alice', 100000, 1)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (2, 'Bob', 80000, 2)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (3, 'Carol', 90000, 1)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (4, 'Dave', 75000, 2)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (5, 'Eve', 85000, 1)",
    ],
    validation_rules=[
        ValidationRule(
            type=ValidationType.CONTAINS_ROWS,
            expected_value=[
                {"depid": 1, "emp_count": 3},
                {"depid": 2, "emp_count": 2},
            ]
        ),
        ValidationRule(
            type=ValidationType.ROW_COUNT,
            expected_value=2
        ),
    ],
    hints=[
        "GROUP BY groups rows by column values",
        "Aggregate functions operate on each group",
        "SELECT depid, COUNT(id) ... GROUP BY depid"
    ],
    expected_query="SELECT depid, COUNT(id) AS emp_count FROM employees GROUP BY depid",
    concept_explanation="GROUP BY divides rows into groups based on column values. Aggregate functions then operate on each group separately."
)

# Challenge: GROUP BY with HAVING
AGG_004 = Challenge(
    id="agg_004",
    title="Big Departments",
    description="""
# Big Departments

Find departments with more than 2 employees.

Select `depid` and `emp_count`, but only show departments with emp_count > 2.

**Hint:** Use HAVING to filter groups.
""",
    category=ChallengeCategory.AGGREGATION,
    difficulty=Difficulty.INTERMEDIATE,
    xp_reward=30,
    setup_sql=[
        "CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, depid INTEGER)",
        "INSERT INTO employees (id, name, depid) VALUES (1, 'Alice', 1)",
        "INSERT INTO employees (id, name, depid) VALUES (2, 'Bob', 2)",
        "INSERT INTO employees (id, name, depid) VALUES (3, 'Carol', 1)",
        "INSERT INTO employees (id, name, depid) VALUES (4, 'Dave', 2)",
        "INSERT INTO employees (id, name, depid) VALUES (5, 'Eve', 1)",
        "INSERT INTO employees (id, name, depid) VALUES (6, 'Frank', 3)",
        "INSERT INTO employees (id, name, depid) VALUES (7, 'Grace', 1)",
    ],
    validation_rules=[
        ValidationRule(
            type=ValidationType.EXACT_MATCH,
            expected_value=[
                {"depid": 1, "emp_count": 4},
            ]
        ),
    ],
    hints=[
        "First GROUP BY depid",
        "HAVING filters groups (like WHERE for rows)",
        "HAVING COUNT(id) > 2"
    ],
    expected_query="SELECT depid, COUNT(id) AS emp_count FROM employees GROUP BY depid HAVING COUNT(id) > 2",
    concept_explanation="HAVING filters groups after aggregation, while WHERE filters rows before grouping. Use HAVING with aggregate conditions."
)

# Challenge: Multiple aggregates
AGG_005 = Challenge(
    id="agg_005",
    title="Department Statistics",
    description="""
# Department Statistics

For each department, calculate:
- Total employees (`emp_count`)
- Total salary (`total_salary`)
- Average salary (`avg_salary`)

Group by `depid`.
""",
    category=ChallengeCategory.AGGREGATION,
    difficulty=Difficulty.ADVANCED,
    xp_reward=40,
    setup_sql=[
        "CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, salary INTEGER, depid INTEGER)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (1, 'Alice', 100000, 1)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (2, 'Bob', 80000, 2)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (3, 'Carol', 90000, 1)",
        "INSERT INTO employees (id, name, salary, depid) VALUES (4, 'Dave', 70000, 2)",
    ],
    validation_rules=[
        ValidationRule(
            type=ValidationType.ROW_COUNT,
            expected_value=2
        ),
        ValidationRule(
            type=ValidationType.COLUMN_CHECK,
            expected_value=["depid", "emp_count", "total_salary", "avg_salary"]
        ),
    ],
    hints=[
        "You can use multiple aggregate functions in one query",
        "COUNT, SUM, and AVG can all be in the SELECT",
        "All aggregate columns need aliases"
    ],
    expected_query="""
        SELECT depid,
               COUNT(id) AS emp_count,
               SUM(salary) AS total_salary,
               AVG(salary) AS avg_salary
        FROM employees
        GROUP BY depid
    """,
)


# Export all challenges
AGGREGATION_CHALLENGES = [
    AGG_001,
    AGG_002,
    AGG_003,
    AGG_004,
    AGG_005,
]
