import customtkinter as ctk
from tkinter import filedialog
import PyPDF2
import docx
import base64
from openai import OpenAI
import os

client = OpenAI()
MODEL = "gpt-4o-mini"

class TranscritorApp:
    def __init__(self):
        self.conteudo_transcrito = ""
        self.is_image = False
        self.nome_arquivo = ""

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.app = ctk.CTk()
        self.app.geometry("700x600")
        self.app.title("Transcritor com GPT")

        self.criar_interface()

    def criar_interface(self):
        self.label_arquivo = ctk.CTkLabel(self.app, text="Nenhum arquivo selecionado")
        self.label_arquivo.pack(pady=10)

        frame = ctk.CTkFrame(master=self.app)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        btn_arquivo = ctk.CTkButton(master=frame, text="Selecionar Arquivo", command=self.selecionar_arquivo)
        btn_arquivo.pack(pady=5)

        btn_remover = ctk.CTkButton(master=frame, text="Remover Arquivo", command=self.remover_arquivo)
        btn_remover.pack(pady=5)

        self.prompt_entry = ctk.CTkEntry(master=frame, placeholder_text="Digite seu prompt aqui...")
        self.prompt_entry.pack(pady=10, fill="x")

        btn_enviar = ctk.CTkButton(master=frame, text="Enviar para o GPT", command=self.enviar_prompt)
        btn_enviar.pack(pady=5)

        self.resposta_area = ctk.CTkTextbox(master=frame, height=300)
        self.resposta_area.pack(pady=10, fill="both", expand=True)

    def verificar_tipo_arquivo(self, arquivo: str) -> str:
        if arquivo.endswith(".pdf"):
            return "pdf"
        elif arquivo.endswith(".docx"):
            return "docx"
        elif arquivo.endswith((".jpg", ".jpeg", ".png")):
            return "image"
        else:
            return "unknown"

    def transcrever(self, arquivo):
        if arquivo.endswith(".pdf"):
            with open(arquivo, 'rb') as file:
                leitor = PyPDF2.PdfReader(file)
                return "\n".join(p.extract_text() for p in leitor.pages)
        elif arquivo.endswith(".docx"):
            doc = docx.Document(arquivo)
            return "\n".join(paragrafo.text for paragrafo in doc.paragraphs)
        elif arquivo.endswith((".jpg", ".jpeg", ".png")):
            with open(arquivo, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

    def selecionar_arquivo(self):
        arquivo = filedialog.askopenfilename(
            filetypes=[("PDF", "*.pdf"), ("DOCX", "*.docx"), ("Images", "*.jpg;*.jpeg;*.png")],
            title="Selecione um arquivo"
        )
        if not arquivo:
            return

        tipo = self.verificar_tipo_arquivo(arquivo)
        self.is_image = (tipo == "image")
        self.conteudo_transcrito = self.transcrever(arquivo)
        self.nome_arquivo = os.path.basename(arquivo)
        self.label_arquivo.configure(text=f"Arquivo selecionado: {self.nome_arquivo}")

    def remover_arquivo(self):
        self.conteudo_transcrito = ""
        self.is_image = False
        self.nome_arquivo = ""
        self.label_arquivo.configure(text="Nenhum arquivo selecionado")
        self.resposta_area.delete("1.0", "end")

    def enviar_prompt(self):

        prompt = self.prompt_entry.get()
        self.resposta_area.delete("1.0", "end")
        self.resposta_area.insert("1.0", "Aguarde... Processando a resposta.")

        resposta = self.enviar_para_gpt(prompt, self.conteudo_transcrito, self.is_image)

        self.resposta_area.delete("1.0", "end")
        self.resposta_area.insert("1.0", resposta)

    def enviar_para_gpt(self, prompt, conteudo, is_image=False):
        try:
            if is_image:
                completion = client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": "Você é professor universitário"},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{conteudo}"}
                                }
                            ]
                        }
                    ]
                )
            else:
                completion = client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": "Você é professor universitário"},
                        {"role": "user", "content": f"{prompt}\n\n{conteudo}"}
                    ]
                )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Erro ao chamar a API: {e}"

    def run(self):
        self.app.mainloop()


if __name__ == "__main__":
    app = TranscritorApp()
    app.run()