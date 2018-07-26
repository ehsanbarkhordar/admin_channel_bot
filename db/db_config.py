import os


class DatabaseConfig:
    db_string_main = 'postgresql://{}:{}@{}:{}/{}'
    db_string = db_string_main.format(os.environ.get('POSTGRES_USER', None) or "ehsan",
                                      os.environ.get('POSTGRES_PASSWORD', None) or "ehsan1379",
                                      os.environ.get('POSTGRES_HOST', None) or "localhost",
                                      os.environ.get('POSTGRES_PORT', None) or "5432",
                                      os.environ.get('POSTGRES_DB', None) or "admin_channel")
