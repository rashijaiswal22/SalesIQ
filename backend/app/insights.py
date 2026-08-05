import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def generate_business_insights(historical_sample, forecast_data, metrics=None, insight_type="all"):
    if not api_key:
        return {"insights": "⚠️ **GEMINI_API_KEY Missing**"}

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
        fallback_heading = "### 📦 Stock Refill Advice"
        
    elif insight_type == "revenue":
        prompt_instruction = f"""
        {formatting_rules}
        Focus ONLY on **Revenue Optimization Strategy** 💰.
        - Strategic pricing adjustments or upsell recommendations.
        - Best promo strategies for peak forecast days.
        """
        fallback_heading = "### 💰 Revenue Optimization"
        
    elif insight_type == "risk":
        prompt_instruction = f"""
        {formatting_rules}
        Focus ONLY on **Business Risk & Overstock Warnings** ⚠️.
        - Point out low-demand periods and holding cost risks.
        - Give 2 quick action steps to avoid inventory bottleneck.
        """
        fallback_heading = "### ⚠️ Risk & Overstock Alert"
        
    elif insight_type == "marketing":
        prompt_instruction = f"""
        {formatting_rules}
        Focus ONLY on **Marketing & Promotion Copy** 📢.
        - Draft a short 3-line catchy Marketing Email.
        - Draft a 1-line promotional SMS with a CTA.
        """
        fallback_heading = "### 📢 Marketing & Promo Campaign"
        
    else:
        prompt_instruction = f"""
        {formatting_rules}
        Give a brief, 3-bullet summary covering:
        1. 📈 Forecast Trend
        2. 📦 Quick Stock Action
        3. 💰 Quick Revenue Tip
        """
        fallback_heading = "### 📊 Business Intelligence Brief"

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
        error_details = str(e)
        return {
            "insights": (
                f"{fallback_heading} *(Fallback Mode)*\n\n"
                f"* 🚀 **Demand Status:** Continuous positive momentum detected.\n"
                f"* 🛡️ **Quick Action:** Maintain a **+15% safety stock** buffer.\n"
                f"* 💡 **Growth Tip:** Target promotions during high-demand cycles.\n\n"
                f"*(Note: Live GenAI Status -> {error_details})*"
            )
        }

def generate_general_chat_response(query):
    if not api_key:
        return {"insights": "⚠️ **Something went wrong. Unable to answer.**"}
        
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
        return {"insights": f"⚠️ **Service Notice:** Unable to reach AI. ({str(e)})"}