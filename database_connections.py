import psycopg2


def get_db_connection(db_uri):
    """ 
        Connect to the database
        Parameters: db_uri (str): The URI of the database
        Returns: conn (psycopg2.extensions.connection): The connection object    
    """
    conn = psycopg2.connect(db_uri)
    return conn
