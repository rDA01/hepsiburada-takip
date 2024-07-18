import psycopg2
import uuid
from datetime import datetime

class Product:
    def __init__(self, id ,title, link, price, created_at=None, updated_at=None, is_deleted=False):
        if(id == None or str(id) == ''):
            self.id = str(uuid.uuid4())
        else:
            self.id = id
            
        self.title = title
        self.link = link
        self.price = price
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.is_deleted = is_deleted
