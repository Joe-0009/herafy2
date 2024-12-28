from datetime import datetime

def timeago(date):
    now = datetime.utcnow()
    diff = now - date
    
    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = diff.days
    
    if days > 365:
        years = days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    elif days > 30:
        months = days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif days > 0:
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif hours > 0:
        return f"{int(hours)} hour{'s' if int(hours) != 1 else ''} ago"
    elif minutes > 0:
        return f"{int(minutes)} minute{'s' if int(minutes) != 1 else ''} ago"
    else:
        return "Just now"