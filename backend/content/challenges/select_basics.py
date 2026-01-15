"""Basic SELECT challenges for beginners."""

from backend.models.challenge import (
    Challenge,
    ChallengeCategory,
    Difficulty,
    ValidationRule,
    ValidationType,
)

# Challenge: Select All Columns
SELECT_001 = Challenge(
    id="select_001",
    title="Select All Fruits",
    description="""
# Select All Fruits

You have a table called `fruits` with the following columns:
- `id` (INTEGER, PRIMARY KEY)
- `name` (TEXT)
- `avg_weight` (INTEGER)

Write a query to select the `name` and `avg_weight` of all fruits.

**Note:** LearnDB does not support `SELECT *` - you must specify column names explicitly.
""",
    category=ChallengeCategory.SELECT_BASICS,
    difficulty=Difficulty.BEGINNER,
    xp_reward=10,
    setup_sql=[
        "CREATE TABLE fruits (id INTEGER PRIMARY KEY, name TEXT, avg_weight INTEGER)",
        "INSERT INTO fruits (id, name, avg_weight) VALUES (1, 'apple', 200)",
        "INSERT INTO fruits (id, name, avg_weight) VALUES (2, 'orange', 140)",
        "INSERT INTO fruits (id, name, avg_weight) VALUES (3, 'banana', 118)",
    ],
    validation_rules=[
        ValidationRule(
            type=ValidationType.ROW_COUNT,
            expected_value=3
        ),
        ValidationRule(
            type=ValidationType.COLUMN_CHECK,
            expected_value=["name", "avg_weight"]
        ),
    ],
    hints=[
        "Use SELECT followed by column names separated by commas",
        "The FROM clause specifies which table to query",
        "Example: SELECT col1, col2 FROM tablename"
    ],
    expected_query="SELECT name, avg_weight FROM fruits",
    concept_explanation="The SELECT statement retrieves data from tables. You specify which columns you want and which table to get them from."
)

# Challenge: Select with ORDER BY
SELECT_002 = Challenge(
    id="select_002",
    title="Sort the Fruits",
    description="""
# Sort the Fruits

Using the same `fruits` table, write a query to select `name` and `avg_weight`,
sorted by `avg_weight` in ascending order (lightest first).

**Hint:** Use the ORDER BY clause.
""",
    category=ChallengeCategory.SELECT_BASICS,
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
                {"name": "grape", "avg_weight": 5},
                {"name": "banana", "avg_weight": 118},
                {"name": "orange", "avg_weight": 140},
                {"name": "apple", "avg_weight": 200},
                {"name": "watermelon", "avg_weight": 10000},
            ],
            order_matters=True
        ),
    ],
    hints=[
        "Add ORDER BY at the end of your SELECT statement",
        "ORDER BY column_name ASC sorts in ascending order",
        "ASC is the default, so you can omit it"
    ],
    expected_query="SELECT name, avg_weight FROM fruits ORDER BY avg_weight",
    concept_explanation="ORDER BY sorts your results. ASC (ascending) is the default. Use DESC for descending order."
)

# Challenge: LIMIT clause
SELECT_003 = Challenge(
    id="select_003",
    title="Top 3 Heaviest",
    description="""
# Top 3 Heaviest Fruits

Write a query to find the 3 heaviest fruits.
Select `name` and `avg_weight`, sorted by weight descending, limited to 3 results.
""",
    category=ChallengeCategory.SELECT_BASICS,
    difficulty=Difficulty.BEGINNER,
    xp_reward=15,
    setup_sql=[
        "CREATE TABLE fruits (id INTEGER PRIMARY KEY, name TEXT, avg_weight INTEGER)",
        "INSERT INTO fruits (id, name, avg_weight) VALUES (1, 'apple', 200)",
        "INSERT INTO fruits (id, name, avg_weight) VALUES (2, 'orange', 140)",
        "INSERT INTO fruits (id, name, avg_weight) VALUES (3, 'banana', 118)",
        "INSERT INTO fruits (id, name, avg_weight) VALUES (4, 'grape', 5)",
        "INSERT INTO fruits (id, name, avg_weight) VALUES (5, 'watermelon', 10000)",
        "INSERT INTO fruits (id, name, avg_weight) VALUES (6, 'pineapple', 1000)",
    ],
    validation_rules=[
        ValidationRule(
            type=ValidationType.EXACT_MATCH,
            expected_value=[
                {"name": "watermelon", "avg_weight": 10000},
                {"name": "pineapple", "avg_weight": 1000},
                {"name": "apple", "avg_weight": 200},
            ],
            order_matters=True
        ),
    ],
    hints=[
        "Use ORDER BY with DESC to sort heaviest first",
        "Use LIMIT to restrict the number of results",
        "LIMIT comes after ORDER BY"
    ],
    expected_query="SELECT name, avg_weight FROM fruits ORDER BY avg_weight DESC LIMIT 3",
)

# Challenge: Select specific row
SELECT_004 = Challenge(
    id="select_004",
    title="Find the Apple",
    description="""
# Find the Apple

Write a query to find the fruit named 'apple'.
Select the `id`, `name`, and `avg_weight` columns.

**Hint:** Use the WHERE clause to filter rows.
""",
    category=ChallengeCategory.FILTERING,
    difficulty=Difficulty.BEGINNER,
    xp_reward=15,
    setup_sql=[
        "CREATE TABLE fruits (id INTEGER PRIMARY KEY, name TEXT, avg_weight INTEGER)",
        "INSERT INTO fruits (id, name, avg_weight) VALUES (1, 'apple', 200)",
        "INSERT INTO fruits (id, name, avg_weight) VALUES (2, 'orange', 140)",
        "INSERT INTO fruits (id, name, avg_weight) VALUES (3, 'banana', 118)",
    ],
    validation_rules=[
        ValidationRule(
            type=ValidationType.EXACT_MATCH,
            expected_value=[
                {"id": 1, "name": "apple", "avg_weight": 200},
            ],
            order_matters=False
        ),
    ],
    hints=[
        "WHERE clause filters which rows are returned",
        "Use = for equality comparison",
        "Text values need single quotes: 'apple'"
    ],
    expected_query="SELECT id, name, avg_weight FROM fruits WHERE name = 'apple'",
    concept_explanation="The WHERE clause filters rows based on conditions. Only rows where the condition is true are included in the results."
)

# Challenge: Numeric comparison
SELECT_005 = Challenge(
    id="select_005",
    title="Light Fruits",
    description="""
# Light Fruits

Find all fruits that weigh less than 150 grams.
Select `name` and `avg_weight`.
""",
    category=ChallengeCategory.FILTERING,
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
            type=ValidationType.CONTAINS_ROWS,
            expected_value=[
                {"name": "orange", "avg_weight": 140},
                {"name": "banana", "avg_weight": 118},
                {"name": "grape", "avg_weight": 5},
            ]
        ),
        ValidationRule(
            type=ValidationType.ROW_COUNT,
            expected_value=3
        ),
    ],
    hints=[
        "Use < for less than comparison",
        "Numbers don't need quotes",
        "WHERE avg_weight < 150"
    ],
    expected_query="SELECT name, avg_weight FROM fruits WHERE avg_weight < 150",
)


# Export all challenges
SELECT_BASICS_CHALLENGES = [
    SELECT_001,
    SELECT_002,
    SELECT_003,
    SELECT_004,
    SELECT_005,
]
