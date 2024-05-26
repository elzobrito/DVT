import os
import uuid
import subprocess
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from pytube import YouTube, Playlist

# Variável global para controlar o estado do processamento
stop_processing = False

# Função para salvar a pasta de destino em um arquivo de configuração
def save_config(destination_folder):
    config = {'destination_folder': destination_folder}
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file)

# Função para carregar a pasta de destino do arquivo de configuração
def load_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            return config.get('destination_folder', '')
    return ''

# Função para selecionar a pasta de destino
def select_destination_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        destination_var.set(folder_selected)
        save_config(folder_selected)

# Função para atualizar a barra de progresso
def update_progress(value):
    progress_var.set(value)
    window.update_idletasks()

# Função para atualizar a mensagem de status
def update_status(message):
    status_var.set(message)
    window.update_idletasks()

# Função para processar os vídeos em uma thread separada
def process_videos_thread():
    global stop_processing
    youtube_url = url_var.get()
    if not youtube_url:
        messagebox.showerror("Erro", "Por favor, insira uma URL válida do YouTube.")
        return

    destination_folder = destination_var.get()
    if not destination_folder:
        messagebox.showerror("Erro", "Por favor, selecione uma pasta de destino.")
        return

    try:
        if 'playlist' in youtube_url:
            playlist = Playlist(youtube_url)
            urls = playlist.video_urls
        else:
            urls = [youtube_url]

        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        diretorio_whisper = 'C:/WHISPER'
        modelo = 'ggml-small.bin'
        idioma = 'portuguese'

        total_videos = len(urls)
        for index, url in enumerate(urls, start=1):
            if stop_processing:
                update_status("Processamento interrompido pelo usuário.")
                break

            try:
                yt = YouTube(url)
                video = yt.streams.get_highest_resolution()
                arquivo_uuid = str(uuid.uuid4())
                video_path = os.path.join(destination_folder, f"{arquivo_uuid}.mp4")
                caminho_audio = os.path.splitext(video_path)[0] + '.wav'

                if not os.path.exists(video_path):
                    video.download(filename=video_path)
                    update_status(f"Download concluído: {yt.title} (Arquivo: {arquivo_uuid}.mp4)")
                else:
                    update_status(f"Vídeo já baixado: {yt.title} (Arquivo: {arquivo_uuid}.mp4)")

                if not os.path.exists(caminho_audio):
                    comando_conversao = ["ffmpeg", "-i", video_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", caminho_audio]
                    subprocess.run(comando_conversao)
                    update_status(f"Conversão concluída para: {yt.title} (Arquivo: {arquivo_uuid}.wav)")
                else:
                    update_status(f"Áudio WAV já existente para: {yt.title} (Arquivo: {arquivo_uuid}.wav)")

                comando_transcricao = [f"{diretorio_whisper}/main", "-f", caminho_audio, "-l", idioma, "-m", f"{diretorio_whisper}/{modelo}", "--output-txt", "--output-srt", "-pp", "--output-file", os.path.splitext(video_path)[0]]
                
                # Executa o comando e captura a saída em tempo real
                process = subprocess.Popen(comando_transcricao, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                
                for line in process.stdout:
                    if stop_processing:
                        process.terminate()
                        update_status("Processamento interrompido pelo usuário.")
                        return

                    if 'progress =' in line:
                        progress = int(line.split('progress =')[1].split('%')[0].strip())
                        update_progress(progress)
                    update_status(line.strip())
                
                process.wait()

                if process.returncode != 0:
                    raise subprocess.CalledProcessError(process.returncode, comando_transcricao)
                
                update_status(f"Transcrição concluída para: {yt.title} (Arquivo: {arquivo_uuid})")

                update_progress((index / total_videos) * 100)

            except Exception as e:
                update_status(f"Erro ao processar o vídeo {url}: {e}")

        messagebox.showinfo("Concluído", "Processo de download, conversão e transcrição de todos os vídeos concluído.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao processar os vídeos: {e}")
    finally:
        # Restaurar o estado inicial da interface
        start_button.config(text="Iniciar", command=start_processing)
        stop_processing = False

# Função para iniciar o processamento dos vídeos
def start_processing():
    global stop_processing
    stop_processing = False
    start_button.config(text="PARAR", command=stop_processing_function)
    threading.Thread(target=process_videos_thread).start()

# Função para parar o processamento dos vídeos
def stop_processing_function():
    global stop_processing
    stop_processing = True
    update_status("Interrompendo o processamento...")

# Configuração da GUI
window = tk.Tk()
window.title("YouTube Video Downloader and Transcriber")
window.geometry("600x400")

url_label = tk.Label(window, text="URL do YouTube:")
url_label.pack(pady=(20, 0))

url_var = tk.StringVar()
url_entry = tk.Entry(window, textvariable=url_var, width=80)
url_entry.pack(pady=5)

destination_label = tk.Label(window, text="Pasta de Destino:")
destination_label.pack(pady=(20, 0))

destination_frame = tk.Frame(window)
destination_frame.pack(pady=5)

destination_var = tk.StringVar(value=load_config())
destination_entry = tk.Entry(destination_frame, textvariable=destination_var, width=60)
destination_entry.pack(side=tk.LEFT, padx=5)

select_button = tk.Button(destination_frame, text="Selecione", command=select_destination_folder)
select_button.pack(side=tk.LEFT)

progress_label = tk.Label(window, text="Barra de Progresso:")
progress_label.pack(pady=(20, 0))

progress_var = tk.DoubleVar()
progress_bar = Progressbar(window, variable=progress_var, maximum=100)
progress_bar.pack(fill=tk.X, padx=20, pady=5)

status_var = tk.StringVar()
status_label = tk.Label(window, textvariable=status_var)
status_label.pack(pady=5)

start_button = tk.Button(window, text="Iniciar", command=start_processing)
start_button.pack(pady=(20, 20))

window.mainloop()
