def get_distinct_companies_max_year(conn):
    query = """
        SELECT DISTINCT company, MAX(year) AS max_year
        FROM your_table
        GROUP BY company;
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
    
    return results  # Returns a list of tuples (company, max_year)

## Example usage
# companies_max_year = get_distinct_companies_max_year(conn)
# for company, max_year in companies_max_year:
#     print(f"Company: {company}, Max Year: {max_year}")
