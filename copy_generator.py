import json
from prompt_parser import call_groq_api

def generate_email_copy(purpose, step_number, campaign_context, groq_api_key):
    """
    Generate email copy for a specific purpose and context
    """
    prompt = build_email_prompt(purpose, step_number, campaign_context)
    
    try:
        response = call_groq_api(prompt, groq_api_key)
        
        # Try to parse JSON response
        response_text = response.strip()
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = response_text[start_idx:end_idx]
            email_data = json.loads(json_str)
        else:
            # Fallback - create structure from text
            email_data = parse_email_from_text(response_text, purpose)
        
        # Add metadata
        email_data["purpose"] = purpose
        email_data["step"] = step_number
        email_data["delay"] = get_email_delay(step_number, campaign_context["campaign_type"])
        
        return email_data
    
    except Exception as e:
        print(f"Error generating email copy: {e}")
        return create_fallback_email(purpose, step_number, campaign_context)

def generate_sms_copy(purpose, step_number, campaign_context, groq_api_key):
    """
    Generate SMS copy for a specific purpose and context
    """
    prompt = build_sms_prompt(purpose, step_number, campaign_context)
    
    try:
        response = call_groq_api(prompt, groq_api_key)
        
        # Try to parse JSON response
        response_text = response.strip()
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = response_text[start_idx:end_idx]
            sms_data = json.loads(json_str)
        else:
            # Fallback - create structure from text
            sms_data = {"message": response_text.strip()}
        
        # Add metadata
        sms_data["purpose"] = purpose
        sms_data["step"] = step_number
        sms_data["delay"] = get_sms_delay(step_number, campaign_context["campaign_type"])
        
        return sms_data
    
    except Exception as e:
        print(f"Error generating SMS copy: {e}")
        return create_fallback_sms(purpose, step_number, campaign_context)

def build_email_prompt(purpose, step_number, campaign_context):
    """
    Build prompt for email generation
    """
    return f"""
    Create an email for a {campaign_context['campaign_type']} campaign.
    
    Context:
    - Purpose: {purpose}
    - Step: {step_number}
    - Brand tone: {campaign_context['brand_tone']}
    - Target audience: {campaign_context['target_audience']}
    - Brand context: {campaign_context.get('brand_context', 'Not specified')}
    
    Generate an email with the following specifications:
    - Tone should be {campaign_context['brand_tone'].lower()}
    - Target {campaign_context['target_audience']} audience
    - Purpose is: {purpose}
    
    Return ONLY a JSON object with these fields:
    {{
        "subject": "<compelling subject line>",
        "body": "<email body text - engaging and action-oriented>",
        "cta": "<call-to-action text>"
    }}
    
    Rules:
    - Subject line should be attention-grabbing and under 50 characters
    - Body should be 50-150 words, scannable, and persuasive
    - CTA should be action-oriented and specific
    - Match the brand tone exactly
    - No placeholders or brackets in the final copy
    """

def build_sms_prompt(purpose, step_number, campaign_context):
    """
    Build prompt for SMS generation
    """
    return f"""
    Create an SMS message for a {campaign_context['campaign_type']} campaign.
    
    Context:
    - Purpose: {purpose}
    - Step: {step_number}
    - Brand tone: {campaign_context['brand_tone']}
    - Target audience: {campaign_context['target_audience']}
    - Brand context: {campaign_context.get('brand_context', 'Not specified')}
    
    Generate a short SMS message (under 160 characters) that:
    - Uses {campaign_context['brand_tone'].lower()} tone
    - Targets {campaign_context['target_audience']} audience
    - Serves the purpose: {purpose}
    - Includes a clear call-to-action
    
    Return ONLY a JSON object:
    {{
        "message": "<SMS message text under 160 characters>"
    }}
    
    Rules:
    - Keep under 160 characters total
    - Be direct and action-oriented
    - Include urgency when appropriate
    - No placeholders or brackets
    """

def parse_email_from_text(text, purpose):
    """
    Parse email components from unstructured text response
    """
    lines = text.strip().split('\n')
    
    email_data = {
        "subject": f"Don't miss out - {purpose}",
        "body": text[:200] + "..." if len(text) > 200 else text,
        "cta": "Take Action Now"
    }
    
    # Try to extract components
    for line in lines:
        line = line.strip()
        if line.startswith('Subject:'):
            email_data["subject"] = line.replace('Subject:', '').strip()
        elif line.startswith('Body:'):
            email_data["body"] = line.replace('Body:', '').strip()
        elif line.startswith('CTA:'):
            email_data["cta"] = line.replace('CTA:', '').strip()
    
    return email_data

def create_fallback_email(purpose, step_number, campaign_context):
    """
    Create a fallback email when generation fails
    """
    subject_templates = {
        "Reminder": "Don't forget about your items",
        "Urgency": "Only a few hours left!",
        "Welcome": "Welcome to our community!",
        "Social Proof": "Join thousands of happy customers",
        "Offer": "Special offer just for you"
    }
    
    return {
        "subject": subject_templates.get(purpose, f"Important message - Step {step_number}"),
        "body": f"This is a {purpose.lower()} message for your {campaign_context['campaign_type']} campaign. We've prepared something special for you based on your interests.",
        "cta": "Learn More",
        "purpose": purpose,
        "step": step_number,
        "delay": get_email_delay(step_number, campaign_context["campaign_type"])
    }

def create_fallback_sms(purpose, step_number, campaign_context):
    """
    Create a fallback SMS when generation fails
    """
    return {
        "message": f"Quick reminder about your {purpose.lower()}. Don't miss out! Reply STOP to opt out.",
        "purpose": purpose,
        "step": step_number,
        "delay": get_sms_delay(step_number, campaign_context["campaign_type"])
    }

def get_email_delay(step_number, campaign_type):
    """
    Get appropriate delay for email based on step and campaign type
    """
    delay_patterns = {
        "cart_abandonment": ["1 hour", "6 hours", "1 day", "2 days", "4 days", "1 week", "2 weeks"],
        "welcome_series": ["immediate", "1 day", "3 days", "1 week", "2 weeks", "1 month"],
        "win_back": ["immediate", "3 days", "1 week", "2 weeks"],
        "post_purchase": ["immediate", "3 days", "1 week", "2 weeks", "1 month", "3 months"]
    }
    
    pattern = delay_patterns.get(campaign_type, ["1 day"] * 10)
    
    if step_number <= len(pattern):
        return pattern[step_number - 1]
    else:
        return "1 week"

def get_sms_delay(step_number, campaign_type):
    """
    Get appropriate delay for SMS based on step and campaign type
    """
    delay_patterns = {
        "cart_abandonment": ["2 hours", "1 day"],
        "welcome_series": ["1 hour", "1 week"],
        "win_back": ["1 day", "1 week"],
        "post_purchase": ["1 day", "1 week"]
    }
    
    pattern = delay_patterns.get(campaign_type, ["1 day"] * 10)
    
    if step_number <= len(pattern):
        return pattern[step_number - 1]
    else:
        return "3 days"
