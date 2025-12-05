import json
import openai
from tools import get_gold_price
import tools

class llmClient:
    def __init__(self, chat_model="gpt-4o-mini", translate_model="gpt-4o-mini"):
        self.chat_model = chat_model
        self.translate_model = translate_model
        self.tools = self.define_tools()
        self.target_language = "Vietnamese"
        self.investment_type = "Gold"
        self.system_message = f"You are a professional financial investment advisor specializing in {self.investment_type} investments.\
        Provide concise and actionable advice based on current market data and risk assessments.\
        if you don't know the answer, just say you don't know."
    
    def set_target_language(self, language):
        self.target_language = language
        
    def set_investment_type(self, investment_type):
        self.investment_type = investment_type
        
    def define_tools(self):
        """
        Define tools that can be used by the LLM.
        """
        gold_price_tool = {
            "name": "get_gold_price",
            "description": "Get the current gold price for a specified country.",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {
                        "type": "string",
                        "description": "The name of the country (e.g., USA, UK, Japan, Vietnam)."
                    },
                },
                "required": ["country"],
                "additionalProperties": False
            }
        }
        tools = [
            {"type": "function", "function": gold_price_tool},
        ]
        return tools   
        
    

    def translate(self, text, target_language):
        """
        Translate the given text to the target language using OpenAI.
        """
        system_content = f"You are a professional translator. Translate the given text to {target_language}. Maintain the meaning and tone. Only return the {target_language} translation, nothing else."
        try:
            response = openai.chat.completions.create(
                model=self.translate_model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Translation error: {e}"
    
    def handle_tool_call(self, message):
        """
        Handle tool calls made by the LLM.
        """
        tool_call = message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        if tool_name == "get_gold_price":
            country = tool_args.get("country")
            result = get_gold_price(country)
            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            }
        elif tool_name == "generate_gold_investment_advice":
            price = tool_args.get("price")
            currency = tool_args.get("currency")
            country = tool_args.get("country")
            history = tool_args.get("history", [])
            result = tools.generate_gold_investment_advice(price, currency, country, history)
            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            }
    
    def chat(self, history):
        """ Main chat function to interact with the LLM."""
        messages = [{'role': 'system', 'content': self.system_message}] + history

        response = openai.chat.completions.create(
            model=self.chat_model,
            messages=messages,
            tools=self.tools,
        )
        
        if response.choices[0].finish_reason == "tool_calls":
            message = response.choices[0].message
            tool_response = self.handle_tool_call(message)
            messages.append(message)
            messages.append(tool_response)
            response = openai.chat.completions.create(
                model=self.chat_model,
                messages=messages
            )
        
        reply = response.choices[0].message.content
        history += [{"role": "assistant", "content": reply}]
        
        translation = self.translate(reply, self.target_language)
        return history, translation
        