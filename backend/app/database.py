import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from backend.app.config import settings

logger = logging.getLogger("documind.database")


class DatabaseManager:
    def __init__(self):
        self._client: Optional[MongoClient] = None
        self._db = None
        self._is_connected = False
        self._connection_error: Optional[str] = None

        # Fallback local in-memory store if MongoDB is not connected
        self._local_documents: Dict[str, Dict[str, Any]] = {}
        self._local_history: List[Dict[str, Any]] = []

        self._connect()

    def _connect(self):
        if not settings.MONGODB_URI:
            self._connection_error = "MONGODB_URI is not set in environment."
            logger.info("MongoDB URI not provided. Operating with in-memory persistence.")
            return

        try:
            self._client = MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=4000,
                connectTimeoutMS=4000,
            )
            # Trigger server selection to verify connectivity
            self._client.admin.command("ping")
            self._db = self._client[settings.MONGODB_DB_NAME]
            self._is_connected = True
            self._connection_error = None
            logger.info(f"Connected to MongoDB Atlas database: {settings.MONGODB_DB_NAME}")

            # Ensure indexes
            self._db.documents.create_index([("document_id", ASCENDING)], unique=True)
            self._db.documents.create_index([("upload_timestamp", DESCENDING)])
            self._db.question_history.create_index([("interaction_id", ASCENDING)], unique=True)
            self._db.question_history.create_index([("document_id", ASCENDING)])
            self._db.question_history.create_index([("timestamp", DESCENDING)])
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
            self._is_connected = False
            self._connection_error = f"Failed to connect to MongoDB Atlas: {str(e)}"
            logger.warning(f"MongoDB connection failed: {e}. Using in-memory store.")

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def connection_error(self) -> Optional[str]:
        return self._connection_error

    # Documents operations
    def save_document(self, doc_data: Dict[str, Any]) -> bool:
        doc_data.setdefault("upload_timestamp", datetime.now(timezone.utc).isoformat())
        doc_id = doc_data["document_id"]

        if self._is_connected and self._db is not None:
            try:
                self._db.documents.update_one(
                    {"document_id": doc_id},
                    {"$set": doc_data},
                    upsert=True,
                )
                return True
            except Exception as e:
                logger.error(f"Error saving document to MongoDB: {e}")
                self._local_documents[doc_id] = doc_data
                return False
        else:
            self._local_documents[doc_id] = doc_data
            return True

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        if self._is_connected and self._db is not None:
            try:
                res = self._db.documents.find_one({"document_id": doc_id}, {"_id": 0})
                if res:
                    return res
            except Exception as e:
                logger.error(f"Error fetching document from MongoDB: {e}")
        return self._local_documents.get(doc_id)

    def list_documents(self) -> List[Dict[str, Any]]:
        if self._is_connected and self._db is not None:
            try:
                cursor = self._db.documents.find({}, {"_id": 0}).sort("upload_timestamp", DESCENDING)
                return list(cursor)
            except Exception as e:
                logger.error(f"Error listing documents from MongoDB: {e}")
        return sorted(
            list(self._local_documents.values()),
            key=lambda d: d.get("upload_timestamp", ""),
            reverse=True,
        )

    def delete_document(self, doc_id: str) -> bool:
        deleted = False
        if self._is_connected and self._db is not None:
            try:
                res = self._db.documents.delete_one({"document_id": doc_id})
                self._db.question_history.delete_many({"document_id": doc_id})
                deleted = res.deleted_count > 0
            except Exception as e:
                logger.error(f"Error deleting document from MongoDB: {e}")
        
        if doc_id in self._local_documents:
            del self._local_documents[doc_id]
            self._local_history = [h for h in self._local_history if h.get("document_id") != doc_id]
            deleted = True

        return deleted

    # Question history operations
    def save_history(self, history_data: Dict[str, Any]) -> bool:
        history_data.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        interaction_id = history_data["interaction_id"]

        if self._is_connected and self._db is not None:
            try:
                self._db.question_history.update_one(
                    {"interaction_id": interaction_id},
                    {"$set": history_data},
                    upsert=True,
                )
                return True
            except Exception as e:
                logger.error(f"Error saving history to MongoDB: {e}")
                self._local_history.append(history_data)
                return False
        else:
            self._local_history.append(history_data)
            return True

    def list_history(self, document_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        if self._is_connected and self._db is not None:
            try:
                query = {"document_id": document_id} if document_id else {}
                cursor = (
                    self._db.question_history.find(query, {"_id": 0})
                    .sort("timestamp", DESCENDING)
                    .limit(limit)
                )
                return list(cursor)
            except Exception as e:
                logger.error(f"Error listing history from MongoDB: {e}")

        records = self._local_history
        if document_id:
            records = [r for r in records if r.get("document_id") == document_id]
        records = sorted(records, key=lambda r: r.get("timestamp", ""), reverse=True)
        return records[:limit]

    def get_interaction(self, interaction_id: str) -> Optional[Dict[str, Any]]:
        if self._is_connected and self._db is not None:
            try:
                res = self._db.question_history.find_one({"interaction_id": interaction_id}, {"_id": 0})
                if res:
                    return res
            except Exception as e:
                logger.error(f"Error getting interaction from MongoDB: {e}")
        for item in self._local_history:
            if item.get("interaction_id") == interaction_id:
                return item
        return None

    def clear_history(self, document_id: Optional[str] = None) -> int:
        count = 0
        if self._is_connected and self._db is not None:
            try:
                query = {"document_id": document_id} if document_id else {}
                res = self._db.question_history.delete_many(query)
                count = res.deleted_count
            except Exception as e:
                logger.error(f"Error clearing history in MongoDB: {e}")
        
        if document_id:
            orig_len = len(self._local_history)
            self._local_history = [h for h in self._local_history if h.get("document_id") != document_id]
            count += orig_len - len(self._local_history)
        else:
            count += len(self._local_history)
            self._local_history.clear()

        return count


db_manager = DatabaseManager()
