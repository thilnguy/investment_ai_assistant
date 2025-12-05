import gradio as gr
from llm_client import llmClient
from dotenv import load_dotenv
import os

def update_label(language):
    return gr.update(label=f"{language} Translation")

def update_target_language(language):
    llm_client.set_target_language(language)

def update_investment_type(investment_type):
    if investment_type is None:
        return
    llm_client.set_investment_type(investment_type)

load_dotenv()
chat_model = os.getenv("CHAT_MODEL", "gpt-4o-mini")
translate_model = os.getenv("TRANSLATE_MODEL", "gpt-4o-mini")
llm_client = llmClient(chat_model=chat_model, translate_model=translate_model)

def main():
    with gr.Blocks(title="Financial investment AI assistant") as ui:
        gr.Markdown("# Financial Investment AI Assistant")
        gr.Markdown(
            """
            This AI assistant supports and gives you valuable recommendations for financial investment (e.g., in gold or crypto).
            It receives your requirements via text or voice media, analyzes them, and provides output in a defined language.
            """
        )
        with gr.Row():
            with gr.Column():
                gr.Markdown("## English chat")
                chatbot = gr.Chatbot(label="Investment Chatbot")
                with gr.Row():
                    investment_type = gr.Dropdown(
                        choices=["Gold", "Crypto", "Stocks"],
                        value="Gold",
                        label="Select Investment Type",
                        interactive=True
                    )
                with gr.Row():
                    txt_input = gr.Textbox(
                        placeholder="Enter your investment query here (ex: current price, investment advice ...) ...",
                        label="Your Message",
                        lines=2,
                    )
                gr.Examples(examples=
                            ["What is the price of gold in usa?", 
                            "Can you give me investment advice for gold in Vietnam?", 
                            "What is the current price of gold in Japan?",
                            "Is it a good time to invest in gold in UK?",
                            "What are the risks of investing in gold in India?"], 
                            inputs=txt_input)
                with gr.Row():    
                    send_btn = gr.Button("Send", variant="primary")
                    clear_btn = gr.Button("Clear chat")
                
                gr.Markdown("### 🎤 Speech Input")
                speech_input = gr.Audio(type="filepath", label="Record your message")
                audio_content = gr.Textbox(
                    label="Transcribed Text from Speech",
                    lines=2,
                    interactive=False,
                )
            with gr.Column():
                gr.Markdown("## 🌐 Translation")
                language_dropdown = gr.Dropdown(
                    choices=["Vietnamese", "French"],
                    value="Vietnamese",
                    label="Select Target Language",
                    interactive=True
                )
                    
                translation_output = gr.Textbox(
                    label=f"Vietnamese Translation",
                    lines=15,
                    interactive=False,
                    text_align="left")
        
        # Event handlers
        language_dropdown.change(
            fn=update_label,
            inputs=language_dropdown,
            outputs=translation_output
        )
        
        language_dropdown.change(
            fn=update_target_language,
            inputs=language_dropdown,
            outputs=[]
        )
        
        investment_type.change(
            fn=update_investment_type,
            inputs=investment_type,
            outputs=[]
        )
        
        clear_btn.click(
            fn=lambda: ([], "", "", None),
            inputs=[],
            outputs=[chatbot, txt_input, translation_output, audio_content]
        )  
           
        send_btn.click(
            fn=process_investment_query,
            inputs=[txt_input, chatbot],
            outputs=[chatbot, translation_output],
        )
                
    ui.launch(theme=gr.themes.Soft(), inbrowser=True)

def process_investment_query(user_input, chat_history):
    """
    Process the investment query and return updated chat history and translation.
    """
    if user_input is None or user_input.strip() == "":
        return chat_history, ""
    
    chat_history += [{"role": "user", "content": user_input}]
    
    update_history, translation = llm_client.chat(chat_history)
    
    return update_history, translation

if __name__ == "__main__":
    main()
