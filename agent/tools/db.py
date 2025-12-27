from agent.schemas.tools import DBQueryInput

def execute_query(input_data: DBQueryInput):
    """
    Mock function to execute a DB query.
    """
    # In a real app, this would execute SQL against a database
    return {
        "columns": ["id", "name"],
        "rows": [
            [1, "Alice"],
            [2, "Bob"]
        ]
    }
