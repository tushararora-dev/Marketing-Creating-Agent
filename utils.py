import re
import json
from datetime import datetime

def validate_prompt(prompt):
    """
    Validate user prompt for campaign generation
    """
    if not prompt or not prompt.strip():
        return {"valid": False, "message": "Prompt cannot be empty"}
    
    if len(prompt.strip()) < 10:
        return {"valid": False, "message": "Prompt too short. Please provide more details."}
    
    if len(prompt) > 1000:
        return {"valid": False, "message": "Prompt too long. Please keep it under 1000 characters."}
    
    # Check for basic campaign indicators
    campaign_keywords = [
        "email", "sms", "campaign", "sequence", "series", 
        "cart", "welcome", "abandon", "win-back", "post-purchase"
    ]
    
    if not any(keyword in prompt.lower() for keyword in campaign_keywords):
        return {
            "valid": False, 
            "message": "Prompt should mention campaign type or include keywords like 'email', 'SMS', 'campaign', etc."
        }
    
    return {"valid": True, "message": "Prompt is valid"}

def get_campaign_preview(campaign_data):
    """
    Generate a preview summary of the campaign
    """
    if not campaign_data:
        return "No campaign data available"
    
    emails = campaign_data.get("emails", [])
    sms_messages = campaign_data.get("sms_messages", [])
    campaign_type = campaign_data.get("campaign_type", "general")
    
    preview = {
        "summary": {
            "type": campaign_type.replace("_", " ").title(),
            "total_emails": len(emails),
            "total_sms": len(sms_messages),
            "total_touchpoints": len(emails) + len(sms_messages)
        },
        "first_email": emails[0] if emails else None,
        "first_sms": sms_messages[0] if sms_messages else None,
        "estimated_duration": estimate_campaign_duration(campaign_data.get("flow_logic", {}))
    }
    
    return preview

def estimate_campaign_duration(flow_logic):
    """
    Estimate total campaign duration
    """
    if not flow_logic or not flow_logic.get("steps"):
        return "Unknown"
    
    return flow_logic.get("metadata", {}).get("estimated_duration", "Unknown")

def sanitize_text(text):
    """
    Sanitize text content for safe display
    """
    if not text:
        return ""
    
    # Remove any potentially harmful characters
    sanitized = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)\[\]\'\"@#$%&*+=<>/\\|`~]', '', str(text))
    
    # Limit length
    if len(sanitized) > 2000:
        sanitized = sanitized[:2000] + "..."
    
    return sanitized

def format_delay(delay_string):
    """
    Format delay string for consistent display
    """
    if not delay_string:
        return "Not specified"
    
    delay_string = delay_string.lower().strip()
    
    # Standardize common formats
    replacements = {
        "immediate": "Immediate",
        "1 hour": "1 hour",
        "6 hours": "6 hours",
        "1 day": "1 day",
        "2 days": "2 days",
        "3 days": "3 days",
        "1 week": "1 week",
        "2 weeks": "2 weeks"
    }
    
    return replacements.get(delay_string, delay_string.title())

def extract_numbers_from_text(text):
    """
    Extract numeric values from text
    """
    if not text:
        return []
    
    numbers = re.findall(r'\d+', text)
    return [int(num) for num in numbers]

def detect_campaign_type(text):
    """
    Detect campaign type from text using keywords
    """
    if not text:
        return "general"
    
    text_lower = text.lower()
    
    # Campaign type detection patterns
    patterns = {
        "cart_abandonment": ["cart abandon", "abandon", "left cart", "forgotten cart"],
        "welcome_series": ["welcome", "onboard", "new subscriber", "introduction"],
        "win_back": ["win-back", "winback", "inactive", "re-engage", "return"],
        "post_purchase": ["post-purchase", "post purchase", "after purchase", "thank you", "order confirmation"]
    }
    
    for campaign_type, keywords in patterns.items():
        if any(keyword in text_lower for keyword in keywords):
            return campaign_type
    
    return "general"

def validate_email_content(email_data):
    """
    Validate email content structure and quality
    """
    errors = []
    warnings = []
    
    # Required fields
    required_fields = ["subject", "body", "cta"]
    for field in required_fields:
        if not email_data.get(field):
            errors.append(f"Missing {field}")
    
    # Subject line validation
    subject = email_data.get("subject", "")
    if subject:
        if len(subject) > 50:
            warnings.append("Subject line is longer than 50 characters")
        if len(subject) < 10:
            warnings.append("Subject line might be too short")
        if subject.isupper():
            warnings.append("Subject line is all caps (might trigger spam filters)")
    
    # Body validation
    body = email_data.get("body", "")
    if body:
        if len(body) < 50:
            warnings.append("Email body might be too short")
        if len(body) > 1000:
            warnings.append("Email body is quite long")
    
    # CTA validation
    cta = email_data.get("cta", "")
    if cta:
        if len(cta) > 30:
            warnings.append("CTA text is longer than recommended (30 chars)")
        if not any(word in cta.lower() for word in ["click", "shop", "buy", "learn", "get", "start", "join"]):
            warnings.append("CTA might not be action-oriented enough")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def validate_sms_content(sms_data):
    """
    Validate SMS content structure and quality
    """
    errors = []
    warnings = []
    
    # Required fields
    if not sms_data.get("message"):
        errors.append("Missing SMS message")
    
    # Message validation
    message = sms_data.get("message", "")
    if message:
        if len(message) > 160:
            errors.append("SMS message exceeds 160 characters")
        if len(message) < 20:
            warnings.append("SMS message might be too short")
        
        # Check for common SMS issues
        if not any(word in message.lower() for word in ["click", "tap", "visit", "call", "text", "reply"]):
            warnings.append("SMS might benefit from a clearer call-to-action")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def calculate_campaign_metrics(campaign_data):
    """
    Calculate basic metrics for campaign preview
    """
    emails = campaign_data.get("emails", [])
    sms_messages = campaign_data.get("sms_messages", [])
    
    # Word counts
    total_email_words = sum(len(email.get("body", "").split()) for email in emails)
    average_email_length = total_email_words / len(emails) if emails else 0
    
    # Character counts for SMS
    total_sms_chars = sum(len(sms.get("message", "")) for sms in sms_messages)
    average_sms_length = total_sms_chars / len(sms_messages) if sms_messages else 0
    
    # Estimated costs (rough estimates)
    estimated_sms_segments = sum(calculate_sms_segments(sms.get("message", "")) for sms in sms_messages)
    
    return {
        "content_metrics": {
            "total_email_words": total_email_words,
            "average_email_length": round(average_email_length, 1),
            "total_sms_characters": total_sms_chars,
            "average_sms_length": round(average_sms_length, 1)
        },
        "cost_estimates": {
            "sms_segments": estimated_sms_segments,
            "estimated_sms_cost": round(estimated_sms_segments * 0.01, 2)  # $0.01 per segment
        },
        "engagement_potential": {
            "email_cta_count": sum(1 for email in emails if email.get("cta")),
            "sms_urgency_indicators": count_urgency_words(sms_messages)
        }
    }

def calculate_sms_segments(message):
    """
    Calculate SMS segments (helper function)
    """
    if not message:
        return 0
    
    char_count = len(message)
    
    if char_count <= 160:
        return 1
    else:
        return (char_count - 1) // 153 + 1

def count_urgency_words(sms_messages):
    """
    Count urgency indicators in SMS messages
    """
    urgency_words = ["now", "today", "urgent", "limited", "hurry", "last chance", "expires", "ending"]
    
    count = 0
    for sms in sms_messages:
        message = sms.get("message", "").lower()
        count += sum(1 for word in urgency_words if word in message)
    
    return count

def format_timestamp():
    """
    Get formatted timestamp for exports
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

def clean_json_response(response_text):
    """
    Clean and extract JSON from API responses
    """
    if not response_text:
        return None
    
    # Try to find JSON object
    start_idx = response_text.find('{')
    end_idx = response_text.rfind('}') + 1
    
    if start_idx == -1 or end_idx == 0:
        return None
    
    json_str = response_text[start_idx:end_idx]
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None
