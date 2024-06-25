# KMP Algorithm for searching in SQLite database?
# Boyer-Moore-Algorithm? 
# TODO: Ausprobieren
import sqlite3

def search_database(connection, search_terms, search_fields=["artist", "title", "album"]):
    cursor = connection.cursor()
    if not search_terms:
        return []  # Return an empty list instead of None
    query = "SELECT DISTINCT * FROM audio_files WHERE ("
    placeholders = " OR ".join([f"{field} LIKE ?" for field in search_fields])
    query += placeholders + ") ORDER BY last_modified DESC;"
    
    # Ensure search_terms is a list even if it's a single term
    if isinstance(search_terms, str):
        search_terms = [search_terms]
    
    search_terms = [term.lower() for term in search_terms]
    search_terms_tuple = tuple([f"%{term}%" for term in search_terms] * len(search_fields))

    try:
        cursor.execute(query, search_terms_tuple)
        results = cursor.fetchall()
        return results
    except (Exception, sqlite3.Error) as error:
        print("Error while searching database:", error)
        return []  # Return an empty list instead of None
    finally:
        cursor.close()

