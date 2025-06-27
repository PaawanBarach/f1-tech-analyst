from fastapi import FastAPI
import gradio as gr
from agents import answer_question
from utils.plotting import line_plot

app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "alive"}

def qa_interface(query):
    ans, srcs = answer_question(query)
    return ans + "\n\nSources:\n" + "\n".join(srcs)

with gr.Blocks() as demo:
    gr.Markdown("# F1 Technical Analyst")
    inp = gr.Textbox(placeholder="Ask a technical F1 question…")
    out = gr.Textbox()
    inp.submit(qa_interface, inp, out)

@app.on_event("startup")
def startup():
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True, prevent_thread_lock=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=80)
