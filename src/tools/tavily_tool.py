from typing import List, Dict, Any
import redis
import json
import redis.exceptions
from tavily import TavilyClient
from crewai.tools import BaseTool
from dotenv import load_dotenv
from src.config.settings import settings
from loguru import logger


load_dotenv()

TAVILY_API_KEY = settings.TAVILY_API_KEY
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY environment variable not set.")

# Tavily Client (using the direct library)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

redis_client = None
try:
    redis_client = redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=True # Decode responses from bytes to strings
    )
    redis_client.ping() # Check the connection
    logger.info(f"✅ Successfully connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
except redis.exceptions.ConnectionError as e:
    logger.info(f"⚠️ Warning: Could not connect to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}. Caching will be disabled. Error: {e}")
    redis_client = None
except Exception as e:
    logger.info(f"⚠️ Warning: An unexpected error occurred during Redis connection. Caching disabled. Error: {e}")
    redis_client = None


class CachedTavilySearchTool(BaseTool):
    name: str = "Tavily Search with Cache"
    description: str = (
        "Performs a Tavily web search for a given query. "
        "Results are cached in Redis to avoid redundant API calls "
        "and conserve credits. Provides comprehensive search results."
    )

    def _run(
        self,
        query: str,
        search_depth: str = "advanced",
        max_results: int = 5
    ) -> Dict:
        """Execute tavily search with Redis caching"""

        # Validate search depth 
        valid_search_depth = search_depth
        if valid_search_depth not in ["basic", "advanced"]:
            logger.warning(f"⚠️ Warning: Invalid search_depth '{search_depth}' received. Defaulting to 'advanced'.")
            valid_search_depth = "advanced"

        # Start search execution 
        logger.info(f"\n🔎 Executing Tavily Search (cached): '{query}'")
        cache_key = f"tavily:{search_depth}:{max_results}:{query}"

        # 1. If cache exists 
        if redis_client: 
            try:
                cached_result_json = redis_client.get(cache_key)
                if cached_result_json:
                    logger.success("✅ Cache HIT! returning cached response.")
                    return {
                        "status": "success",
                        "query": query,
                        "response": cached_result_json,
                        "response_type": "cached"
                    }
            except redis.exceptions.RedisError as e:
                logger.info(f"⚠️ Redis GET Error: {e}. Proceeding without cache.")
            except Exception as e: # Catch other potential errors
                logger.info(f"⚠️ Unexpected error during Redis GET: {e}. Proceeding without cache.")

        # 2. If cache miss
        logger.info("🔍 Cache MISS or Redis unavailable. Calling Tavily API...")
        try:
            # Use Tavily Serch tool for new response
            response = tavily_client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results
            )
            # Convert to json str for storing in Redis
            result_json = json.dumps(response)
        except Exception as e:
            logger.error(f"❌ Error calling Tavily API: {e}")
            return {
                "status": "error",
                "query": query,
                "response": None,
                "details": str(e)
            }

        # 3. Store the json string in Redis
        if redis_client and result_json:
            try:
                redis_client.setex(cache_key, settings.TTL_TIME, result_json)
                logger.info(f"💾 Result stored in Redis cache (TTL: {settings.TTL_TIME}s).")
            except redis.exceptions.RedisError as e:
                logger.warning(f"⚠️ Redis SETEX Error: {e}. Result not cached.")
            except Exception as e: # Catch other potential errors
                logger.warning(f"⚠️ Unexpected error during Redis SETEX: {e}. Result not cached.")

        return {
            "status": "success",
            "query": query,
            "response": result_json,
            "response_type": "generated"
        }
    
# Instance of the custom tool 
cached_tavily_search_tool = CachedTavilySearchTool()


# Example usage
if __name__ == "__main__":
    logger.debug("--- Running standalone test ---")
    test_query = "What are the latest AI trends in production?"

    logger.debug("\n--- First Call (Should be Cache MISS) ---")
    results1 = cached_tavily_search_tool.run(test_query)
    logger.debug("\nResults 1:")
    response1 = results1.get('response')
    print(response1)

    logger.debug("\n--- Second Call (Should be Cache HIT) ---")
    results2 = cached_tavily_search_tool.run(test_query)
    logger.debug("\nResults 2:")
    response2 = results1.get('response')
    print(response2)

    # Verify they are the same (if no errors)
    if response1 == response2 and results1['status'] != "error":
      print("\n✅ SUCCESS: Second call returned the same result from cache.")