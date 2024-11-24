from pymongo import MongoClient
from neo4j import GraphDatabase
from app.core.config import settings

# MongoDB setup
mongo_client = MongoClient(settings.MONGO_URI)
trace_collection = mongo_client[settings.MONGO_DB]["traces"]

# Neo4j setup
neo4j_driver = GraphDatabase.driver(
    settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
)
