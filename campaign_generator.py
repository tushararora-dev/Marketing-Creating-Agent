import json
from prompt_parser import parse_campaign_prompt
from copy_generator import generate_email_copy, generate_sms_copy
from image_generator import generate_campaign_visuals

def generate_campaign(prompt, brand_name="", brand_category="", brand_tone="Friendly", target_audience="All Ages", include_visuals=True, groq_api_key="", hf_api_key=""):
    """
    Main function to generate a complete marketing campaign based on user prompt
    """
    # Parse the initial prompt
    parsed_data = parse_campaign_prompt(prompt, groq_api_key)
    
    # Enhance with brand context
    campaign_context = {
        "brand_name": brand_name,
        "brand_category": brand_category,
        "brand_tone": brand_tone,
        "target_audience": target_audience,
        "campaign_type": parsed_data.get("campaign_type", "general"),
        "email_count": parsed_data.get("email_count", 5),
        "sms_count": parsed_data.get("sms_count", 2)
    }
    
    # Generate email copy
    emails = []
    for i in range(campaign_context["email_count"]):
        email_purpose = get_email_purpose(i, campaign_context["campaign_type"], campaign_context["email_count"])
        email = generate_email_copy(
            purpose=email_purpose,
            step_number=i+1,
            campaign_context=campaign_context,
            groq_api_key=groq_api_key
        )
        emails.append(email)
    
    # Generate SMS copy
    sms_messages = []
    for i in range(campaign_context["sms_count"]):
        sms_purpose = get_sms_purpose(i, campaign_context["campaign_type"], campaign_context["sms_count"])
        sms = generate_sms_copy(
            purpose=sms_purpose,
            step_number=i+1,
            campaign_context=campaign_context,
            groq_api_key=groq_api_key
        )
        sms_messages.append(sms)
    
    # Generate visuals if requested
    visuals = []
    if include_visuals:
        # Prepare campaign data and brand info for visuals
        campaign_data = {
            "type": campaign_context["campaign_type"],
            "emails": emails
        }
        
        brand_info = {
            "name": brand_name,
            "category": brand_category,
            "tone": brand_tone,
            "audience": target_audience
        }
        
        visuals = generate_campaign_visuals(
            campaign_data=campaign_data,
            brand_info=brand_info,
            hf_api_key=hf_api_key
        )
    
    # No flow logic needed - removed per user request
    
    # Compile final campaign data
    final_campaign_data = {
        "campaign_type": campaign_context["campaign_type"],
        "brand_name": brand_name,
        "brand_category": brand_category,
        "brand_tone": campaign_context["brand_tone"],
        "target_audience": campaign_context["target_audience"],
        "emails": emails,
        "sms_messages": sms_messages,
        "visuals": visuals,
        "metadata": {
            "generated_at": str(json.dumps({"timestamp": "now"})),
            "total_steps": len(emails) + len(sms_messages)
        }
    }
    
    return final_campaign_data

def get_email_purpose(step_number, campaign_type, total_emails):
    """
    Determine the purpose of each email based on campaign type and step number
    """
    campaign_structures = {
        "cart_abandonment": [
            "Reminder", "Gentle Nudge", "Social Proof", "Urgency", 
            "Last Chance", "Win-back Offer", "Final Reminder"
        ],
        "welcome_series": [
            "Welcome", "Brand Story", "Product Education", "Social Proof",
            "First Purchase Incentive", "Community Building"
        ],
        "win_back": [
            "We Miss You", "Exclusive Offer", "What's New", "Final Attempt"
        ],
        "post_purchase": [
            "Thank You", "Product Tips", "Upsell", "Review Request", 
            "Loyalty Program", "Referral"
        ]
    }
    
    structure = campaign_structures.get(campaign_type, ["General Message"] * total_emails)
    
    if step_number < len(structure):
        return structure[step_number]
    else:
        return structure[-1] if structure else "General Message"

def get_sms_purpose(step_number, campaign_type, total_sms):
    """
    Determine the purpose of each SMS based on campaign type and step number
    """
    sms_purposes = {
        "cart_abandonment": ["Quick Reminder", "Urgency + Offer"],
        "welcome_series": ["Welcome SMS", "Quick Tip"],
        "win_back": ["Miss You", "Exclusive Deal"],
        "post_purchase": ["Thank You", "Review Request"]
    }
    
    structure = sms_purposes.get(campaign_type, ["General SMS"] * total_sms)
    
    if step_number < len(structure):
        return structure[step_number]
    else:
        return structure[-1] if structure else "General SMS"
