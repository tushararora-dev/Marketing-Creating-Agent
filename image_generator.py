"""
Image generation module for creating brand-specific campaign visuals
"""
import requests


def generate_campaign_visuals(campaign_data, brand_info, hf_api_key):
    """
    Generate all visuals for a campaign with brand-specific styling
    """
    visuals = []
    
    try:
        # Extract campaign context
        campaign_context = {
            'campaign_type': campaign_data['type'],
            'brand_tone': brand_info['tone'],
            'target_audience': brand_info['audience']
        }
        
        # Generate campaign header
        header_visual = generate_campaign_header(campaign_context, brand_info, hf_api_key)
        if header_visual:
            visuals.append(header_visual)
        
        # Generate visuals for each email
        emails = campaign_data.get('emails', [])
        for i, email in enumerate(emails, 1):
            email_visual = generate_email_visual(email, campaign_context, brand_info, hf_api_key, i)
            if email_visual:
                visuals.append(email_visual)
    
    except Exception as e:
        print(f"Error generating visuals: {e}")
        # Return at least one placeholder visual
        visuals.append({
            "purpose": f"{brand_info['name']} Campaign Visual",
            "description": f"Brand visual for {brand_info['name']} campaign",
            "type": "placeholder",
            "placeholder_text": f"{brand_info['name']} - {brand_info['category']} Campaign",
            "status": "error",
            "error": str(e)
        })
    
    return visuals


def generate_campaign_header(campaign_context, brand_info, hf_api_key):
    """
    Generate main campaign header visual based on brand
    """
    prompt = build_brand_based_header_prompt(campaign_context, brand_info)
    
    try:
        image_result = generate_image_with_hf(prompt, hf_api_key)
        
        return {
            "purpose": f"{brand_info['name']} Campaign Header",
            "description": f"Brand header for {brand_info['name']} ({brand_info['category']}) {campaign_context['campaign_type']} campaign",
            "prompt": prompt,
            "image_data": image_result.get("image_data"),
            "image_base64": image_result.get("image_base64"),
            "placeholder_text": image_result.get("placeholder_text"),
            "status": image_result.get("status"),
            "type": "header"
        }
    
    except Exception as e:
        print(f"Error generating campaign header: {e}")
        return {
            "purpose": f"{brand_info['name']} Campaign Header",
            "description": f"Brand header for {brand_info['name']} ({brand_info['category']}) campaign",
            "prompt": prompt,
            "type": "header",
            "placeholder_text": f"{brand_info['name']} - {brand_info['category']} Campaign Visual",
            "status": "error",
            "error": str(e)
        }


def generate_email_visual(email, campaign_context, brand_info, hf_api_key, email_number):
    """
    Generate visual for specific email based on brand
    """
    prompt = build_brand_based_email_prompt(email, campaign_context, brand_info)
    
    try:
        image_result = generate_image_with_hf(prompt, hf_api_key)
        
        return {
            "purpose": f"{brand_info['name']} Email {email_number} - {email.get('purpose', 'General')}",
            "description": f"Brand visual for {brand_info['name']} email: {email.get('subject', 'No subject')}",
            "prompt": prompt,
            "image_data": image_result.get("image_data"),
            "image_base64": image_result.get("image_base64"),
            "placeholder_text": image_result.get("placeholder_text"),
            "status": image_result.get("status"),
            "type": "email_banner",
            "email_step": email_number
        }
    
    except Exception as e:
        print(f"Error generating email visual: {e}")
        return {
            "purpose": f"{brand_info['name']} Email {email_number} - {email.get('purpose', 'General')}",
            "description": f"Brand visual for {brand_info['name']} email: {email.get('subject', 'No subject')}",
            "prompt": prompt,
            "type": "email_banner",
            "email_step": email_number,
            "placeholder_text": f"{brand_info['name']} Email {email_number}: {email.get('subject', 'Email')}",
            "status": "error",
            "error": str(e)
        }


def build_brand_based_header_prompt(campaign_context, brand_info):
    """
    Build prompt for brand-specific product visual
    """
    brand_name = brand_info['name'] or "Brand"
    brand_category = brand_info['category'].lower()
    
    # Category-specific product visuals
    category_products = {
        "beauty & skincare": f"{brand_name} skincare product, cosmetic tube, premium beauty package, elegant design, spa aesthetic, natural lighting",
        "fashion & apparel": f"{brand_name} fashion brand logo, clothing tag, premium fabric texture, stylish design, fashion photography style",
        "health & fitness": f"{brand_name} fitness supplement bottle, protein container, gym equipment branded, athletic design, motivational",
        "technology": f"{brand_name} tech product, sleek device, modern gadget, innovative design, clean technology aesthetic",
        "food & beverage": f"{brand_name} food packaging, premium product label, delicious presentation, restaurant quality, fresh ingredients",
        "home & garden": f"{brand_name} home product, garden tool, cozy home decor, domestic lifestyle, comfortable living",
        "travel": f"{brand_name} travel gear, luggage tag, adventure equipment, wanderlust design, scenic background",
        "education": f"{brand_name} educational material, book cover, learning resource, academic design, knowledge focused",
        "finance": f"{brand_name} business card, professional document, secure design, trustworthy appearance, success oriented"
    }
    
    product_prompt = category_products.get(brand_category, f"{brand_name} branded product, professional design, high quality")
    
    full_prompt = f"Product photography of {product_prompt}, commercial photography, studio lighting, professional branding, high resolution"
    
    return full_prompt


def build_brand_based_email_prompt(email, campaign_context, brand_info):
    """
    Build prompt for brand-specific product visual variation
    """
    brand_name = brand_info['name'] or "Brand"
    brand_category = brand_info['category'].lower()
    
    # Different product angles/variations for each email
    category_variations = {
        "beauty & skincare": [
            f"{brand_name} skincare cream jar, top view, white background, luxury cosmetic",
            f"{brand_name} serum bottle, side profile, elegant glass, premium skincare",
            f"{brand_name} face mask package, front view, spa treatment, natural ingredients",
            f"{brand_name} moisturizer tube, angled view, minimalist design, beauty product"
        ],
        "fashion & apparel": [
            f"{brand_name} clothing label, close-up, premium fabric, fashion tag",
            f"{brand_name} branded accessory, lifestyle shot, stylish design",
            f"{brand_name} fashion logo, embroidered detail, high-end apparel",
            f"{brand_name} garment texture, fabric close-up, quality material"
        ],
        "health & fitness": [
            f"{brand_name} supplement bottle, gym setting, protein powder, fitness nutrition",
            f"{brand_name} sports equipment, branded gear, athletic performance",
            f"{brand_name} energy drink, active lifestyle, fitness motivation",
            f"{brand_name} workout accessory, exercise equipment, health brand"
        ],
        "technology": [
            f"{brand_name} tech device, sleek design, modern gadget, innovation",
            f"{brand_name} software interface, clean UI, digital product",
            f"{brand_name} electronic component, precision engineering, technology",
            f"{brand_name} smart device, futuristic design, connectivity"
        ]
    }
    
    # Get variations for the category, default to generic if not found
    variations = category_variations.get(brand_category, [
        f"{brand_name} branded product, professional photography",
        f"{brand_name} logo design, commercial branding",
        f"{brand_name} product package, retail display",
        f"{brand_name} business identity, corporate design"
    ])
    
    # Use email step to cycle through variations
    email_step = email.get('step', 1) - 1
    variation_index = email_step % len(variations)
    product_description = variations[variation_index]
    
    full_prompt = f"Product photography of {product_description}, commercial studio lighting, professional branding, high resolution, clean background"
    
    return full_prompt


def generate_image_with_hf(prompt, api_key):
    """
    Generate image using Hugging Face Stable Diffusion API
    """
    try:
        import base64
        import time
        
        # Try working Stable Diffusion models from 2024
        models = [
            "runwayml/stable-diffusion-v1-5",
            "stabilityai/stable-diffusion-xl-base-1.0", 
            "stabilityai/stable-diffusion-2-1-base",
            "black-forest-labs/FLUX.1-dev",
            "stabilityai/stable-diffusion-3-medium-diffusers"
        ]
        
        for model in models:
            try:
                url = f"https://api-inference.huggingface.co/models/{model}"
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "negative_prompt": "blurry, low quality, distorted",
                        "num_inference_steps": 20,
                        "guidance_scale": 7.5
                    }
                }
                
                response = requests.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    # Check if response is an image
                    if response.headers.get('content-type', '').startswith('image'):
                        image_bytes = response.content
                        image_base64 = base64.b64encode(image_bytes).decode()
                        
                        return {
                            "image_data": image_bytes,
                            "image_base64": f"data:image/png;base64,{image_base64}",
                            "status": "generated",
                            "model": model
                        }
                    else:
                        # Model might be loading, check response
                        try:
                            response_data = response.json()
                            if "estimated_time" in response_data:
                                print(f"Model {model} loading, estimated time: {response_data['estimated_time']}s")
                                continue
                        except:
                            continue
                
                elif response.status_code == 503:
                    # Model loading, try next one
                    print(f"Model {model} is loading, trying next model...")
                    continue
                else:
                    print(f"Error with model {model}: {response.status_code}")
                    continue
                    
            except Exception as e:
                print(f"Exception with model {model}: {str(e)}")
                continue
        
        # Create brand-specific product visuals using PIL
        return create_brand_product_visual(prompt)
        
    except Exception as e:
        # Final fallback - text placeholder
        placeholder_text = f"Visual for: {prompt[:100]}"
        
        return {
            "image_data": None,
            "image_base64": None,
            "placeholder_text": placeholder_text,
            "status": "text_placeholder",
            "model": "none"
        }


def create_brand_product_visual(prompt):
    """
    Create brand-specific product visuals based on brand name and category
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        import base64
        
        # Extract brand info from prompt
        brand_name = extract_brand_name_from_prompt(prompt)
        category = extract_category_from_prompt(prompt)
        
        # Create product visual based on category
        if "skincare" in category.lower() or "beauty" in category.lower():
            return create_skincare_product_visual(brand_name, prompt)
        elif "fashion" in category.lower() or "apparel" in category.lower():
            return create_fashion_visual(brand_name, prompt)
        elif "fitness" in category.lower() or "health" in category.lower():
            return create_fitness_visual(brand_name, prompt)
        elif "technology" in category.lower() or "tech" in category.lower():
            return create_tech_visual(brand_name, prompt)
        elif "food" in category.lower() or "beverage" in category.lower():
            return create_food_visual(brand_name, prompt)
        else:
            return create_generic_brand_visual(brand_name, category, prompt)
            
    except Exception as e:
        # Final fallback - text placeholder
        placeholder_text = f"Visual for: {prompt[:100]}"
        
        return {
            "image_data": None,
            "image_base64": None,
            "placeholder_text": placeholder_text,
            "status": "text_placeholder",
            "model": "none"
        }


def extract_brand_name_from_prompt(prompt):
    """Extract brand name from prompt"""
    if "Professional marketing banner for" in prompt:
        parts = prompt.split(",")
        if len(parts) > 0:
            return parts[0].replace("Professional marketing banner for ", "").strip()
    elif "Email marketing visual for" in prompt:
        parts = prompt.split(",")
        if len(parts) > 0:
            return parts[0].replace("Email marketing visual for ", "").strip()
    return "Brand"


def extract_category_from_prompt(prompt):
    """Extract category from prompt"""
    categories = ["beauty & skincare", "fashion & apparel", "health & fitness", "technology", "food & beverage", "home & garden", "travel", "education", "finance"]
    for cat in categories:
        if cat in prompt.lower():
            return cat
    return "general"


def create_skincare_product_visual(brand_name, prompt):
    """Create skincare product visual with tube/bottle design"""
    from PIL import Image, ImageDraw, ImageFont
    import io
    import base64
    
    width, height = 800, 400
    image = Image.new('RGB', (width, height), color='#f8f5f2')
    draw = ImageDraw.Draw(image)
    
    # Create gradient background (spa-like)
    for y in range(height):
        gradient = int(248 - (y / height) * 30)
        for x in range(width):
            image.putpixel((x, y), (gradient, gradient-5, gradient-10))
    
    draw = ImageDraw.Draw(image)
    
    # Draw skincare tube/bottle
    tube_x, tube_y = 150, 100
    tube_width, tube_height = 120, 200
    
    # Tube body (rounded rectangle)
    draw.rounded_rectangle([tube_x, tube_y, tube_x + tube_width, tube_y + tube_height], 
                          radius=20, fill='#ffffff', outline='#e0e0e0', width=2)
    
    # Tube cap
    cap_height = 30
    draw.rounded_rectangle([tube_x + 10, tube_y - cap_height, tube_x + tube_width - 10, tube_y + 5], 
                          radius=10, fill='#d4af37', outline='#b8941f', width=1)
    
    # Brand label on tube
    label_y = tube_y + 50
    draw.rectangle([tube_x + 10, label_y, tube_x + tube_width - 10, label_y + 60], 
                  fill='#f0f0f0', outline='#d0d0d0')
    
    # Load fonts
    try:
        brand_font = ImageFont.truetype("arial.ttf", 18)
        desc_font = ImageFont.truetype("arial.ttf", 12)
        title_font = ImageFont.truetype("arial.ttf", 36)
    except:
        brand_font = ImageFont.load_default()
        desc_font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # Brand name on tube
    brand_bbox = draw.textbbox((0, 0), brand_name, font=brand_font)
    brand_width = brand_bbox[2] - brand_bbox[0]
    brand_x = tube_x + (tube_width - brand_width) // 2
    draw.text((brand_x, label_y + 10), brand_name, fill='#333333', font=brand_font)
    
    # Product description on tube
    desc_text = "SKINCARE"
    desc_bbox = draw.textbbox((0, 0), desc_text, font=desc_font)
    desc_width = desc_bbox[2] - desc_bbox[0]
    desc_x = tube_x + (tube_width - desc_width) // 2
    draw.text((desc_x, label_y + 35), desc_text, fill='#666666', font=desc_font)
    
    # Main title
    title = f"{brand_name} Skincare Collection"
    title_x = 350
    draw.text((title_x, 80), title, fill='#2c3e50', font=title_font)
    
    # Subtitle
    subtitle = "Premium Beauty Solutions"
    draw.text((title_x, 130), subtitle, fill='#7f8c8d', font=brand_font)
    
    # Product benefits
    benefits = ["✓ Natural Ingredients", "✓ Dermatologist Tested", "✓ Anti-aging Formula"]
    for i, benefit in enumerate(benefits):
        draw.text((title_x, 170 + i * 25), benefit, fill='#27ae60', font=desc_font)
    
    # Add some decorative elements (botanical)
    # Simple leaf shapes
    draw.ellipse([600, 150, 650, 180], fill='#a8d5a8', outline='#7cb97c')
    draw.ellipse([680, 120, 720, 160], fill='#b5e0b5', outline='#8cc68c')
    
    # Convert to base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_bytes = buffer.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode()
    
    return {
        "image_data": image_bytes,
        "image_base64": f"data:image/png;base64,{image_base64}",
        "status": "brand_visual_generated",
        "model": "PIL_skincare"
    }


def create_fashion_visual(brand_name, prompt):
    """Create fashion brand visual"""
    from PIL import Image, ImageDraw, ImageFont
    import io
    import base64
    
    width, height = 800, 400
    image = Image.new('RGB', (width, height), color='#1a1a1a')
    draw = ImageDraw.Draw(image)
    
    # Fashion-style background
    for y in range(height):
        shade = int(26 + (y / height) * 40)
        for x in range(width):
            image.putpixel((x, y), (shade, shade, shade))
    
    draw = ImageDraw.Draw(image)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 48)
        subtitle_font = ImageFont.truetype("arial.ttf", 24)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Brand name in elegant style
    brand_bbox = draw.textbbox((0, 0), brand_name, font=title_font)
    brand_width = brand_bbox[2] - brand_bbox[0]
    brand_x = (width - brand_width) // 2
    
    # Draw brand name with golden effect
    draw.text((brand_x + 2, 152), brand_name, fill='#000000', font=title_font)  # Shadow
    draw.text((brand_x, 150), brand_name, fill='#d4af37', font=title_font)      # Gold
    
    # Fashion tagline
    tagline = "FASHION COLLECTION"
    tagline_bbox = draw.textbbox((0, 0), tagline, font=subtitle_font)
    tagline_width = tagline_bbox[2] - tagline_bbox[0]
    tagline_x = (width - tagline_width) // 2
    draw.text((tagline_x, 220), tagline, fill='#ffffff', font=subtitle_font)
    
    # Decorative lines
    draw.rectangle([200, 280, 600, 285], fill='#d4af37')
    
    # Convert to base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_bytes = buffer.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode()
    
    return {
        "image_data": image_bytes,
        "image_base64": f"data:image/png;base64,{image_base64}",
        "status": "brand_visual_generated",
        "model": "PIL_fashion"
    }


def create_fitness_visual(brand_name, prompt):
    """Create fitness brand visual"""
    from PIL import Image, ImageDraw, ImageFont
    import io
    import base64
    
    width, height = 800, 400
    image = Image.new('RGB', (width, height), color='#ff6b35')
    draw = ImageDraw.Draw(image)
    
    # Energetic gradient background
    for y in range(height):
        r = int(255 - (y / height) * 50)
        g = int(107 + (y / height) * 30)
        b = int(53 - (y / height) * 20)
        for x in range(width):
            image.putpixel((x, y), (r, g, b))
    
    draw = ImageDraw.Draw(image)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 42)
        subtitle_font = ImageFont.truetype("arial.ttf", 20)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Brand name
    brand_bbox = draw.textbbox((0, 0), brand_name, font=title_font)
    brand_width = brand_bbox[2] - brand_bbox[0]
    brand_x = (width - brand_width) // 2
    
    draw.text((brand_x + 3, 153), brand_name, fill='#000000', font=title_font)  # Shadow
    draw.text((brand_x, 150), brand_name, fill='#ffffff', font=title_font)      # White
    
    # Fitness tagline
    tagline = "FITNESS & WELLNESS"
    tagline_bbox = draw.textbbox((0, 0), tagline, font=subtitle_font)
    tagline_width = tagline_bbox[2] - tagline_bbox[0]
    tagline_x = (width - tagline_width) // 2
    draw.text((tagline_x, 210), tagline, fill='#ffffff', font=subtitle_font)
    
    # Motivational text
    motivation = "UNLEASH YOUR POTENTIAL"
    mot_bbox = draw.textbbox((0, 0), motivation, font=subtitle_font)
    mot_width = mot_bbox[2] - mot_bbox[0]
    mot_x = (width - mot_width) // 2
    draw.text((mot_x, 250), motivation, fill='#ffff00', font=subtitle_font)
    
    # Convert to base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_bytes = buffer.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode()
    
    return {
        "image_data": image_bytes,
        "image_base64": f"data:image/png;base64,{image_base64}",
        "status": "brand_visual_generated",
        "model": "PIL_fitness"
    }


def create_tech_visual(brand_name, prompt):
    """Create technology brand visual"""
    from PIL import Image, ImageDraw, ImageFont
    import io
    import base64
    
    width, height = 800, 400
    image = Image.new('RGB', (width, height), color='#0d1421')
    draw = ImageDraw.Draw(image)
    
    # Tech gradient background
    for y in range(height):
        for x in range(width):
            r = int(13 + (x / width) * 30)
            g = int(20 + (y / height) * 40)
            b = int(33 + ((x + y) / (width + height)) * 60)
            image.putpixel((x, y), (r, g, b))
    
    draw = ImageDraw.Draw(image)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 40)
        subtitle_font = ImageFont.truetype("arial.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Brand name with tech style
    brand_bbox = draw.textbbox((0, 0), brand_name, font=title_font)
    brand_width = brand_bbox[2] - brand_bbox[0]
    brand_x = (width - brand_width) // 2
    
    draw.text((brand_x, 150), brand_name, fill='#00ffff', font=title_font)
    
    # Tech tagline
    tagline = "INNOVATIVE TECHNOLOGY"
    tagline_bbox = draw.textbbox((0, 0), tagline, font=subtitle_font)
    tagline_width = tagline_bbox[2] - tagline_bbox[0]
    tagline_x = (width - tagline_width) // 2
    draw.text((tagline_x, 210), tagline, fill='#ffffff', font=subtitle_font)
    
    # Tech elements (circuit-like lines)
    draw.rectangle([100, 300, 700, 302], fill='#00ffff')
    draw.rectangle([200, 280, 202, 320], fill='#00ffff')
    draw.rectangle([600, 280, 602, 320], fill='#00ffff')
    
    # Convert to base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_bytes = buffer.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode()
    
    return {
        "image_data": image_bytes,
        "image_base64": f"data:image/png;base64,{image_base64}",
        "status": "brand_visual_generated",
        "model": "PIL_tech"
    }


def create_food_visual(brand_name, prompt):
    """Create food & beverage brand visual"""
    from PIL import Image, ImageDraw, ImageFont
    import io
    import base64
    
    width, height = 800, 400
    image = Image.new('RGB', (width, height), color='#ffe4b5')
    draw = ImageDraw.Draw(image)
    
    # Warm food background
    for y in range(height):
        r = int(255 - (y / height) * 20)
        g = int(228 - (y / height) * 40)
        b = int(181 - (y / height) * 60)
        for x in range(width):
            image.putpixel((x, y), (r, g, b))
    
    draw = ImageDraw.Draw(image)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 38)
        subtitle_font = ImageFont.truetype("arial.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Brand name
    brand_bbox = draw.textbbox((0, 0), brand_name, font=title_font)
    brand_width = brand_bbox[2] - brand_bbox[0]
    brand_x = (width - brand_width) // 2
    
    draw.text((brand_x + 2, 152), brand_name, fill='#8b4513', font=title_font)  # Shadow
    draw.text((brand_x, 150), brand_name, fill='#d2691e', font=title_font)      # Orange
    
    # Food tagline
    tagline = "DELICIOUS & FRESH"
    tagline_bbox = draw.textbbox((0, 0), tagline, font=subtitle_font)
    tagline_width = tagline_bbox[2] - tagline_bbox[0]
    tagline_x = (width - tagline_width) // 2
    draw.text((tagline_x, 210), tagline, fill='#8b4513', font=subtitle_font)
    
    # Convert to base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_bytes = buffer.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode()
    
    return {
        "image_data": image_bytes,
        "image_base64": f"data:image/png;base64,{image_base64}",
        "status": "brand_visual_generated",
        "model": "PIL_food"
    }


def create_generic_brand_visual(brand_name, category, prompt):
    """Create generic brand visual"""
    from PIL import Image, ImageDraw, ImageFont
    import io
    import base64
    
    width, height = 800, 400
    image = Image.new('RGB', (width, height), color='#4a90e2')
    draw = ImageDraw.Draw(image)
    
    # Generic gradient background
    for y in range(height):
        for x in range(width):
            r = int(74 + (x / width) * 100)
            g = int(144 + (y / height) * 50)
            b = int(226 - (x / width) * 50)
            image.putpixel((x, y), (r, g, b))
    
    draw = ImageDraw.Draw(image)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 36)
        subtitle_font = ImageFont.truetype("arial.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Brand name
    brand_bbox = draw.textbbox((0, 0), brand_name, font=title_font)
    brand_width = brand_bbox[2] - brand_bbox[0]
    brand_x = (width - brand_width) // 2
    
    draw.text((brand_x + 2, 152), brand_name, fill='#000000', font=title_font)  # Shadow
    draw.text((brand_x, 150), brand_name, fill='#ffffff', font=title_font)      # White
    
    # Category
    cat_text = category.upper()
    cat_bbox = draw.textbbox((0, 0), cat_text, font=subtitle_font)
    cat_width = cat_bbox[2] - cat_bbox[0]
    cat_x = (width - cat_width) // 2
    draw.text((cat_x, 210), cat_text, fill='#ffffff', font=subtitle_font)
    
    # Convert to base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_bytes = buffer.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode()
    
    return {
        "image_data": image_bytes,
        "image_base64": f"data:image/png;base64,{image_base64}",
        "status": "brand_visual_generated",
        "model": "PIL_generic"
    }