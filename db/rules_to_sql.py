from datetime import datetime, timedelta
from typing import Tuple, List

def rules_to_sql_query(rules_data: dict) -> Tuple[str, List]:
    """
    Convert JSON rules into a SQL query with parameters.
    
    Returns:
        query (str): SQL query string with placeholders
        params (list): List of parameters for the query
    """
    rules_predicate = rules_data.get("rules_predicate", "all").lower()
    conditions = rules_data.get("rules", [])
    
    sql_clauses = []
    params = []

    for cond in conditions:
        field = cond["field"].lower()
        predicate = cond["predicate"].lower()
        value = cond["value"]

        if field in ("sender", "recipient", "subject", "body", "snippet"):
            if predicate == "contains":
                sql_clauses.append(f"{field} LIKE ?")
                params.append(f"%{value}%")
            elif predicate == "does_not_contain":
                sql_clauses.append(f"{field} NOT LIKE ?")
                params.append(f"%{value}%")
            elif predicate == "equals":
                sql_clauses.append(f"{field} = ?")
                params.append(value)
            elif predicate == "does_not_equal":
                sql_clauses.append(f"{field} != ?")
                params.append(value)
            else:
                raise ValueError(f"Unknown string predicate: {predicate}")

        elif field == "received_at":
            number, unit = value.split()
            number = int(number)
            if unit.lower().startswith("month"):
                delta_days = number * 30
            else:
                delta_days = number

            if predicate == "less_than":
                sql_clauses.append(f"{field} >= datetime('now', ?)")
                params.append(f"-{delta_days} days")
            elif predicate == "greater_than":
                sql_clauses.append(f"{field} <= datetime('now', ?)")
                params.append(f"-{delta_days} days")
            else:
                raise ValueError(f"Unknown date predicate: {predicate}")

        else:
            raise ValueError(f"Unknown field: {field}")

    connector = " AND " if rules_predicate == "all" else " OR "
    where_clause = connector.join(sql_clauses) if sql_clauses else "1=1"

    query = f"SELECT * FROM emails WHERE {where_clause};"
    return query, params
