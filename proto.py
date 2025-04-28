from idlelib.pyparse import trans
from tkinter import filedialog
import PyPDF2
from openai import OpenAI
import base64
import tkinter as tk
import docx

client = OpenAI()
MODEL = "gpt-4o-mini"

def selecionar_arquivo():
    root = tk.Tk()
    root.withdraw()
    arquivo = filedialog.askopenfilename(
        filetypes=[("PDF", "*.pdf"), ("DOCX", "*.docx"), ("Images", "*.jpg;*.jpeg;*.png")],
        title="Select a file"
    )
    return arquivo
def verificar_tipo_arquivo(arquivo: str) -> str:
    """
    Verifica o tipo de arquivo com base na extensão.

    Args:
        arquivo (str): Caminho do arquivo.

    Returns:
        str: Tipo de arquivo ('pdf', 'docx', 'image') ou 'unknown' se não for suportado.
    """
    if arquivo.endswith(".pdf"):
        return "pdf"
    elif arquivo.endswith(".docx"):
        return "docx"
    elif arquivo.endswith((".jpg", ".jpeg", ".png")):
        return "image"
    else:
        return "unknown"

def transcrever(arquivo):
    if arquivo.endswith(".pdf"):
        with open(arquivo, 'rb') as file:
            leitor = PyPDF2.PdfReader(file)
            texto = ''
            for pagina in leitor.pages:
                texto += pagina.extract_text() + '\n'
        return texto
    elif arquivo.endswith(".docx"):
            doc = docx.Document(arquivo)
            texto = '\n'.join([paragrafo.text for paragrafo in doc.paragraphs])
            return texto
    elif arquivo.endswith(".jpeg") or arquivo.endswith(".jpg") or arquivo.endswith(".png"):
        with open(arquivo, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

def gpt(prompt, conteudo, is_image=False):
    try:
        if is_image:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Você é professor numa classe universitária"},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{conteudo}"
                                }
                            }
                        ]
                    }
                ]
            )
        else:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Você é professor numa classe universitária"},
                    {"role": "user", "content": f"{prompt}\n\n{conteudo}"}
                ]
            )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Erro ao chamar a API: {e}")
        return None


arquivo = selecionar_arquivo()

def main():
    if not arquivo:
        conteudo = "\n"
        while True:
            prompt = input("Você: ")
            if prompt.lower() == 'quit':
                break
            resposta = gpt(prompt, conteudo, is_image=False)
            print(resposta)

    tipo_arquivo = verificar_tipo_arquivo(arquivo)

    conteudo = transcrever(arquivo)
    is_image = (tipo_arquivo == "image")

    while True:
        prompt = input("Você: ")
        if prompt.lower() == 'quit':
            break
        resposta = gpt(prompt, conteudo, is_image)
        if resposta:
            print(resposta)
        else:
            print("Erro ao processar a resposta.")

if __name__ == '__main__':
    main()

#BRAVO FERNANDO 2005 WORLD CHAMPION