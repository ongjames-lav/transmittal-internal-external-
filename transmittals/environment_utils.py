"""
Utility functions to capture sender environment details.
Extracts device information, IP address, and browser from request object.
"""
from user_agents import parse


def get_client_ip(request):
    """
    Extract client IP address from request object.
    Respects X-Forwarded-For header for proxied requests.
    
    Args:
        request: Django HTTP request object
        
    Returns:
        str: IPv4 or IPv6 address, or None if not available
    """
    # Check for X-Forwarded-For header (for proxied requests)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For can contain multiple IPs, get the first one
        ip = x_forwarded_for.split(',')[0].strip()
        return ip
    
    # Fall back to REMOTE_ADDR
    ip = request.META.get('REMOTE_ADDR')
    return ip if ip else None


def get_device_information(request):
    """
    Extract device information (type and OS) from User-Agent header.
    
    Args:
        request: Django HTTP request object
        
    Returns:
        str: Device information (e.g., "Desktop Windows 10", "Mobile iOS")
    """
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    if not user_agent_string:
        return None
    
    try:
        user_agent = parse(user_agent_string)
        
        # Determine device type
        if user_agent.is_mobile:
            device_type = 'Mobile'
        elif user_agent.is_tablet:
            device_type = 'Tablet'
        elif user_agent.is_pc:
            device_type = 'Desktop'
        else:
            device_type = 'Unknown'
        
        # Get OS
        os_name = user_agent.os.family or 'Unknown OS'
        os_version = user_agent.os.version_string or ''
        
        if os_version:
            os_info = f"{os_name} {os_version}"
        else:
            os_info = os_name
        
        return f"{device_type} {os_info}".strip()
    except Exception:
        return None


def get_browser_information(request):
    """
    Extract browser name and version from User-Agent header.
    
    Args:
        request: Django HTTP request object
        
    Returns:
        str: Browser information (e.g., "Chrome 118.0", "Firefox 121.0")
    """
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    if not user_agent_string:
        return None
    
    try:
        user_agent = parse(user_agent_string)
        
        # Get browser name
        browser_name = user_agent.browser.family or 'Unknown Browser'
        browser_version = user_agent.browser.version_string or ''
        
        if browser_version:
            return f"{browser_name} {browser_version}".strip()
        else:
            return browser_name
    except Exception:
        return None


def capture_sender_environment(request):
    """
    Capture all sender environment details in one call.
    
    Args:
        request: Django HTTP request object
        
    Returns:
        dict: Dictionary with keys:
            - device_information: str
            - ip_address: str
            - browser_of_sender: str
    """
    return {
        'device_information': get_device_information(request),
        'ip_address': get_client_ip(request),
        'browser_of_sender': get_browser_information(request),
    }
