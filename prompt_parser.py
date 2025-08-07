import json
import requests

def parse_campaign_prompt(prompt, groq_api_key):
    """
    Parse natural language prompt to extract campaign parameters
    """
    parsing_prompt = f"""
    Analyze this marketing campaign request and extract the key parameters in JSON format:
    
    Request: "{prompt}"
    
    Extract and return ONLY a JSON object with these fields:
    {{
        "campaign_type": "cart_abandonment|welcome_series|win_back|post_purchase|general",
        "email_count": <number of emails>,
        "sms_count": <number of SMS messages>,
        "brand_industry": "<inferred industry>",
        "target_audience": "<inferred audience>",
        "key_objectives": ["<objective1>", "<objective2>"]
    }}
    
    Rules:
    - If no specific numbers are mentioned, use reasonable defaults (5 emails, 2 SMS)
    - Infer campaign type from context keywords like "cart abandonment", "welcome", "win-back"
    - Return only valid JSON, no explanations
    """
    
    try:
        response = call_groq_api(parsing_prompt, groq_api_key)
        
        # Try to extract JSON from response
        response_text = response.strip()
        
        # Find JSON object in response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = response_text[start_idx:end_idx]
            parsed_data = json.loads(json_str)
            return parsed_data
        else:
            # Fallback parsing
            return fallback_parse_prompt(prompt)
    
    except Exception as e:
        print(f"Error parsing prompt: {e}")
        return fallback_parse_prompt(prompt)

def call_groq_api(prompt, api_key, model="llama3-8b-8192"):
    """
    Make API call to Groq
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 1000
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    result = response.json()
    return result["choices"][0]["message"]["content"]

def fallback_parse_prompt(prompt):
    """
    Fallback parser using keyword matching when API fails
    """
    prompt_lower = prompt.lower()
    
    # Extract numbers
    import re
    numbers = re.findall(r'\d+', prompt)
    email_count = 5
    sms_count = 2
    
    if len(numbers) >= 1:
        email_count = int(numbers[0])
    if len(numbers) >= 2:
        sms_count = int(numbers[1])
    
    # Determine campaign type
    campaign_type = "general"
    if "cart abandon" in prompt_lower or "abandon" in prompt_lower:
        campaign_type = "cart_abandonment"
    elif "welcome" in prompt_lower:
        campaign_type = "welcome_series"
    elif "win-back" in prompt_lower or "winback" in prompt_lower:
        campaign_type = "win_back"
    elif "post-purchase" in prompt_lower or "post purchase" in prompt_lower:
        campaign_type = "post_purchase"
    
    # Infer industry
    brand_industry = "general"
    industries = {
        "skincare": ["skincare", "beauty", "cosmetic"],
        "fitness": ["fitness", "gym", "workout", "health"],
        "ecommerce": ["store", "shop", "retail", "ecommerce"],
        "saas": ["saas", "software", "app", "platform"],
        "fashion": ["fashion", "clothing", "apparel"]
    }
    
    for industry, keywords in industries.items():
        if any(keyword in prompt_lower for keyword in keywords):
            brand_industry = industry
            break
    
    return {
        "campaign_type": campaign_type,
        "email_count": email_count,
        "sms_count": sms_count,
        "brand_industry": brand_industry,
        "target_audience": "general",
        "key_objectives": ["engagement", "conversion"]
    }
