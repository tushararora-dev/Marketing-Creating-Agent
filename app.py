import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os

# Import our custom modules
from campaign_generator import generate_campaign
from export_manager import export_campaign_json, export_campaign_csv
from utils import validate_prompt, get_campaign_preview

def main():
    st.set_page_config(
        page_title="Marketing Automation Agent",
        page_icon="📧",
        layout="wide"
    )
    
    st.title("📧 Marketing Automation Agent")
    st.subheader("Generate complete email/SMS campaigns with AI")
    
    # Sidebar for campaign settings
    with st.sidebar:
        st.header("Campaign Settings")
        
        # Brand information
        brand_name = st.text_input("Brand Name", value="", placeholder="e.g., SkinGlow Beauty")
        
        brand_category = st.selectbox(
            "Brand Category",
            ["Beauty & Skincare", "Fashion & Apparel", "Health & Fitness", "Technology", "Food & Beverage", "Home & Garden", "Travel", "Education", "Finance", "Other"]
        )
        
        brand_tone = st.selectbox(
            "Brand Tone",
            ["Friendly", "Professional", "Casual", "Luxury", "Playful", "Authoritative", "Caring", "Bold"]
        )
        
        # Audience settings
        target_audience = st.selectbox(
            "Target Audience",
            ["Gen Z (18-24)", "Millennials (25-40)", "Gen X (41-56)", "Baby Boomers (57+)", "All Ages"]
        )
        
        age_range = st.selectbox(
            "Age Range",
            ["18-24", "25-34", "35-44", "45-54", "55-64", "65+", "All ages"]
        )
        
        include_visuals = st.checkbox("Generate Visual Elements", value=True)
    
    # API keys (hidden from user)
    groq_api_key = "----"
    hf_api_key = "----"
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Campaign Input")
        
        # Example prompts
        st.subheader("Example Prompts:")
        example_prompts = [
            "Create a 7-email + 2-SMS cart abandonment sequence for a skincare brand",
            "Generate a 5-email welcome series for a fitness app",
            "Build a 4-email + 1-SMS win-back campaign for an e-commerce store",
            "Create a 6-email post-purchase nurture sequence for a SaaS product"
        ]
        
        for i, prompt in enumerate(example_prompts):
            if st.button(f"Use Example {i+1}", key=f"example_{i}"):
                st.session_state.user_prompt = prompt
        
        # Main prompt input
        user_prompt = st.text_area(
            "Describe your campaign:",
            value=st.session_state.get('user_prompt', ''),
            height=100,
            placeholder="e.g., Create a 7-email + 2-SMS cart abandonment sequence for a skincare brand targeting Gen Z women"
        )
        
        # Brand context input
        brand_context = st.text_area(
            "Brand Context (optional):",
            height=80,
            placeholder="Describe your brand, products, unique selling points, etc."
        )
        
        # Generate campaign button
        if st.button("🚀 Generate Campaign", type="primary"):
            if not user_prompt.strip():
                st.error("Please enter a campaign description.")
                return
            
            if not groq_api_key or not hf_api_key:
                st.error("Please provide both Groq and Hugging Face API keys.")
                return
            
            # Validate prompt
            validation_result = validate_prompt(user_prompt)
            if not validation_result["valid"]:
                st.error(f"Invalid prompt: {validation_result['message']}")
                return
            
            # Generate campaign
            with st.spinner("Generating your marketing campaign..."):
                try:
                    # Build enhanced brand context
                    enhanced_brand_context = f"{brand_context}\n\nBrand: {brand_name}\nCategory: {brand_category}\nAge Range: {age_range}" if brand_context else f"Brand: {brand_name}\nCategory: {brand_category}\nAge Range: {age_range}"
                    
                    campaign_data = generate_campaign(
                        prompt=user_prompt,
                        brand_name=brand_name,
                        brand_category=brand_category,
                        brand_tone=brand_tone,
                        target_audience=target_audience,
                        include_visuals=include_visuals,
                        groq_api_key=groq_api_key,
                        hf_api_key=hf_api_key
                    )
                    
                    st.session_state.campaign_data = campaign_data
                    st.success("Campaign generated successfully!")
                    
                except Exception as e:
                    st.error(f"Error generating campaign: {str(e)}")
                    return
    
    with col2:
        st.header("Campaign Actions")
        
        if 'campaign_data' in st.session_state:
            campaign = st.session_state.campaign_data
            
            # Export options
            st.subheader("Export Options")
            
            col_json, col_csv = st.columns(2)
            
            with col_json:
                if st.button("📄 Export JSON"):
                    json_data = export_campaign_json(campaign)
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name=f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            with col_csv:
                if st.button("📊 Export CSV"):
                    csv_data = export_campaign_csv(campaign)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
    
    # Campaign preview
    if 'campaign_data' in st.session_state:
        st.header("Campaign Preview")
        
        campaign = st.session_state.campaign_data
        
        # Tabs for different sections
        tab1, tab2, tab3 = st.tabs(["📧 Emails", "📱 SMS", "🎨 Visuals"])
        
        with tab1:
            emails = campaign.get('emails', [])
            for i, email in enumerate(emails):
                with st.expander(f"Email {i+1}: {email.get('subject', 'No Subject')}"):
                    st.write("**Subject:**", email.get('subject', ''))
                    st.write("**Body:**")
                    st.write(email.get('body', ''))
                    st.write("**CTA:**", email.get('cta', ''))
                    if email.get('delay'):
                        st.write("**Delay:**", email.get('delay', ''))
        
        with tab2:
            sms_messages = campaign.get('sms_messages', [])
            if sms_messages:
                for i, sms in enumerate(sms_messages):
                    with st.expander(f"SMS {i+1} - {sms.get('purpose', 'Message')}"):
                        st.write("**Message:**", sms.get('message', 'No message content'))
                        if sms.get('purpose'):
                            st.write("**Purpose:**", sms.get('purpose', ''))
                        if sms.get('delay'):
                            st.write("**Delay:**", sms.get('delay', ''))
                        # Debug info
                        st.caption(f"Characters: {len(sms.get('message', ''))}")
            else:
                st.write("No SMS messages generated")
        
        with tab3:
            visuals = campaign.get('visuals', [])
            if visuals:
                for i, visual in enumerate(visuals):
                    st.subheader(f"Visual {i+1}")
                    st.write("**Purpose:**", visual.get('purpose', ''))
                    st.write("**Description:**", visual.get('description', ''))
                    
                    # Show image if available
                    if visual.get('image_base64'):
                        try:
                            st.image(visual['image_base64'], caption=visual.get('purpose', ''), use_container_width=True)
                        except Exception as e:
                            st.write(f"Could not display image: {str(e)}")
                    elif visual.get('image_data'):
                        try:
                            st.image(visual['image_data'], caption=visual.get('purpose', ''), use_container_width=True)
                        except Exception as e:
                            st.write(f"Could not display image: {str(e)}")
                    elif visual.get('placeholder_text'):
                        st.info(f"**Visual Placeholder:** {visual['placeholder_text']}")
                    
                    # Always show the prompt used
                    if visual.get('prompt'):
                        st.write("**Image Prompt:**", visual.get('prompt', ''))
                    
                    # Show status
                    if visual.get('status'):
                        st.caption(f"Status: {visual['status']}")
                    
                    # Show any error message
                    if visual.get('error'):
                        st.error(f"Image generation failed: {visual['error']}")
            else:
                st.write("No visuals generated")

if __name__ == "__main__":
    main()
