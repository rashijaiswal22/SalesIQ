import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def generate_business_insights(historical_sample, forecast_data, metrics=None, insight_type="all"):
    if not api_key:
        return {"insights": "⚠️ **GEMINI_API_KEY Missing** in .env file."}

    formatting_rules = """
    CRITICAL FORMATTING INSTRUCTIONS:
    - Keep response SHORT, CONCISE, and DIRECT (maximum 4 bullet points).
    - Use relevant emojis generously (e.g., 📦, 📈, ⚠️, 💡, 🏷️).
    - Avoid long paragraphs. Use bold headers and short bullet points.
    - Do NOT start with greetings like "Hey there" or "Hello". Start directly with the insights.
    """

    if insight_type == "stock":
        prompt_instruction = f"""
        {formatting_rules}
        Focus ONLY on **Stock Refill Recommendations** 📦.
        - Give exact reorder points or safety stock percentages based on forecast.
        - Mention high-demand peak days to prepare for.
        """
        fallback_text = (
            "### 📦 Stock Refill Advice \n\n"
            "* 📦 **Inventory Buffer:** Maintain a **+15% safety stock** for peak demand days.\n"
            "* 🔄 **Reorder Threshold:** Trigger reorder when stock drops below 20% capacity.\n"
            "* 🚚 **Supplier Action:** Coordinate with suppliers 3 days prior to peak cycles."
        )
        
    elif insight_type == "revenue":
        prompt_instruction = f"""
        {formatting_rules}
        Focus ONLY on **Revenue Optimization Strategy** 💰.
        - Strategic pricing adjustments or upsell recommendations.
        - Best promo strategies for peak forecast days.
        """
        fallback_text = (
            "### 💰 Revenue Optimization \n\n"
            "* 🏷️ **Dynamic Pricing:** Apply a 5-10% promo discount during slow sales days.\n"
            "* 📦 **Bundle Strategy:** Pair top-selling items with slow-moving inventory.\n"
            "* 💳 **Upsell Target:** Offer checkout add-ons during high-traffic weekend periods."
        )
        
    elif insight_type == "risk":
        prompt_instruction = f"""
        {formatting_rules}
        Focus ONLY on **Business Risk & Overstock Warnings** ⚠️.
        - Point out low-demand periods and holding cost risks.
        - Give 2 quick action steps to avoid inventory bottleneck.
        """
        fallback_text = (
            "### ⚠️ Risk & Overstock Alert \n\n"
            "* 📉 **Demand Drop:** Watch out for low sales cycles mid-week to avoid overstock.\n"
            "* 💸 **Holding Costs:** Clear aging inventory to prevent tied-up capital.\n"
            "* 🛡️ **Mitigation:** Limit bulk purchasing for items with fluctuating demand."
        )
        
    elif insight_type == "marketing":
        prompt_instruction = f"""
        {formatting_rules}
        Focus ONLY on **Marketing & Promotion Copy** 📢.
        - Draft a short 3-line catchy Marketing Email.
        - Draft a 1-line promotional SMS with a CTA.
        """
        fallback_text = (
            "### 📢 Marketing & Promo Campaign *(Offline Mode)*\n\n"
            "* 📧 **Email Idea:** 'Unbeatable Deals This Week! Get up to 20% off on top-rated products.'\n"
            "* 📱 **SMS CTA:** 'Flash Sale Alert! Use code SALES20 today at checkout. Shop now!'\n"
            "* 🎯 **Target Audience:** Re-engage recent visitors with weekend discount alerts."
        )
        
    else:
        prompt_instruction = f"""
        {formatting_rules}
        Give a brief, 3-bullet summary covering:
        1. 📈 Forecast Trend
        2. 📦 Quick Stock Action
        3. 💰 Quick Revenue Tip
        """
        fallback_text = (
            "### 📊 Business Intelligence Brief *(Offline Mode)*\n\n"
            "* 📈 **Forecast Trend:** Stable demand momentum predicted for the upcoming cycle.\n"
            "* 📦 **Quick Stock Action:** Keep safety buffer aligned with high-volume sales days.\n"
            "* 💰 **Quick Revenue Tip:** Run flash discounts during low-demand time slots."
        )

    try:
        client = genai.Client(api_key=api_key)
        recent_history = historical_sample[:5] if isinstance(historical_sample, list) else historical_sample

        prompt = f"""
        You are SalesIQ AI, a Retail Business Assistant.
        Data Context:
        - MAE: {metrics.get('mae') if metrics else 'N/A'} | R2 Score: {metrics.get('r2_score') if metrics else 'N/A'}
        - Recent History: {recent_history}
        - Forecast: {forecast_data}

        {prompt_instruction}
        """

        supported_models = ['gemini-2.0-flash', 'gemini-flash-latest']
        response_text = None
        last_error = None

        for model_name in supported_models:
            try:
                res = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if res and res.text:
                    response_text = res.text
                    break
            except Exception as e:
                last_error = str(e)
                if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                    time.sleep(2)
                continue

        if response_text:
            return {"insights": response_text}
        else:
            raise Exception(last_error if last_error else "Execution failed")

    except Exception as e:
        # Fallback with type-specific static content
        return {"insights": fallback_text}


def generate_general_chat_response(query):
    if not api_key:
        return {"insights": "⚠️ **GEMINI_API_KEY Missing** in .env file."}
        
    prompt = f"""
    You are SalesIQ AI Copilot. Answer the retail/business question concisely with emojis.
    Keep response under 4 bullet points. Be energetic, friendly, and practical.
    Do NOT start with greetings like "Hey there". Start directly with the answer.
    
    User Query: {query}
    """
    
    try:
        client = genai.Client(api_key=api_key)
        res = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        return {"insights": res.text if res else "🤖 Ready to assist with your retail operations!"}
    except Exception as e:
        return {
            "insights": (
                "⚠️ **Network Connection Issue**\n\n"
                "* 🌐 **Status:** Unable to connect to Google GenAI servers.\n"
                "* 🔧 **Fix:** Please check your internet connection or turn off active VPNs.\n"
                f"* 🛠️ **Technical Log:** `{str(e)}`"
            )
        }