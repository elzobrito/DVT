from pytube import YouTube, Playlist
import os
import subprocess
import uuid

# URL do YouTube (pode ser de uma playlist ou vídeo único)
youtube_url = 'https://youtu.be/w13aeOGO3ZI?si=Ql8fUTo2OEEslJ39'

# Verifica se a URL é de uma playlist ou de um vídeo único
if 'playlist' in youtube_url:
    playlist = Playlist(youtube_url)    
    urls = playlist.video_urls
else:
    urls = [youtube_url]

data_folder = 'videos'
diretorio_destino = os.path.join(os.getcwd(), data_folder)

if not os.path.exists(diretorio_destino):
    os.makedirs(diretorio_destino)

diretorio_whisper = 'C:/WHISPER'
modelo = 'ggml-small.bin'
idioma = 'portuguese'

for url in urls:
    try:
        yt = YouTube(url)
        video = yt.streams.get_highest_resolution()
        arquivo_uuid = str(uuid.uuid4())
        video_path = os.path.join(diretorio_destino, f"{arquivo_uuid}.mp4")
        caminho_audio = os.path.splitext(video_path)[0] + '.wav'

        if not os.path.exists(video_path):
            video.download(filename=video_path)
            print(f"Download concluído: {yt.title} (Arquivo: {arquivo_uuid}.mp4)")
        else:
            print(f"Vídeo já baixado: {yt.title} (Arquivo: {arquivo_uuid}.mp4)")

        if not os.path.exists(caminho_audio):
            comando_conversao = ["ffmpeg", "-i", video_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", caminho_audio]
            subprocess.run(comando_conversao)
            print(f"Conversão concluída para: {yt.title} (Arquivo: {arquivo_uuid}.wav)")
        else:
            print(f"Áudio WAV já existente para: {yt.title} (Arquivo: {arquivo_uuid}.wav)")

        comando_transcricao = [f"{diretorio_whisper}/main", "-f", caminho_audio, "-l", idioma, "-m", f"{diretorio_whisper}/{modelo}", "--output-txt", "--output-srt", "-pp", "--output-file", os.path.splitext(video_path)[0]]
        subprocess.run(comando_transcricao)
        print(f"Transcrição concluída para: {yt.title} (Arquivo: {arquivo_uuid})")

    except Exception as e:
        print(f"Erro ao processar o vídeo {url}: {e}")

print("Processo de download, conversão e transcrição de todos os vídeos concluído.")
