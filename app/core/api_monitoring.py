"""
API monitoring and logging utilities for security and analytics.
"""

import json
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.models.database import APIKey
from app.core.cache import redis_client

logger = logging.getLogger(__name__)


class APIMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring API usage and security events."""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """Monitor and log API requests."""
        start_time = time.time()

        # Collect request data
        request_data = await self._collect_request_data(request)

        try:
            # Process request
            response = await call_next(request)

            # Collect response data
            response_data = self._collect_response_data(response, start_time)

            # Log the API usage
            await self._log_api_usage(request_data, response_data, request)

            return response

        except Exception as e:
            # Log errors
            await self._log_api_error(request_data, str(e), request)
            raise

    async def _collect_request_data(self, request: Request) -> Dict[str, Any]:
        """Collect request data for logging."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("User-Agent"),
            "content_type": request.headers.get("Content-Type"),
            "content_length": request.headers.get("Content-Length"),
        }

    def _collect_response_data(self, response: Response, start_time: float) -> Dict[str, Any]:
        """Collect response data for logging."""
        processing_time = time.time() - start_time

        return {
            "status_code": response.status_code,
            "processing_time": processing_time,
            "response_headers": dict(response.headers),
        }

    async def _log_api_usage(self, request_data: Dict, response_data: Dict, request: Request):
        """Log API usage to structured logs and metrics."""

        # Get API key info if available
        api_key = getattr(request.state, 'api_key', None)
        auth_type = getattr(request.state, 'auth_type', 'jwt')
        rate_limit_status = getattr(request.state, 'rate_limit_status', {})

        # Create comprehensive log entry
        log_entry = {
            **request_data,
            **response_data,
            "auth_type": auth_type,
            "api_key_info": {
                "key_prefix": api_key.key_prefix if api_key else None,
                "key_id": str(api_key.id) if api_key else None,
                "scopes": api_key.scopes if api_key else None,
                "tier": api_key.rate_limit_tier.value if api_key else None,
            } if api_key else None,
            "rate_limit_status": rate_limit_status if rate_limit_status else None,
        }

        # Log based on status code and processing time
        if response_data["status_code"] >= 400:
            logger.warning(f"API Error - {request_data['method']} {request_data['path']} - {response_data['status_code']}", extra=log_entry)
        elif response_data["processing_time"] > 5.0:  # Slow request
            logger.warning(f"Slow API Request - {request_data['method']} {request_data['path']} - {response_data['processing_time']:.2f}s", extra=log_entry)
        else:
            logger.info(f"API Request - {request_data['method']} {request_data['path']} - {response_data['status_code']}", extra=log_entry)

        # Store metrics in Redis for analytics
        await self._store_metrics(log_entry, api_key)

    async def _log_api_error(self, request_data: Dict, error: str, request: Request):
        """Log API errors."""
        api_key = getattr(request.state, 'api_key', None)

        log_entry = {
            **request_data,
            "error": error,
            "api_key_prefix": api_key.key_prefix if api_key else None,
        }

        logger.error(f"API Exception - {request_data['method']} {request_data['path']}: {error}", extra=log_entry)

    async def _store_metrics(self, log_entry: Dict, api_key: Optional[APIKey]):
        """Store metrics in Redis for analytics and monitoring."""
        try:
            if not redis_client:
                return

            current_time = int(time.time())
            hour_bucket = current_time // 3600
            day_bucket = current_time // 86400

            # Global API metrics
            pipe = redis_client.pipeline()

            # Total requests
            pipe.incr(f"api_metrics:total_requests:{hour_bucket}")
            pipe.expire(f"api_metrics:total_requests:{hour_bucket}", 86400)  # Keep for 24 hours

            # Status code metrics
            status_code = log_entry["status_code"]
            pipe.incr(f"api_metrics:status:{status_code}:{hour_bucket}")
            pipe.expire(f"api_metrics:status:{status_code}:{hour_bucket}", 86400)

            # Endpoint metrics
            path = log_entry["path"]
            method = log_entry["method"]
            pipe.incr(f"api_metrics:endpoint:{method}:{path}:{hour_bucket}")
            pipe.expire(f"api_metrics:endpoint:{method}:{path}:{hour_bucket}", 86400)

            # Processing time (average calculation would require additional logic)
            processing_time = log_entry["processing_time"]
            pipe.lpush(f"api_metrics:processing_times:{hour_bucket}", processing_time)
            pipe.expire(f"api_metrics:processing_times:{hour_bucket}", 3600)
            pipe.ltrim(f"api_metrics:processing_times:{hour_bucket}", 0, 999)  # Keep last 1000 entries

            # API key specific metrics
            if api_key:
                key_id = str(api_key.id)
                pipe.incr(f"api_metrics:apikey:{key_id}:requests:{hour_bucket}")
                pipe.expire(f"api_metrics:apikey:{key_id}:requests:{hour_bucket}", 86400)

                pipe.incr(f"api_metrics:apikey:{key_id}:requests_daily:{day_bucket}")
                pipe.expire(f"api_metrics:apikey:{key_id}:requests_daily:{day_bucket}", 86400 * 7)  # Keep for 7 days

            await pipe.execute()

        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")


class SecurityMonitor:
    """Security monitoring utilities."""

    @staticmethod
    async def log_security_event(
        event_type: str,
        details: Dict[str, Any],
        severity: str = "warning",
        request: Optional[Request] = None
    ):
        """Log security events for monitoring and alerting."""

        security_log = {
            "event_type": event_type,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details,
        }

        if request:
            security_log.update({
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("User-Agent"),
                "method": request.method,
                "path": request.url.path,
            })

        # Log with appropriate level
        if severity == "critical":
            logger.critical(f"Security Event: {event_type}", extra=security_log)
        elif severity == "error":
            logger.error(f"Security Event: {event_type}", extra=security_log)
        elif severity == "warning":
            logger.warning(f"Security Event: {event_type}", extra=security_log)
        else:
            logger.info(f"Security Event: {event_type}", extra=security_log)

        # Store in Redis for alerting
        try:
            if redis_client:
                key = f"security_events:{event_type}"
                await redis_client.lpush(key, json.dumps(security_log))
                await redis_client.expire(key, 86400 * 7)  # Keep for 7 days
                await redis_client.ltrim(key, 0, 999)  # Keep last 1000 events
        except Exception as e:
            logger.error(f"Failed to store security event: {e}")

    @staticmethod
    async def detect_suspicious_activity(request: Request, api_key: Optional[APIKey] = None):
        """Detect and log suspicious activity patterns."""

        try:
            if not redis_client:
                return

            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("User-Agent", "")

            # Check for suspicious patterns
            suspicious_indicators = []

            # 1. Missing or suspicious user agent
            if not user_agent or len(user_agent) < 10:
                suspicious_indicators.append("missing_or_short_user_agent")

            # 2. High request rate from single IP
            current_minute = int(time.time()) // 60
            ip_requests_key = f"ip_requests:{client_ip}:{current_minute}"
            ip_request_count = await redis_client.incr(ip_requests_key)
            await redis_client.expire(ip_requests_key, 60)

            if ip_request_count > 100:  # More than 100 requests per minute
                suspicious_indicators.append("high_request_rate")

            # 3. Unusual request patterns
            if request.method in ["PUT", "DELETE", "PATCH"] and not api_key:
                suspicious_indicators.append("write_operation_without_apikey")

            # 4. Suspicious paths
            suspicious_paths = ["/admin", "/.env", "/config", "/wp-admin", "/phpinfo"]
            if any(path in request.url.path.lower() for path in suspicious_paths):
                suspicious_indicators.append("suspicious_path_access")

            # Log if suspicious activity detected
            if suspicious_indicators:
                await SecurityMonitor.log_security_event(
                    event_type="suspicious_activity",
                    details={
                        "indicators": suspicious_indicators,
                        "ip_request_count": ip_request_count,
                        "api_key_prefix": api_key.key_prefix if api_key else None,
                    },
                    severity="warning",
                    request=request
                )

        except Exception as e:
            logger.error(f"Error in suspicious activity detection: {e}")


class MetricsCollector:
    """Collect and provide API metrics."""

    @staticmethod
    async def get_api_metrics(hours: int = 24) -> Dict[str, Any]:
        """Get API metrics for the specified time period."""
        try:
            if not redis_client:
                return {"error": "Redis not available"}

            current_time = int(time.time())
            metrics = {
                "total_requests": 0,
                "status_codes": {},
                "top_endpoints": {},
                "processing_times": [],
                "hourly_requests": [],
            }

            # Collect hourly data
            for i in range(hours):
                hour_bucket = (current_time // 3600) - i

                # Total requests
                total = await redis_client.get(f"api_metrics:total_requests:{hour_bucket}")
                if total:
                    metrics["total_requests"] += int(total)
                    metrics["hourly_requests"].append({
                        "hour": hour_bucket * 3600,
                        "requests": int(total)
                    })

            return metrics

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {"error": str(e)}

    @staticmethod
    async def get_api_key_metrics(api_key_id: str, days: int = 7) -> Dict[str, Any]:
        """Get metrics for a specific API key."""
        try:
            if not redis_client:
                return {"error": "Redis not available"}

            current_time = int(time.time())
            metrics = {
                "total_requests": 0,
                "daily_requests": [],
            }

            # Collect daily data
            for i in range(days):
                day_bucket = (current_time // 86400) - i

                # Daily requests
                daily = await redis_client.get(f"api_metrics:apikey:{api_key_id}:requests_daily:{day_bucket}")
                if daily:
                    metrics["total_requests"] += int(daily)
                    metrics["daily_requests"].append({
                        "date": day_bucket * 86400,
                        "requests": int(daily)
                    })

            return metrics

        except Exception as e:
            logger.error(f"Error collecting API key metrics: {e}")
            return {"error": str(e)}


# Global instances
security_monitor = SecurityMonitor()
metrics_collector = MetricsCollector()