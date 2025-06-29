"""
Customer.IO comprehensive video tracking semantic events.

This module provides functions for tracking all video-related semantic events
as defined in the Customer.IO Data Pipelines API specification, including
playback lifecycle, content tracking, and advertisement events.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from .api_client import CustomerIOClient
from .validators import validate_user_id
from .exceptions import ValidationError


def track_video_playback_started(
    client: CustomerIOClient,
    user_id: str,
    video_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Video Playback Started" semantic event.
    
    This event indicates that video playback has been initiated, providing
    analytics on video engagement and viewer behavior patterns.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    video_id : str
        Unique identifier for the video
    properties : dict, optional
        Additional video properties (title, duration, quality, etc.)
    timestamp : datetime, optional
        When the playback started
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id, video_id, or parameters are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = track_video_playback_started(
    ...     client, 
    ...     user_id="user123",
    ...     video_id="video_456",
    ...     properties={"title": "Introduction", "duration": 300}
    ... )
    >>> print(result["status"])
    success
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not video_id or not isinstance(video_id, str):
        raise ValidationError("Video ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build event properties
    event_properties = {"video_id": video_id}
    if properties:
        event_properties.update(properties)
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Video Playback Started",
        "properties": event_properties
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_video_playback_paused(
    client: CustomerIOClient,
    user_id: str,
    video_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Video Playback Paused" semantic event.
    
    This event indicates that video playback has been paused by the user,
    providing insights into engagement patterns and drop-off points.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    video_id : str
        Unique identifier for the video
    properties : dict, optional
        Additional properties (position, duration, percentage_watched, etc.)
    timestamp : datetime, optional
        When the playback was paused
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not video_id or not isinstance(video_id, str):
        raise ValidationError("Video ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build event properties
    event_properties = {"video_id": video_id}
    if properties:
        event_properties.update(properties)
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Video Playback Paused",
        "properties": event_properties
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_video_playback_interrupted(
    client: CustomerIOClient,
    user_id: str,
    video_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Video Playback Interrupted" semantic event.
    
    This event indicates that video playback was interrupted due to technical
    issues, providing insights into quality of service and user experience.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    video_id : str
        Unique identifier for the video
    properties : dict, optional
        Additional properties (interruption_reason, error_code, position, etc.)
    timestamp : datetime, optional
        When the interruption occurred
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not video_id or not isinstance(video_id, str):
        raise ValidationError("Video ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build event properties
    event_properties = {"video_id": video_id}
    if properties:
        event_properties.update(properties)
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Video Playback Interrupted",
        "properties": event_properties
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_video_playback_buffer_started(
    client: CustomerIOClient,
    user_id: str,
    video_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Video Playback Buffer Started" semantic event.
    
    This event indicates that video buffering has started, providing insights
    into streaming quality and network performance.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    video_id : str
        Unique identifier for the video
    properties : dict, optional
        Additional properties (position, bitrate, buffer_reason, etc.)
    timestamp : datetime, optional
        When buffering started
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not video_id or not isinstance(video_id, str):
        raise ValidationError("Video ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build event properties
    event_properties = {"video_id": video_id}
    if properties:
        event_properties.update(properties)
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Video Playback Buffer Started",
        "properties": event_properties
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_video_playback_buffer_completed(
    client: CustomerIOClient,
    user_id: str,
    video_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Video Playback Buffer Completed" semantic event.
    
    This event indicates that video buffering has completed and playback
    can resume, providing insights into buffer recovery and quality adaptation.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    video_id : str
        Unique identifier for the video
    properties : dict, optional
        Additional properties (buffer_duration, new_bitrate, position, etc.)
    timestamp : datetime, optional
        When buffering completed
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not video_id or not isinstance(video_id, str):
        raise ValidationError("Video ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build event properties
    event_properties = {"video_id": video_id}
    if properties:
        event_properties.update(properties)
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Video Playback Buffer Completed",
        "properties": event_properties
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_video_playback_seek_started(
    client: CustomerIOClient,
    user_id: str,
    video_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Video Playback Seek Started" semantic event.
    
    This event indicates that the user has initiated a seek operation,
    providing insights into content navigation patterns.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    video_id : str
        Unique identifier for the video
    properties : dict, optional
        Additional properties (position, seek_position, seek_type, etc.)
    timestamp : datetime, optional
        When the seek operation started
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not video_id or not isinstance(video_id, str):
        raise ValidationError("Video ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build event properties
    event_properties = {"video_id": video_id}
    if properties:
        event_properties.update(properties)
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Video Playback Seek Started",
        "properties": event_properties
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_video_playback_seek_completed(
    client: CustomerIOClient,
    user_id: str,
    video_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Video Playback Seek Completed" semantic event.
    
    This event indicates that a seek operation has completed successfully,
    providing insights into user navigation efficiency and preferences.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    video_id : str
        Unique identifier for the video
    properties : dict, optional
        Additional properties (previous_position, new_position, seek_duration, etc.)
    timestamp : datetime, optional
        When the seek operation completed
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not video_id or not isinstance(video_id, str):
        raise ValidationError("Video ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build event properties
    event_properties = {"video_id": video_id}
    if properties:
        event_properties.update(properties)
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Video Playback Seek Completed",
        "properties": event_properties
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_video_playback_resumed(
    client: CustomerIOClient,
    user_id: str,
    video_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Video Playback Resumed" semantic event.
    
    This event indicates that video playback has been resumed after being
    paused, providing insights into engagement recovery and viewing patterns.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    video_id : str
        Unique identifier for the video
    properties : dict, optional
        Additional properties (position, pause_duration, resume_trigger, etc.)
    timestamp : datetime, optional
        When playback was resumed
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not video_id or not isinstance(video_id, str):
        raise ValidationError("Video ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build event properties
    event_properties = {"video_id": video_id}
    if properties:
        event_properties.update(properties)
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Video Playback Resumed",
        "properties": event_properties
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_video_playback_completed(
    client: CustomerIOClient,
    user_id: str,
    video_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Video Playback Completed" semantic event.
    
    This event indicates that video playback has completed successfully,
    providing insights into completion rates and content effectiveness.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    video_id : str
        Unique identifier for the video
    properties : dict, optional
        Additional properties (duration, completion_rate, total_watch_time, etc.)
    timestamp : datetime, optional
        When playback completed
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not video_id or not isinstance(video_id, str):
        raise ValidationError("Video ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build event properties
    event_properties = {"video_id": video_id}
    if properties:
        event_properties.update(properties)
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Video Playback Completed",
        "properties": event_properties
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_video_playback_exited(
    client: CustomerIOClient,
    user_id: str,
    video_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Video Playback Exited" semantic event.
    
    This event indicates that the user has exited video playback before
    completion, providing insights into drop-off patterns and exit reasons.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    video_id : str
        Unique identifier for the video
    properties : dict, optional
        Additional properties (position, completion_rate, exit_reason, etc.)
    timestamp : datetime, optional
        When the user exited playback
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not video_id or not isinstance(video_id, str):
        raise ValidationError("Video ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build event properties
    event_properties = {"video_id": video_id}
    if properties:
        event_properties.update(properties)
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Video Playback Exited",
        "properties": event_properties
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_video_content_started(
    client: CustomerIOClient,
    user_id: str,
    content_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Video Content Started" semantic event.
    
    This event indicates that video content viewing has started, providing
    insights into content engagement and viewing preferences.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    content_id : str
        Unique identifier for the content
    properties : dict, optional
        Additional properties (title, category, duration, series, etc.)
    timestamp : datetime, optional
        When content viewing started
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not content_id or not isinstance(content_id, str):
        raise ValidationError("Content ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build event properties
    event_properties = {"content_id": content_id}
    if properties:
        event_properties.update(properties)
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Video Content Started",
        "properties": event_properties
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_video_content_playing(
    client: CustomerIOClient,
    user_id: str,
    content_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Video Content Playing" semantic event.
    
    This event indicates ongoing video content consumption, providing insights
    into viewing progress and engagement levels during playback.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    content_id : str
        Unique identifier for the content
    properties : dict, optional
        Additional properties (position, duration, playback_speed, quality, etc.)
    timestamp : datetime, optional
        When this playing event occurred
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not content_id or not isinstance(content_id, str):
        raise ValidationError("Content ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build event properties
    event_properties = {"content_id": content_id}
    if properties:
        event_properties.update(properties)
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Video Content Playing",
        "properties": event_properties
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_video_content_completed(
    client: CustomerIOClient,
    user_id: str,
    content_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Video Content Completed" semantic event.
    
    This event indicates that video content has been fully consumed,
    providing insights into content completion rates and viewer satisfaction.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    content_id : str
        Unique identifier for the content
    properties : dict, optional
        Additional properties (duration, completion_rate, total_watch_time, engagement_score, etc.)
    timestamp : datetime, optional
        When content viewing completed
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not content_id or not isinstance(content_id, str):
        raise ValidationError("Content ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build event properties
    event_properties = {"content_id": content_id}
    if properties:
        event_properties.update(properties)
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Video Content Completed",
        "properties": event_properties
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_video_ad_started(
    client: CustomerIOClient,
    user_id: str,
    ad_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Video Ad Started" semantic event.
    
    This event indicates that a video advertisement has started playing,
    providing insights into ad engagement and revenue optimization.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    ad_id : str
        Unique identifier for the advertisement
    properties : dict, optional
        Additional properties (ad_type, advertiser, duration, content_id, etc.)
    timestamp : datetime, optional
        When the ad started playing
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not ad_id or not isinstance(ad_id, str):
        raise ValidationError("Ad ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build event properties
    event_properties = {"ad_id": ad_id}
    if properties:
        event_properties.update(properties)
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Video Ad Started",
        "properties": event_properties
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_video_ad_playing(
    client: CustomerIOClient,
    user_id: str,
    ad_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Video Ad Playing" semantic event.
    
    This event indicates ongoing video advertisement playback, providing
    insights into ad engagement levels and viewer attention during ads.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    ad_id : str
        Unique identifier for the advertisement
    properties : dict, optional
        Additional properties (position, duration, quartile, engagement_events, etc.)
    timestamp : datetime, optional
        When this ad playing event occurred
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not ad_id or not isinstance(ad_id, str):
        raise ValidationError("Ad ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build event properties
    event_properties = {"ad_id": ad_id}
    if properties:
        event_properties.update(properties)
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Video Ad Playing",
        "properties": event_properties
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_video_ad_completed(
    client: CustomerIOClient,
    user_id: str,
    ad_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Video Ad Completed" semantic event.
    
    This event indicates that a video advertisement has finished playing,
    providing insights into ad completion rates and effectiveness.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    ad_id : str
        Unique identifier for the advertisement
    properties : dict, optional
        Additional properties (duration, completion_rate, clicked, skipped, etc.)
    timestamp : datetime, optional
        When the ad completed
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not ad_id or not isinstance(ad_id, str):
        raise ValidationError("Ad ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build event properties
    event_properties = {"ad_id": ad_id}
    if properties:
        event_properties.update(properties)
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Video Ad Completed",
        "properties": event_properties
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)