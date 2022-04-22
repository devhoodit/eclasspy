from .client import client

def login(id, password):
    return client(id, password)