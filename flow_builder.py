import json

def build_campaign_flow(emails, sms_messages, campaign_type):
    """
    Build campaign flow logic with delays, triggers, and conditions
    """
    flow_steps = []
    step_counter = 1
    
    # Create combined sequence based on campaign type
    if campaign_type == "cart_abandonment":
        flow_steps = build_cart_abandonment_flow(emails, sms_messages, step_counter)
    elif campaign_type == "welcome_series":
        flow_steps = build_welcome_series_flow(emails, sms_messages, step_counter)
    elif campaign_type == "win_back":
        flow_steps = build_win_back_flow(emails, sms_messages, step_counter)
    elif campaign_type == "post_purchase":
        flow_steps = build_post_purchase_flow(emails, sms_messages, step_counter)
    else:
        flow_steps = build_general_flow(emails, sms_messages, step_counter)
    
    # Add triggers and conditions
    flow_logic = {
        "campaign_type": campaign_type,
        "total_steps": len(flow_steps),
        "steps": flow_steps,
        "triggers": get_campaign_triggers(campaign_type),
        "exit_conditions": get_exit_conditions(campaign_type),
        "metadata": {
            "estimated_duration": calculate_campaign_duration(flow_steps),
            "touchpoints": len([step for step in flow_steps if step["type"] in ["email", "sms"]])
        }
    }
    
    return flow_logic

def build_cart_abandonment_flow(emails, sms_messages, step_counter):
    """
    Build cart abandonment specific flow
    """
    flow_steps = []
    
    # Interleave emails and SMS strategically
    email_index = 0
    sms_index = 0
    
    # First email (quick reminder)
    if email_index < len(emails):
        flow_steps.append({
            "step": step_counter,
            "type": "email",
            "delay": emails[email_index].get("delay", "1 hour"),
            "content_id": f"email_{email_index + 1}",
            "subject": emails[email_index].get("subject", ""),
            "purpose": emails[email_index].get("purpose", "Reminder"),
            "conditions": ["cart_not_completed", "user_active"]
        })
        step_counter += 1
        email_index += 1
    
    # First SMS (urgency)
    if sms_index < len(sms_messages):
        flow_steps.append({
            "step": step_counter,
            "type": "sms",
            "delay": sms_messages[sms_index].get("delay", "6 hours"),
            "content_id": f"sms_{sms_index + 1}",
            "message": sms_messages[sms_index].get("message", "")[:50] + "...",
            "purpose": sms_messages[sms_index].get("purpose", "Quick Reminder"),
            "conditions": ["cart_not_completed", "phone_available"]
        })
        step_counter += 1
        sms_index += 1
    
    # Remaining emails
    while email_index < len(emails):
        flow_steps.append({
            "step": step_counter,
            "type": "email",
            "delay": emails[email_index].get("delay", f"{email_index + 1} days"),
            "content_id": f"email_{email_index + 1}",
            "subject": emails[email_index].get("subject", ""),
            "purpose": emails[email_index].get("purpose", "Follow-up"),
            "conditions": ["cart_not_completed", "user_active"]
        })
        step_counter += 1
        email_index += 1
        
        # Add second SMS after 3rd email
        if email_index == 3 and sms_index < len(sms_messages):
            flow_steps.append({
                "step": step_counter,
                "type": "sms",
                "delay": sms_messages[sms_index].get("delay", "1 day"),
                "content_id": f"sms_{sms_index + 1}",
                "message": sms_messages[sms_index].get("message", "")[:50] + "...",
                "purpose": sms_messages[sms_index].get("purpose", "Final Push"),
                "conditions": ["cart_not_completed", "phone_available"]
            })
            step_counter += 1
            sms_index += 1
    
    return flow_steps

def build_welcome_series_flow(emails, sms_messages, step_counter):
    """
    Build welcome series specific flow
    """
    flow_steps = []
    
    # Welcome email immediately
    if len(emails) > 0:
        flow_steps.append({
            "step": step_counter,
            "type": "email",
            "delay": "immediate",
            "content_id": "email_1",
            "subject": emails[0].get("subject", "Welcome!"),
            "purpose": emails[0].get("purpose", "Welcome"),
            "conditions": ["new_subscriber"]
        })
        step_counter += 1
    
    # Welcome SMS after 1 hour
    if len(sms_messages) > 0:
        flow_steps.append({
            "step": step_counter,
            "type": "sms",
            "delay": "1 hour",
            "content_id": "sms_1",
            "message": sms_messages[0].get("message", "")[:50] + "...",
            "purpose": sms_messages[0].get("purpose", "Welcome SMS"),
            "conditions": ["new_subscriber", "phone_available"]
        })
        step_counter += 1
    
    # Remaining emails with progressive delays
    for i in range(1, len(emails)):
        flow_steps.append({
            "step": step_counter,
            "type": "email",
            "delay": emails[i].get("delay", f"{i * 2} days"),
            "content_id": f"email_{i + 1}",
            "subject": emails[i].get("subject", ""),
            "purpose": emails[i].get("purpose", "Education"),
            "conditions": ["subscriber_active"]
        })
        step_counter += 1
    
    # Additional SMS messages
    for i in range(1, len(sms_messages)):
        flow_steps.append({
            "step": step_counter,
            "type": "sms",
            "delay": sms_messages[i].get("delay", f"{(i + 1) * 7} days"),
            "content_id": f"sms_{i + 1}",
            "message": sms_messages[i].get("message", "")[:50] + "...",
            "purpose": sms_messages[i].get("purpose", "Engagement"),
            "conditions": ["subscriber_active", "phone_available"]
        })
        step_counter += 1
    
    return flow_steps

def build_win_back_flow(emails, sms_messages, step_counter):
    """
    Build win-back specific flow
    """
    flow_steps = []
    
    # Immediate win-back email
    if len(emails) > 0:
        flow_steps.append({
            "step": step_counter,
            "type": "email",
            "delay": "immediate",
            "content_id": "email_1",
            "subject": emails[0].get("subject", "We miss you!"),
            "purpose": emails[0].get("purpose", "We Miss You"),
            "conditions": ["inactive_user", "churned_90_days"]
        })
        step_counter += 1
    
    # Follow-up emails with increasing urgency
    for i in range(1, len(emails)):
        flow_steps.append({
            "step": step_counter,
            "type": "email",
            "delay": emails[i].get("delay", f"{i * 3} days"),
            "content_id": f"email_{i + 1}",
            "subject": emails[i].get("subject", ""),
            "purpose": emails[i].get("purpose", "Win-back Offer"),
            "conditions": ["still_inactive", "no_recent_purchase"]
        })
        step_counter += 1
    
    # Strategic SMS placement
    for i, sms in enumerate(sms_messages):
        flow_steps.append({
            "step": step_counter,
            "type": "sms",
            "delay": sms.get("delay", f"{(i + 1) * 5} days"),
            "content_id": f"sms_{i + 1}",
            "message": sms.get("message", "")[:50] + "...",
            "purpose": sms.get("purpose", "Win-back SMS"),
            "conditions": ["still_inactive", "phone_available"]
        })
        step_counter += 1
    
    return flow_steps

def build_post_purchase_flow(emails, sms_messages, step_counter):
    """
    Build post-purchase specific flow
    """
    flow_steps = []
    
    # Immediate thank you
    if len(emails) > 0:
        flow_steps.append({
            "step": step_counter,
            "type": "email",
            "delay": "immediate",
            "content_id": "email_1",
            "subject": emails[0].get("subject", "Thank you for your purchase!"),
            "purpose": emails[0].get("purpose", "Thank You"),
            "conditions": ["recent_purchase"]
        })
        step_counter += 1
    
    # Thank you SMS
    if len(sms_messages) > 0:
        flow_steps.append({
            "step": step_counter,
            "type": "sms",
            "delay": "2 hours",
            "content_id": "sms_1",
            "message": sms_messages[0].get("message", "")[:50] + "...",
            "purpose": sms_messages[0].get("purpose", "Thank You SMS"),
            "conditions": ["recent_purchase", "phone_available"]
        })
        step_counter += 1
    
    # Follow-up emails
    for i in range(1, len(emails)):
        flow_steps.append({
            "step": step_counter,
            "type": "email",
            "delay": emails[i].get("delay", f"{i * 7} days"),
            "content_id": f"email_{i + 1}",
            "subject": emails[i].get("subject", ""),
            "purpose": emails[i].get("purpose", "Follow-up"),
            "conditions": ["customer_active"]
        })
        step_counter += 1
    
    # Additional SMS
    for i in range(1, len(sms_messages)):
        flow_steps.append({
            "step": step_counter,
            "type": "sms",
            "delay": sms_messages[i].get("delay", f"{(i + 2) * 7} days"),
            "content_id": f"sms_{i + 1}",
            "message": sms_messages[i].get("message", "")[:50] + "...",
            "purpose": sms_messages[i].get("purpose", "Follow-up SMS"),
            "conditions": ["customer_active", "phone_available"]
        })
        step_counter += 1
    
    return flow_steps

def build_general_flow(emails, sms_messages, step_counter):
    """
    Build general campaign flow
    """
    flow_steps = []
    
    # Simple sequential flow
    for i, email in enumerate(emails):
        flow_steps.append({
            "step": step_counter,
            "type": "email",
            "delay": email.get("delay", f"{i + 1} days"),
            "content_id": f"email_{i + 1}",
            "subject": email.get("subject", ""),
            "purpose": email.get("purpose", "General"),
            "conditions": ["subscriber_active"]
        })
        step_counter += 1
    
    for i, sms in enumerate(sms_messages):
        flow_steps.append({
            "step": step_counter,
            "type": "sms",
            "delay": sms.get("delay", f"{(i + 1) * 3} days"),
            "content_id": f"sms_{i + 1}",
            "message": sms.get("message", "")[:50] + "...",
            "purpose": sms.get("purpose", "General"),
            "conditions": ["subscriber_active", "phone_available"]
        })
        step_counter += 1
    
    return flow_steps

def get_campaign_triggers(campaign_type):
    """
    Get campaign-specific triggers
    """
    triggers = {
        "cart_abandonment": [
            {"event": "cart_abandoned", "delay": "1 hour"},
            {"event": "cart_still_abandoned", "delay": "6 hours"}
        ],
        "welcome_series": [
            {"event": "user_subscribed", "delay": "immediate"},
            {"event": "email_confirmed", "delay": "1 hour"}
        ],
        "win_back": [
            {"event": "user_inactive_90_days", "delay": "immediate"},
            {"event": "no_purchase_180_days", "delay": "immediate"}
        ],
        "post_purchase": [
            {"event": "purchase_completed", "delay": "immediate"},
            {"event": "order_shipped", "delay": "1 day"}
        ]
    }
    
    return triggers.get(campaign_type, [{"event": "campaign_start", "delay": "immediate"}])

def get_exit_conditions(campaign_type):
    """
    Get campaign exit conditions
    """
    exit_conditions = {
        "cart_abandonment": [
            "purchase_completed",
            "cart_cleared",
            "unsubscribed"
        ],
        "welcome_series": [
            "unsubscribed",
            "marked_as_spam",
            "completed_onboarding"
        ],
        "win_back": [
            "purchase_made",
            "engagement_resumed",
            "unsubscribed"
        ],
        "post_purchase": [
            "unsubscribed",
            "return_requested",
            "loyalty_program_joined"
        ]
    }
    
    return exit_conditions.get(campaign_type, ["unsubscribed", "campaign_completed"])

def calculate_campaign_duration(flow_steps):
    """
    Calculate estimated campaign duration
    """
    if not flow_steps:
        return "0 days"
    
    # Parse delays and calculate total duration
    total_hours = 0
    
    for step in flow_steps:
        delay = step.get("delay", "1 day")
        hours = parse_delay_to_hours(delay)
        total_hours += hours
    
    if total_hours < 24:
        return f"{total_hours} hours"
    elif total_hours < 168:  # 1 week
        return f"{total_hours // 24} days"
    else:
        return f"{total_hours // 168} weeks"

def parse_delay_to_hours(delay_str):
    """
    Parse delay string to hours
    """
    delay_str = delay_str.lower()
    
    if "immediate" in delay_str:
        return 0
    elif "hour" in delay_str:
        return int(delay_str.split()[0]) if delay_str.split()[0].isdigit() else 1
    elif "day" in delay_str:
        return int(delay_str.split()[0]) * 24 if delay_str.split()[0].isdigit() else 24
    elif "week" in delay_str:
        return int(delay_str.split()[0]) * 168 if delay_str.split()[0].isdigit() else 168
    else:
        return 24  # Default to 1 day
