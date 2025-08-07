import json
import csv
import io
from datetime import datetime

def export_campaign_json(campaign_data):
    """
    Export campaign data as JSON format for Klaviyo/automation platforms
    """
    # Create Klaviyo-compatible structure
    klaviyo_export = {
        "campaign_name": f"{campaign_data.get('campaign_type', 'campaign')}_{datetime.now().strftime('%Y%m%d')}",
        "campaign_type": campaign_data.get("campaign_type", "general"),
        "brand_context": {
            "tone": campaign_data.get("brand_tone", "Friendly"),
            "audience": campaign_data.get("target_audience", "General"),
            "description": campaign_data.get("brand_context", "")
        },
        "flow_configuration": {
            "trigger_event": get_trigger_event(campaign_data.get("campaign_type", "general")),
            "exit_conditions": campaign_data.get("flow_logic", {}).get("exit_conditions", []),
            "total_steps": len(campaign_data.get("emails", [])) + len(campaign_data.get("sms_messages", []))
        },
        "messages": format_messages_for_export(campaign_data),
        "automation_flow": format_flow_for_export(campaign_data.get("flow_logic", {})),
        "assets": format_assets_for_export(campaign_data.get("visuals", [])),
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_emails": len(campaign_data.get("emails", [])),
            "total_sms": len(campaign_data.get("sms_messages", [])),
            "estimated_duration": campaign_data.get("flow_logic", {}).get("metadata", {}).get("estimated_duration", "Unknown")
        }
    }
    
    return json.dumps(klaviyo_export, indent=2, ensure_ascii=False)

def export_campaign_csv(campaign_data):
    """
    Export campaign data as CSV format for easy import
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write campaign summary
    writer.writerow(["Campaign Summary"])
    writer.writerow(["Type", campaign_data.get("campaign_type", "general")])
    writer.writerow(["Brand Tone", campaign_data.get("brand_tone", "Friendly")])
    writer.writerow(["Target Audience", campaign_data.get("target_audience", "General")])
    writer.writerow([])  # Empty row
    
    # Write emails section
    writer.writerow(["Email Messages"])
    writer.writerow(["Step", "Subject", "Body", "CTA", "Purpose", "Delay"])
    
    emails = campaign_data.get("emails", [])
    for i, email in enumerate(emails):
        writer.writerow([
            i + 1,
            email.get("subject", ""),
            email.get("body", "")[:100] + "..." if len(email.get("body", "")) > 100 else email.get("body", ""),
            email.get("cta", ""),
            email.get("purpose", ""),
            email.get("delay", "")
        ])
    
    writer.writerow([])  # Empty row
    
    # Write SMS section
    writer.writerow(["SMS Messages"])
    writer.writerow(["Step", "Message", "Purpose", "Delay"])
    
    sms_messages = campaign_data.get("sms_messages", [])
    for i, sms in enumerate(sms_messages):
        writer.writerow([
            i + 1,
            sms.get("message", ""),
            sms.get("purpose", ""),
            sms.get("delay", "")
        ])
    
    writer.writerow([])  # Empty row
    
    # Write flow logic section
    writer.writerow(["Flow Logic"])
    writer.writerow(["Step", "Type", "Content ID", "Delay", "Conditions"])
    
    flow_steps = campaign_data.get("flow_logic", {}).get("steps", [])
    for step in flow_steps:
        conditions = ", ".join(step.get("conditions", []))
        writer.writerow([
            step.get("step", ""),
            step.get("type", ""),
            step.get("content_id", ""),
            step.get("delay", ""),
            conditions
        ])
    
    writer.writerow([])  # Empty row
    
    # Write visuals section
    writer.writerow(["Visual Assets"])
    writer.writerow(["Purpose", "Description", "Type", "Prompt"])
    
    visuals = campaign_data.get("visuals", [])
    for visual in visuals:
        writer.writerow([
            visual.get("purpose", ""),
            visual.get("description", ""),
            visual.get("type", ""),
            visual.get("prompt", "")[:100] + "..." if len(visual.get("prompt", "")) > 100 else visual.get("prompt", "")
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    return csv_content

def format_messages_for_export(campaign_data):
    """
    Format messages for automation platform export
    """
    messages = []
    
    # Format emails
    emails = campaign_data.get("emails", [])
    for i, email in enumerate(emails):
        messages.append({
            "id": f"email_{i + 1}",
            "type": "email",
            "step": i + 1,
            "subject": email.get("subject", ""),
            "content": email.get("body", ""),
            "cta": email.get("cta", ""),
            "delay": email.get("delay", "1 day"),
            "purpose": email.get("purpose", "General"),
            "metadata": {
                "character_count": len(email.get("body", "")),
                "has_cta": bool(email.get("cta", "")),
                "estimated_read_time": calculate_read_time(email.get("body", ""))
            }
        })
    
    # Format SMS messages
    sms_messages = campaign_data.get("sms_messages", [])
    for i, sms in enumerate(sms_messages):
        messages.append({
            "id": f"sms_{i + 1}",
            "type": "sms",
            "step": len(emails) + i + 1,
            "content": sms.get("message", ""),
            "delay": sms.get("delay", "1 day"),
            "purpose": sms.get("purpose", "General"),
            "metadata": {
                "character_count": len(sms.get("message", "")),
                "sms_segments": calculate_sms_segments(sms.get("message", "")),
                "estimated_cost": calculate_sms_segments(sms.get("message", "")) * 0.01  # Rough estimate
            }
        })
    
    return messages

def format_flow_for_export(flow_logic):
    """
    Format flow logic for automation platform
    """
    if not flow_logic:
        return {}
    
    return {
        "type": "sequential",
        "steps": flow_logic.get("steps", []),
        "triggers": flow_logic.get("triggers", []),
        "exit_conditions": flow_logic.get("exit_conditions", []),
        "settings": {
            "allow_multiple_entries": False,
            "respect_quiet_hours": True,
            "timezone_aware": True
        },
        "performance_tracking": {
            "track_opens": True,
            "track_clicks": True,
            "track_conversions": True,
            "a_b_test_ready": False
        }
    }

def format_assets_for_export(visuals):
    """
    Format visual assets for export
    """
    assets = []
    
    for visual in visuals:
        assets.append({
            "id": f"asset_{len(assets) + 1}",
            "type": visual.get("type", "image"),
            "purpose": visual.get("purpose", ""),
            "description": visual.get("description", ""),
            "prompt": visual.get("prompt", ""),
            "url": visual.get("image_url", ""),
            "metadata": {
                "format": "png",
                "usage": visual.get("type", "header"),
                "ai_generated": True
            }
        })
    
    return assets

def get_trigger_event(campaign_type):
    """
    Get the main trigger event for campaign type
    """
    triggers = {
        "cart_abandonment": "cart_abandoned",
        "welcome_series": "user_subscribed",
        "win_back": "user_inactive",
        "post_purchase": "purchase_completed"
    }
    
    return triggers.get(campaign_type, "manual_trigger")

def calculate_read_time(text):
    """
    Calculate estimated reading time for email content
    """
    if not text:
        return "0 seconds"
    
    words = len(text.split())
    # Average reading speed: 200 words per minute
    minutes = words / 200
    
    if minutes < 1:
        return f"{int(minutes * 60)} seconds"
    else:
        return f"{int(minutes)} minute(s)"

def calculate_sms_segments(message):
    """
    Calculate SMS segments based on character count
    """
    if not message:
        return 0
    
    char_count = len(message)
    
    # SMS segment calculation (160 chars for single, 153 for multi-part)
    if char_count <= 160:
        return 1
    else:
        return (char_count - 1) // 153 + 1

def create_import_template():
    """
    Create a template for importing campaigns
    """
    template = {
        "campaign_info": {
            "name": "Campaign Name",
            "type": "cart_abandonment|welcome_series|win_back|post_purchase",
            "brand_tone": "Friendly|Professional|Casual|etc",
            "target_audience": "Gen Z|Millennials|etc"
        },
        "messages": [
            {
                "type": "email",
                "subject": "Email subject line",
                "body": "Email body content",
                "cta": "Call to action text",
                "delay": "1 hour|1 day|etc"
            },
            {
                "type": "sms",
                "message": "SMS message content (under 160 chars)",
                "delay": "2 hours|1 day|etc"
            }
        ],
        "settings": {
            "timezone": "UTC",
            "quiet_hours": {"start": "22:00", "end": "08:00"},
            "exit_conditions": ["unsubscribed", "purchase_completed"]
        }
    }
    
    return json.dumps(template, indent=2)
