import config.prompts as prompts
from llm.llm_client import client
import tools.tools as tools
from config.settings import settings


def translate(text, target_language):
        """
        Translate the given text to the target language using OpenAI.
        """
        system_content = prompts.translate_prompt(target_language)
        
        # Handle case where text is a list of messages, then translate the last chat message
        if type(text) == list:
            text = text[-1]['content'][0]["text"]
            
        try:
            response = client.chat.completions.create(
                model=settings.TRANSLATE_MODEL,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Translation error: {e}"

def _speed_to_text(audio_file):
    """
    Convert speech audio content to text using OpenAI's speech-to-text capabilities.
    """
    try:
        if audio_file is None:
            return "No audio content provided. Try again."
        
        with open(audio_file, "rb") as f:
            response = client.audio.transcriptions.create(
                model=settings.STT_MODEL,
                file=f,
                response_format="text"
            )
        return response
    except Exception as e:
        return f"Speech-to-text error: {e}"


def process_audio(audio_content):
    """
    Process the audio content, convert to text, and update chat history.
    """
    transcription = _speed_to_text(audio_content)
    return transcription, transcription


def generate_gold_investment_advice(price, currency, country, history):
    """
    Get investment advice from the LLM based on chat history and investment type.
    """
    
    risk_analysis = tools.get_risk_level_assessment(price, currency)
    risk_level = risk_analysis['risk_level']
    fallback_advice = risk_analysis['advice']
    
    system_prompt = prompts.investment_advice_prompt(
        risk_level, price, currency, country, fallback_advice
    )
    messages = [{"role": "system", "content": system_prompt}] + history
    response = client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=messages
    )
    
    return response.choices[0].message.content

def chat(history, investment_type=settings.DEFAULT_INVESTMENT_TYPE, target_language=settings.DEFAULT_TARGET_LANGUAGE):
        """ Main chat function to interact with the LLM."""
        messages = [{'role': 'system', 'content': prompts.chat_prompt(investment_type)}] + history       
        response = client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=messages,
            tools=tools.TOOLS,
        )
        
        while response.choices[0].finish_reason == "tool_calls":
            message = response.choices[0].message
            tool_response = tools.handle_tool_call(message)
            messages.append(message)
            messages.append(tool_response)
            response = client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=messages,
                tools=tools.TOOLS,
            )
        
        reply = response.choices[0].message.content
        history += [{"role": "assistant", "content": reply}]
        
        translation = translate(reply, target_language)
        return history, translation