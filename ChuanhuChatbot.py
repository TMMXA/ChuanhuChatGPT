import gradio as gr
import openai

my_api_key = ""
initial_prompt = "You are a helpful assistant."

class ChatGPT:

    def __init__(self, apikey) -> None:
        openai.api_key = apikey
        self.system = {"role": "system", "content": initial_prompt}


    def get_response(self, messages):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[self.system, *messages],
        )
        response = response["choices"][0]["message"]["content"]
        return response

    def predict(self, input_sentence, context):
        context.append({"role": "user", "content": f"{input_sentence}"})

        response = self.get_response(context)

        context.append({"role": "assistant", "content": response})

        response = []

        for i in range(0, len(context), 2):
            response.append((context[i]["content"], context[i+1]["content"]))

        return response, context

    def retry(self, context):
        response = self.get_response(context[:-1])
        context[-1] = {"role": "assistant", "content": response}
        response = []
        for i in range(0, len(context), 2):
            response.append((context[i]["content"], context[i+1]["content"]))
        return response, context

    def update_system(self, new_system_prompt):
        self.system = {"role": "system", "content": new_system_prompt}
        return new_system_prompt

def reset_state():
    return [], []

mychatGPT = ChatGPT(my_api_key)


with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    state = gr.State([])

    with gr.Column():
            txt = gr.Textbox(show_label=False, placeholder="💬 在这里输入").style(container=False)
    with gr.Row():
        emptyBth = gr.Button("重置")
        retryBth = gr.Button("再试一次")

    system = gr.Textbox(show_label=True, placeholder="New system prompts here...", label="System Prompt").style(container=False)
    syspromptTxt = gr.Textbox(show_label=False, placeholder=initial_prompt, interactive=False).style(container=False)

    txt.submit(mychatGPT.predict, [txt, state], [chatbot, state], show_progress=True)
    txt.submit(lambda :"", None, txt)
    emptyBth.click(reset_state, outputs=[chatbot, state])
    system.submit(mychatGPT.update_system, system, syspromptTxt)
    system.submit(lambda :"", None, system)
    retryBth.click(mychatGPT.retry, [state], [chatbot, state], show_progress=True)

demo.launch()
