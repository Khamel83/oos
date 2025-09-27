#!/usr/bin/env python3
"""
GoogleSearchFallback module with rate limiting and circuit breaker
Provides reliable Google Custom Search API integration with fallback mechanisms
"""

import json
import time
import logging
import requests
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from queue import Queue, Empty
import hashlib
import os
from enum import Enum

class CircuitBreakerState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"          # Circuit breaker tripped
    HALF_OPEN = "half_open" # Testing if service recovered

@dataclass
class SearchRequest:
    """Container for search requests"""
    query: str
    cx: str
    api_key: str
    num_results: int = 10
    start_index: int = 1
    timestamp: datetime = None
    retry_count: int = 0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class SearchResponse:
    """Container for search responses"""
    success: bool
    query: str
    results: List[Dict] = None
    error_message: str = None
    response_time: float = 0.0
    cached: bool = False
    rate_limited: bool = False
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.results is None:
            self.results = []

class RateLimiter:
    """Rate limiter with token bucket algorithm"""

    def __init__(self, max_requests_per_day: int = 8000):
        self.max_requests = max_requests_per_day
        self.requests_made = 0
        self.last_reset = datetime.now().date()
        self.min_interval = 86400 / max_requests_per_day  # seconds between requests
        self.last_request_time = 0.0
        self.lock = threading.Lock()

    def can_make_request(self) -> bool:
        """Check if a request can be made without violating rate limits"""
        with self.lock:
            current_date = datetime.now().date()

            # Reset daily counter if new day
            if current_date > self.last_reset:
                self.requests_made = 0
                self.last_reset = current_date

            # Check daily limit
            if self.requests_made >= self.max_requests:
                return False

            # Check minimum interval between requests
            current_time = time.time()
            time_since_last = current_time - self.last_request_time

            if time_since_last < self.min_interval:
                return False

            return True

    def wait_if_needed(self) -> float:
        """Wait if necessary to respect rate limits, return wait time"""
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time

            if time_since_last < self.min_interval:
                wait_time = self.min_interval - time_since_last
                time.sleep(wait_time)
                return wait_time

            return 0.0

    def record_request(self):
        """Record that a request was made"""
        with self.lock:
            self.requests_made += 1
            self.last_request_time = time.time()

    def get_status(self) -> Dict:
        """Get current rate limiter status"""
        with self.lock:
            current_date = datetime.now().date()
            if current_date > self.last_reset:
                requests_today = 0
            else:
                requests_today = self.requests_made

            return {
                'requests_made_today': requests_today,
                'daily_limit': self.max_requests,
                'remaining_requests': max(0, self.max_requests - requests_today),
                'min_interval_seconds': self.min_interval,
                'last_request_time': self.last_request_time,
                'can_make_request': self.can_make_request()
            }

class CircuitBreaker:
    """Circuit breaker to prevent cascade failures"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self.half_open_calls = 0
        self.lock = threading.Lock()

    def can_execute(self) -> bool:
        """Check if requests can be executed"""
        with self.lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.OPEN:
                # Check if recovery timeout has passed
                if (self.last_failure_time and
                    datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)):
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.half_open_calls = 0
                    return True
                return False
            elif self.state == CircuitBreakerState.HALF_OPEN:
                return self.half_open_calls < self.half_open_max_calls

            return False

    def record_success(self):
        """Record a successful operation"""
        with self.lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.half_open_calls += 1
                if self.half_open_calls >= self.half_open_max_calls:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    self.last_failure_time = None
            elif self.state == CircuitBreakerState.CLOSED:
                self.failure_count = max(0, self.failure_count - 1)

    def record_failure(self):
        """Record a failed operation"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
            elif self.state == CircuitBreakerState.CLOSED:
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitBreakerState.OPEN

    def get_status(self) -> Dict:
        """Get current circuit breaker status"""
        with self.lock:
            return {
                'state': self.state.value,
                'failure_count': self.failure_count,
                'failure_threshold': self.failure_threshold,
                'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
                'can_execute': self.can_execute()
            }

class SearchCache:
    """Simple in-memory cache for search results"""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Tuple[SearchResponse, datetime]] = {}
        self.lock = threading.Lock()

    def _generate_key(self, request: SearchRequest) -> str:
        """Generate cache key for request"""
        key_data = f"{request.query}:{request.cx}:{request.num_results}:{request.start_index}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, request: SearchRequest) -> Optional[SearchResponse]:
        """Get cached response if available and not expired"""
        with self.lock:
            key = self._generate_key(request)

            if key in self.cache:
                response, cache_time = self.cache[key]

                # Check if expired
                if datetime.now() - cache_time > timedelta(seconds=self.ttl_seconds):
                    del self.cache[key]
                    return None

                # Return cached response
                cached_response = SearchResponse(**asdict(response))
                cached_response.cached = True
                return cached_response

            return None

    def put(self, request: SearchRequest, response: SearchResponse):
        """Cache a response"""
        with self.lock:
            key = self._generate_key(request)

            # Ensure we don't exceed max size
            if len(self.cache) >= self.max_size:
                # Remove oldest entry
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]

            self.cache[key] = (response, datetime.now())

    def clear(self):
        """Clear all cached entries"""
        with self.lock:
            self.cache.clear()

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'ttl_seconds': self.ttl_seconds
            }

class GoogleSearchFallback:
    """Google Custom Search API client with rate limiting and circuit breaker"""

    def __init__(self, config_path: str = "data/google_search_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = self._setup_logging()

        # Initialize components
        self.rate_limiter = RateLimiter(max_requests_per_day=self.config["rate_limit"]["max_requests_per_day"])
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.config["circuit_breaker"]["failure_threshold"],
            recovery_timeout=self.config["circuit_breaker"]["recovery_timeout"],
            half_open_max_calls=self.config["circuit_breaker"]["half_open_max_calls"]
        )
        self.cache = SearchCache(
            max_size=self.config["cache"]["max_size"],
            ttl_seconds=self.config["cache"]["ttl_seconds"]
        )

        # Request queue for throttling
        self.request_queue = Queue()
        self.queue_processor_thread = None
        self.shutdown_flag = threading.Event()

        # Statistics tracking
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cached_requests': 0,
            'rate_limited_requests': 0,
            'circuit_breaker_rejected': 0,
            'start_time': datetime.now()
        }
        self.stats_lock = threading.Lock()

        self._start_queue_processor()

    def _load_config(self) -> Dict:
        """Load configuration from file"""
        default_config = {
            "api": {
                "base_url": "https://www.googleapis.com/customsearch/v1",
                "timeout": 30,
                "max_retries": 3,
                "backoff_factor": 2.0
            },
            "rate_limit": {
                "max_requests_per_day": 10,  # SAFETY: Maximum 10 queries per day ($0.05)
                "burst_allowance": 2
            },
            "circuit_breaker": {
                "failure_threshold": 5,
                "recovery_timeout": 60,
                "half_open_max_calls": 3
            },
            "cache": {
                "max_size": 1000,
                "ttl_seconds": 3600
            },
            "credentials": {
                "api_key": os.getenv("GOOGLE_SEARCH_API_KEY", ""),
                "search_engine_id": os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
            },
            "logging": {
                "level": "INFO",
                "file": "data/google_search.log"
            }
        }

        try:
            if Path(self.config_path).exists():
                with open(self.config_path) as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                    elif isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if subkey not in config[key]:
                                config[key][subkey] = subvalue
                return config
            else:
                self._save_config(default_config)
                return default_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return default_config

    def _save_config(self, config: Dict):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for Google Search client"""
        logger = logging.getLogger('google_search_fallback')
        logger.setLevel(getattr(logging, self.config["logging"]["level"]))

        if not logger.handlers:
            log_file = self.config["logging"]["file"]
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _start_queue_processor(self):
        """Start background thread to process search requests"""
        if self.queue_processor_thread is None or not self.queue_processor_thread.is_alive():
            self.queue_processor_thread = threading.Thread(
                target=self._process_request_queue,
                daemon=True
            )
            self.queue_processor_thread.start()

    def _process_request_queue(self):
        """Background thread to process queued search requests"""
        while not self.shutdown_flag.is_set():
            try:
                # Get request from queue with timeout
                request, result_queue = self.request_queue.get(timeout=1.0)

                # Process the request
                response = self._execute_search_request(request)
                result_queue.put(response)

                self.request_queue.task_done()

            except Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in queue processor: {e}")

    def _execute_search_request(self, request: SearchRequest) -> SearchResponse:
        """Execute a single search request"""
        start_time = time.time()

        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            with self.stats_lock:
                self.stats['circuit_breaker_rejected'] += 1

            self.logger.warning("Request rejected by circuit breaker")
            return SearchResponse(
                success=False,
                query=request.query,
                error_message="Service temporarily unavailable (circuit breaker open)",
                response_time=time.time() - start_time
            )

        # Check rate limits
        if not self.rate_limiter.can_make_request():
            with self.stats_lock:
                self.stats['rate_limited_requests'] += 1

            self.logger.warning("Request rate limited")
            return SearchResponse(
                success=False,
                query=request.query,
                error_message="Rate limit exceeded",
                response_time=time.time() - start_time,
                rate_limited=True
            )

        # Wait for rate limiting
        wait_time = self.rate_limiter.wait_if_needed()
        if wait_time > 0:
            self.logger.debug(f"Waited {wait_time:.2f}s for rate limiting")

        # Make the API request
        try:
            response = self._make_api_request(request)

            # Record success
            self.circuit_breaker.record_success()
            self.rate_limiter.record_request()

            with self.stats_lock:
                self.stats['successful_requests'] += 1

            response.response_time = time.time() - start_time
            return response

        except Exception as e:
            # Record failure
            self.circuit_breaker.record_failure()

            with self.stats_lock:
                self.stats['failed_requests'] += 1

            self.logger.error(f"Search request failed: {e}")

            return SearchResponse(
                success=False,
                query=request.query,
                error_message=str(e),
                response_time=time.time() - start_time
            )

    def _make_api_request(self, request: SearchRequest) -> SearchResponse:
        """Make the actual API request to Google Custom Search"""
        params = {
            'key': request.api_key,
            'cx': request.cx,
            'q': request.query,
            'num': request.num_results,
            'start': request.start_index
        }

        max_retries = self.config["api"]["max_retries"]
        backoff_factor = self.config["api"]["backoff_factor"]

        for attempt in range(max_retries + 1):
            try:
                response = requests.get(
                    self.config["api"]["base_url"],
                    params=params,
                    timeout=self.config["api"]["timeout"]
                )

                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])

                    # Parse results
                    results = []
                    for item in items:
                        results.append({
                            'title': item.get('title', ''),
                            'link': item.get('link', ''),
                            'snippet': item.get('snippet', ''),
                            'displayLink': item.get('displayLink', '')
                        })

                    return SearchResponse(
                        success=True,
                        query=request.query,
                        results=results
                    )

                elif response.status_code == 429:  # Rate limited
                    if attempt < max_retries:
                        wait_time = backoff_factor ** attempt
                        self.logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"Rate limited after {max_retries} retries")

                else:
                    error_msg = f"API request failed with status {response.status_code}: {response.text}"
                    raise Exception(error_msg)

            except requests.RequestException as e:
                if attempt < max_retries:
                    wait_time = backoff_factor ** attempt
                    self.logger.warning(f"Request failed, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Request failed after {max_retries} retries: {e}")

        raise Exception("Unexpected error in API request")

    def search(self, query: str, num_results: int = 10, start_index: int = 1,
              api_key: str = None, search_engine_id: str = None) -> SearchResponse:
        """
        Perform a search with rate limiting and circuit breaker protection

        Args:
            query: Search query string
            num_results: Number of results to return (1-10)
            start_index: Starting index for results
            api_key: Google API key (uses config default if not provided)
            search_engine_id: Search engine ID (uses config default if not provided)

        Returns:
            SearchResponse object with results or error information
        """
        with self.stats_lock:
            self.stats['total_requests'] += 1

        # Use default credentials if not provided
        if api_key is None:
            api_key = self.config["credentials"]["api_key"]
        if search_engine_id is None:
            search_engine_id = self.config["credentials"]["search_engine_id"]

        # Validate inputs
        if not api_key or not search_engine_id:
            return SearchResponse(
                success=False,
                query=query,
                error_message="Missing API key or search engine ID"
            )

        if not query.strip():
            return SearchResponse(
                success=False,
                query=query,
                error_message="Empty search query"
            )

        # Create search request
        request = SearchRequest(
            query=query.strip(),
            cx=search_engine_id,
            api_key=api_key,
            num_results=max(1, min(10, num_results)),
            start_index=max(1, start_index)
        )

        # Check cache first
        cached_response = self.cache.get(request)
        if cached_response:
            with self.stats_lock:
                self.stats['cached_requests'] += 1

            self.logger.debug(f"Returning cached result for query: {query}")
            return cached_response

        # Queue the request for processing
        result_queue = Queue()
        self.request_queue.put((request, result_queue))

        try:
            # Wait for response (with timeout)
            response = result_queue.get(timeout=self.config["api"]["timeout"] + 10)

            # Cache successful responses
            if response.success:
                self.cache.put(request, response)

            return response

        except Empty:
            return SearchResponse(
                success=False,
                query=query,
                error_message="Request timeout"
            )

    def get_status(self) -> Dict:
        """Get comprehensive status of the search client"""
        with self.stats_lock:
            stats_copy = self.stats.copy()

        uptime = datetime.now() - stats_copy['start_time']

        return {
            'status': 'active',
            'uptime_seconds': uptime.total_seconds(),
            'statistics': stats_copy,
            'rate_limiter': self.rate_limiter.get_status(),
            'circuit_breaker': self.circuit_breaker.get_status(),
            'cache': self.cache.get_stats(),
            'queue_size': self.request_queue.qsize(),
            'config': {
                'daily_request_limit': self.config["rate_limit"]["max_requests_per_day"],
                'cache_ttl': self.config["cache"]["ttl_seconds"],
                'circuit_breaker_threshold': self.config["circuit_breaker"]["failure_threshold"]
            }
        }

    def reset_circuit_breaker(self):
        """Manually reset the circuit breaker"""
        self.circuit_breaker.state = CircuitBreakerState.CLOSED
        self.circuit_breaker.failure_count = 0
        self.circuit_breaker.last_failure_time = None
        self.logger.info("Circuit breaker manually reset")

    def clear_cache(self):
        """Clear the search cache"""
        self.cache.clear()
        self.logger.info("Search cache cleared")

    def shutdown(self):
        """Shutdown the search client and cleanup resources"""
        self.logger.info("Shutting down Google Search client...")

        # Signal shutdown
        self.shutdown_flag.set()

        # Wait for queue processor to finish
        if self.queue_processor_thread and self.queue_processor_thread.is_alive():
            self.queue_processor_thread.join(timeout=5.0)

        # Clear cache to free memory
        self.cache.clear()

        self.logger.info("Google Search client shutdown complete")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.shutdown()

# Convenience functions for external use
def search_google(query: str, num_results: int = 10, **kwargs) -> SearchResponse:
    """Quick search function using default client"""
    client = GoogleSearchFallback()
    try:
        return client.search(query, num_results, **kwargs)
    finally:
        client.shutdown()

def get_search_client_status() -> Dict:
    """Get status of default search client"""
    try:
        # Create a minimal status without starting the full client
        return {
            'status': 'ready',
            'message': 'Client available for use',
            'module_loaded': True
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'module_loaded': False
        }

if __name__ == "__main__":
    # CLI interface for testing
    import argparse

    parser = argparse.ArgumentParser(description="Google Search Fallback Client")
    parser.add_argument("--search", type=str, help="Search query")
    parser.add_argument("--num", type=int, default=10, help="Number of results")
    parser.add_argument("--status", action="store_true", help="Show client status")
    parser.add_argument("--test", action="store_true", help="Run test queries")
    parser.add_argument("--config", default="data/google_search_config.json", help="Config file path")

    args = parser.parse_args()

    if args.status:
        status = get_search_client_status()
        print(json.dumps(status, indent=2, default=str))

    elif args.test:
        print("Running Google Search Fallback tests...")

        with GoogleSearchFallback(args.config) as client:
            test_queries = ["python programming", "artificial intelligence", "web development"]

            for query in test_queries:
                print(f"\nTesting query: '{query}'")
                response = client.search(query, num_results=3)

                if response.success:
                    print(f"✓ Found {len(response.results)} results")
                    for i, result in enumerate(response.results, 1):
                        print(f"  {i}. {result['title']}")
                else:
                    print(f"✗ Search failed: {response.error_message}")

            print(f"\nFinal status:")
            status = client.get_status()
            print(f"Total requests: {status['statistics']['total_requests']}")
            print(f"Successful: {status['statistics']['successful_requests']}")
            print(f"Failed: {status['statistics']['failed_requests']}")
            print(f"Cached: {status['statistics']['cached_requests']}")

    elif args.search:
        with GoogleSearchFallback(args.config) as client:
            response = client.search(args.search, num_results=args.num)

            if response.success:
                print(f"Search results for '{args.search}':")
                for i, result in enumerate(response.results, 1):
                    print(f"\n{i}. {result['title']}")
                    print(f"   {result['link']}")
                    print(f"   {result['snippet']}")
            else:
                print(f"Search failed: {response.error_message}")
    else:
        print("Use --help for usage information")
        print("Example: python google_search_fallback.py --search 'python tutorial' --num 5")