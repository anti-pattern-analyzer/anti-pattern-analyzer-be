from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from neo4j import GraphDatabase
from app.core.config import settings

mongo_client = None
trace_collection = None
neo4j_driver = None


async def initialize_mongo():
    global mongo_client, trace_collection
    try:
        mongo_client = MongoClient(settings.MONGO_URI)
        mongo_client.admin.command("ping")
        trace_collection = mongo_client[settings.MONGO_DB]["traces"]
        print("MongoDB connected successfully.")
    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
        raise e


async def close_mongo():
    global mongo_client
    if mongo_client is not None:
        mongo_client.close()
        print("MongoDB connection closed.")
    else:
        print("MongoDB client was not initialized.")


def initialize_neo4j():
    global neo4j_driver
    try:
        neo4j_driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        with neo4j_driver.session() as session:
            session.run("RETURN 1")
        print("Neo4j connected successfully.")
    except Exception as e:
        print(f"Neo4j connection failed: {e}")
        raise e


def close_neo4j():
    global neo4j_driver
    if neo4j_driver is not None:
        neo4j_driver.close()
        print("Neo4j connection closed.")
    else:
        print("Neo4j driver was not initialized.")
