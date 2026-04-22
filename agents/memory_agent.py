"""
Memory Agent for storing and retrieving past interactions using vector database.
Uses FAISS for efficient similarity search and storage.
"""

import logging
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np

# Try to import FAISS, fallback to simple storage if not available
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS or sentence-transformers not available. Using simple JSON storage.")

from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool

logger = logging.getLogger(__name__)

class MemoryAgent:
    """Agent responsible for storing and retrieving past interactions."""

    def __init__(self, llm_model: str = "gpt-3.5-turbo", temperature: float = 0.1,
                 index_path: str = "memory/faiss_index"):
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature)
        self.index_path = index_path
        self.dimension = 384  # Default for sentence-transformers/all-MiniLM-L6-v2

        # Initialize storage
        self._init_storage()

        # Initialize tools for the agent
        self.tools = [
            Tool(
                name="StoreInteraction",
                func=self._store_interaction_wrapper,
                description="Store an email interaction (sent, opened, replied) for future learning. Input should contain interaction details."
            ),
            Tool(
                name="RetrieveSimilarInteractions",
                func=self._retrieve_similar_wrapper,
                description="Retrieve similar past interactions based on prospect profile or email content. Input should contain search query."
            ),
            Tool(
                name="GetPerformanceStats",
                func=self._get_performance_stats_wrapper,
                description="Get performance statistics for email campaigns. Input should contain optional filters."
            )
        ]

        # Initialize memory
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Initialize the agent
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )

        logger.info(f"Memory Agent initialized with {'FAISS' if FAISS_AVAILABLE else 'JSON'} storage")

    def _init_storage(self):
        """Initialize storage backend."""
        # Create memory directory if it doesn't exist
        os.makedirs(self.index_path, exist_ok=True)

        if FAISS_AVAILABLE:
            # Initialize FAISS index
            self.index_file = os.path.join(self.index_path, "index.faiss")
            self.metadata_file = os.path.join(self.index_path, "metadata.json")

            # Try to load existing index
            if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
                try:
                    self.index = faiss.read_index(self.index_file)
                    with open(self.metadata_file, 'r') as f:
                        self.metadata = json.load(f)
                    logger.info(f"Loaded existing FAISS index with {len(self.metadata)} entries")
                except Exception as e:
                    logger.error(f"Error loading existing index: {e}")
                    self._create_new_index()
            else:
                self._create_new_index()

            # Initialize sentence transformer for embeddings
            try:
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Sentence transformer model loaded")
            except Exception as e:
                logger.error(f"Error loading sentence transformer: {e}")
                self.embedder = None
                FAISS_AVAILABLE = False  # Fallback to JSON
        else:
            # Simple JSON storage
            self.storage_file = os.path.join(self.index_path, "interactions.json")
            self.metadata = []
            if os.path.exists(self.storage_file):
                try:
                    with open(self.storage_file, 'r') as f:
                        self.metadata = json.load(f)
                    logger.info(f"Loaded {len(self.metadata)} interactions from JSON storage")
                except Exception as e:
                    logger.error(f"Error loading JSON storage: {e}")
                    self.metadata = []

    def _create_new_index(self):
        """Create a new FAISS index."""
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for similarity
        self.metadata = []
        logger.info("Created new FAISS index")

    def _store_interaction_wrapper(self, query: str) -> str:
        """Wrapper for storing interactions."""
        try:
            # Parse interaction data (expected JSON string)
            interaction_data = json.loads(query)
            success = self.store_interaction(interaction_data)
            return f"Interaction stored successfully: {success}"
        except json.JSONDecodeError:
            # Treat as plain text description
            interaction_data = {
                "description": query,
                "timestamp": datetime.now().isoformat()
            }
            success = self.store_interaction(interaction_data)
            return f"Interaction stored successfully: {success}"
        except Exception as e:
            logger.error(f"Error storing interaction: {str(e)}")
            return f"Error storing interaction: {str(e)}"

    def _retrieve_similar_wrapper(self, query: str) -> str:
        """Wrapper for retrieving similar interactions."""
        try:
            # Parse query - could be plain text or JSON
            try:
                query_data = json.loads(query)
                search_text = query_data.get("query", str(query_data))
                limit = query_data.get("limit", 5)
            except json.JSONDecodeError:
                search_text = query
                limit = 5

            similar_interactions = self.retrieve_similar_interactions(search_text, limit)
            return f"Found {len(similar_interactions)} similar interactions:\n{json.dumps(similar_interactions, indent=2)}"
        except Exception as e:
            logger.error(f"Error retrieving similar interactions: {str(e)}")
            return f"Error retrieving similar interactions: {str(e)}"

    def _get_performance_stats_wrapper(self, query: str) -> str:
        """Wrapper for getting performance stats."""
        try:
            # Parse optional filters
            try:
                filters = json.loads(query) if query.strip() else {}
            except json.JSONDecodeError:
                filters = {}

            stats = self.get_performance_stats(filters)
            return f"Performance Statistics:\n{json.dumps(stats, indent=2)}"
        except Exception as e:
            logger.error(f"Error getting performance stats: {str(e)}")
            return f"Error getting performance stats: {str(e)}"

    def store_interaction(self, interaction_data: Dict[str, Any]) -> bool:
        """
        Store an email interaction for future learning.

        Args:
            interaction_data: Dictionary containing interaction details

        Returns:
            True if stored successfully, False otherwise
        """
        logger.info("Storing email interaction")

        try:
            # Add timestamp if not present
            if "timestamp" not in interaction_data:
                interaction_data["timestamp"] = datetime.now().isoformat()

            # Add unique ID
            interaction_data["id"] = self._generate_interaction_id(interaction_data)

            if FAISS_AVAILABLE and self.embedder:
                # Create embedding for the interaction
                text_to_embed = self._create_interaction_text(interaction_data)
                embedding = self.embedder.encode([text_to_embed])

                # Normalize for inner product
                faiss.normalize_L2(embedding)

                # Add to index
                self.index.add(embedding.astype('float32'))
                self.metadata.append(interaction_data)

                # Save index and metadata
                faiss.write_index(self.index, self.index_file)
                with open(self.metadata_file, 'w') as f:
                    json.dump(self.metadata, f, indent=2)

                logger.info(f"Stored interaction with FAISS. Total interactions: {len(self.metadata)}")
            else:
                # Simple JSON storage
                self.metadata.append(interaction_data)
                with open(self.storage_file, 'w') as f:
                    json.dump(self.metadata, f, indent=2)

                logger.info(f"Stored interaction with JSON. Total interactions: {len(self.metadata)}")

            return True

        except Exception as e:
            logger.error(f"Error storing interaction: {str(e)}")
            return False

    def retrieve_similar_interactions(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve similar past interactions based on query.

        Args:
            query: Search query text
            limit: Maximum number of results to return

        Returns:
            List of similar interaction dictionaries
        """
        logger.info(f"Retrieving similar interactions for query: {query[:50]}...")

        try:
            if FAISS_AVAILABLE and self.embedder and len(self.metadata) > 0:
                # Create embedding for query
                query_embedding = self.embedder.encode([query])
                faiss.normalize_L2(query_embedding)

                # Search index
                scores, indices = self.index.search(query_embedding.astype('float32'), min(limit, len(self.metadata)))

                # Retrieve results
                results = []
                for score, idx in zip(scores[0], indices[0]):
                    if idx < len(self.metadata):  # Safety check
                        interaction = self.metadata[idx].copy()
                        interaction["similarity_score"] = float(score)
                        results.append(interaction)

                logger.info(f"Retrieved {len(results)} similar interactions using FAISS")
                return results
            else:
                # Simple text matching for JSON storage
                query_lower = query.lower()
                results = []

                for interaction in self.metadata:
                    # Convert interaction to text for matching
                    interaction_text = json.dumps(interaction).lower()
                    if query_lower in interaction_text:
                        results.append(interaction)
                        if len(results) >= limit:
                            break

                logger.info(f"Retrieved {len(results)} similar interactions using text matching")
                return results[:limit]

        except Exception as e:
            logger.error(f"Error retrieving similar interactions: {str(e)}")
            return []

    def get_performance_stats(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get performance statistics for email campaigns.

        Args:
            filters: Optional filters to apply (e.g., date range, campaign tags)

        Returns:
            Dictionary containing performance statistics
        """
        logger.info("Getting performance statistics")

        try:
            if not self.metadata:
                return {
                    "total_interactions": 0,
                    "message": "No interactions stored yet"
                }

            # Apply filters if provided
            filtered_data = self.metadata
            if filters:
                filtered_data = self._apply_filters(self.metadata, filters)

            if not filtered_data:
                return {
                    "total_interactions": 0,
                    "filtered_count": 0,
                    "message": "No interactions match the filters"
                }

            # Calculate statistics
            total = len(filtered_data)
            sent_count = sum(1 for i in filtered_data if i.get("status") == "sent")
            opened_count = sum(1 for i in filtered_data if i.get("status") == "opened")
            replied_count = sum(1 for i in filtered_data if i.get("status") == "replied")
            bounced_count = sum(1 for i in filtered_data if i.get("status") == "bounced")

            # Calculate rates
            open_rate = (opened_count / sent_count * 100) if sent_count > 0 else 0
            reply_rate = (replied_count / sent_count * 100) if sent_count > 0 else 0
            bounce_rate = (bounced_count / sent_count * 100) if sent_count > 0 else 0

            # Analyze by subject line characteristics (if available)
            subject_analysis = self._analyze_subject_performance(filtered_data)

            # Analyze by send time (if available)
            time_analysis = self._analyze_send_time_performance(filtered_data)

            stats = {
                "total_interactions": total,
                "sent_count": sent_count,
                "opened_count": opened_count,
                "replied_count": replied_count,
                "bounced_count": bounced_count,
                "open_rate": round(open_rate, 2),
                "reply_rate": round(reply_rate, 2),
                "bounce_rate": round(bounce_rate, 2),
                "subject_analysis": subject_analysis,
                "send_time_analysis": time_analysis,
                "date_range": self._get_date_range(filtered_data),
                "filters_applied": filters or {}
            }

            logger.info(f"Calculated performance stats for {total} interactions")
            return stats

        except Exception as e:
            logger.error(f"Error getting performance stats: {str(e)}")
            return {
                "error": str(e),
                "total_interactions": len(self.metadata) if self.metadata else 0
            }

    def _create_interaction_text(self, interaction_data: Dict[str, Any]) -> str:
        """Create text representation of interaction for embedding."""
        text_parts = []

        # Add key fields that would be useful for similarity matching
        for key in ["subject", "body", "prospect_name", "prospect_title", "company", "industry"]:
            if key in interaction_data and interaction_data[key]:
                text_parts.append(f"{key}: {interaction_data[key]}")

        # Add status/outcome
        if "status" in interaction_data:
            text_parts.append(f"status: {interaction_data['status']}")

        return " | ".join(text_parts)

    def _generate_interaction_id(self, interaction_data: Dict[str, Any]) -> str:
        """Generate a unique ID for an interaction."""
        import hashlib
        # Create a string from key fields
        key_fields = [
            interaction_data.get("prospect_email", ""),
            interaction_data.get("subject", ""),
            interaction_data.get("timestamp", "")
        ]
        key_string = "|".join(key_fields)
        return hashlib.md5(key_string.encode()).hexdigest()[:12]

    def _apply_filters(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to interaction data."""
        filtered = data

        for key, value in filters.items():
            if key == "date_range" and isinstance(value, dict):
                start_date = value.get("start")
                end_date = value.get("end")
                if start_date or end_date:
                    filtered = [
                        item for item in filtered
                        if self._is_in_date_range(item.get("timestamp"), start_date, end_date)
                    ]
            elif key == "status":
                if isinstance(value, list):
                    filtered = [item for item in filtered if item.get("status") in value]
                else:
                    filtered = [item for item in filtered if item.get("status") == value]
            elif key == "prospect_industry":
                if isinstance(value, list):
                    filtered = [item for item in filtered if item.get("prospect_industry") in value]
                else:
                    filtered = [item for item in filtered if item.get("prospect_industry") == value]
            # Add more filters as needed

        return filtered

    def _is_in_date_range(self, timestamp_str: Optional[str], start_date: Optional[str], end_date: Optional[str]) -> bool:
        """Check if timestamp is within date range."""
        if not timestamp_str:
            return False

        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

            if start_date:
                start = datetime.fromisoformat(start_date)
                if timestamp < start:
                    return False

            if end_date:
                end = datetime.fromisoformat(end_date)
                if timestamp > end:
                    return False

            return True
        except:
            return False

    def _analyze_subject_performance(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance by subject line characteristics."""
        # Simple analysis - in reality would use more sophisticated NLP
        subjects = [i.get("subject", "") for i in interactions if i.get("subject")]

        if not subjects:
            return {"message": "No subject lines available for analysis"}

        # Check for personalization indicators
        personalized_count = sum(1 for s in subjects if any(
            indicator in s.lower() for indicator in ["{", "}", "first_name", "company", "name"]
        ))

        # Check for question marks
        question_count = sum(1 for s in subjects if "?" in s)

        # Check length
        avg_length = sum(len(s) for s in subjects) / len(subjects)

        return {
            "total_subjects_analyzed": len(subjects),
            "personalized_subjects": personalized_count,
            "question_subjects": question_count,
            "average_length": round(avg_length, 1),
            "personalization_rate": round(personalized_count / len(subjects) * 100, 1) if subjects else 0
        }

    def _analyze_send_time_performance(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance by send time."""
        # Extract hours from timestamps
        hours = []
        weekdays = []

        for interaction in interactions:
            timestamp_str = interaction.get("timestamp")
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    hours.append(timestamp.hour)
                    weekdays.append(timestamp.weekday())  # Monday=0, Sunday=6
                except:
                    pass

        if not hours:
            return {"message": "No timestamp data available for analysis"}

        # Find most common hour and weekday
        from collections import Counter
        hour_counts = Counter(hours)
        weekday_counts = Counter(weekdays)

        best_hour = hour_counts.most_common(1)[0][0] if hour_counts else None
        best_weekday = weekday_counts.most_common(1)[0][0] if weekday_counts else None

        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        return {
            "total_timestamps_analyzed": len(hours),
            "best_send_hour": best_hour,
            "best_send_weekday": weekday_names[best_weekday] if best_weekday is not None else None,
            "hour_distribution": dict(hour_counts),
            "weekday_distribution": {weekday_names[k]: v for k, v in weekday_counts.items()}
        }

    def _get_date_range(self, interactions: List[Dict[str, Any]]) -> Dict[str, Optional[str]]:
        """Get date range of interactions."""
        dates = []
        for interaction in interactions:
            timestamp_str = interaction.get("timestamp")
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    dates.append(timestamp)
                except:
                    pass

        if not dates:
            return {"start": None, "end": None}

        return {
            "start": min(dates).isoformat(),
            "end": max(dates).isoformat()
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_memory_summary(self) -> str:
        """Get a formatted summary of the memory system."""
        if FAISS_AVAILABLE:
            storage_type = "FAISS Vector Database"
            count = len(self.metadata) if self.metadata else 0
        else:
            storage_type = "JSON Storage"
            count = len(self.metadata) if self.metadata else 0

        return f"""
Memory System Summary:
- Storage Type: {storage_type}
- Total Interactions Stored: {count}
- Index Path: {self.index_path}
- Embedding Model: {'all-MiniLM-L6-v2' if FAISS_AVAILABLE and self.embedder else 'None (text matching)'}
- Last Updated: {self._get_timestamp()}
        """.strip()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize agent
    agent = MemoryAgent()

    # Test storing an interaction
    test_interaction = {
        "prospect_name": "John Doe",
        "prospect_title": "VP of Engineering",
        "prospect_company": "Acme Corp",
        "subject": "Quick question about Acme Corp's engineering challenges",
        "body": "Hi John, I noticed Acme Corp recently launched an AI-powered product...",
        "status": "sent",
        "email": "john.doe@acmecorp.com"
    }

    store_result = agent.store_interaction(test_interaction)
    print(f"Store Result: {store_result}")

    # Test retrieving similar interactions
    similar_result = agent.retrieve_similar_interactions("VP of Engineering Acme Corp", limit=3)
    print(f"Similar Interactions: {similar_result}")

    # Test getting performance stats
    stats_result = agent.get_performance_stats({})
    print(f"Performance Stats: {json.dumps(stats_result, indent=2)}")

    # Print memory summary
    print("\n" + agent.get_memory_summary())