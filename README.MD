
# YouTube Video Downloader, Converter, and Transcriber

Este repositório contém um script Python que automatiza o processo de download, conversão de vídeo para áudio e transcrição de vídeos do YouTube. Utilizando as bibliotecas `pytube`, `ffmpeg` e Whisper, este script é ideal para educadores, pesquisadores e criadores de conteúdo que necessitam de transcrições precisas de vídeos.

## Funcionalidades

- **Download de Vídeos do YouTube**: Suporta vídeos individuais e playlists.
- **Conversão de Vídeo para Áudio**: Converte vídeos baixados em arquivos de áudio WAV.
- **Transcrição de Áudio**: Utiliza o Whisper para transcrever os áudios em texto.

## Pré-requisitos

Antes de executar o script, certifique-se de ter as seguintes ferramentas instaladas:

- Python 3.x
- `pytube`: Instale com `pip install pytube`
- `ffmpeg`: Certifique-se de que o `ffmpeg` esteja instalado e configurado no PATH do sistema
- Whisper: Configure o Whisper no diretório especificado no script

## Instalação

1. Clone este repositório:
    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2. Instale as dependências Python:
    ```bash
    pip install -r requirements.txt
    ```

3. Configure o `ffmpeg` e o Whisper conforme necessário.

## Uso

Edite o script `main.py` e defina a URL do YouTube (pode ser uma playlist ou vídeo único):

```python
youtube_url = 'https://youtu.be/w13aeOGO3ZI?si=Ql8fUTo2OEEslJ39'
```

Execute o script:

```bash
python main.py
```

## Estrutura do Código

```python
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

# Define a pasta para armazenar os vídeos
data_folder = 'videos'
diretorio_destino = os.path.join(os.getcwd(), data_folder)

if not os.path.exists(diretorio_destino):
    os.makedirs(diretorio_destino)

# Configurações do Whisper
diretorio_whisper = 'C:/WHISPER'
modelo = 'ggml-small.bin'
idioma = 'portuguese'

# Processa cada URL de vídeo
for url in urls:
    try:
        yt = YouTube(url)
        video = yt.streams.get_highest_resolution()
        arquivo_uuid = str(uuid.uuid4())
        video_path = os.path.join(diretorio_destino, f"{arquivo_uuid}.mp4")
        caminho_audio = os.path.splitext(video_path)[0] + '.wav'

        # Baixa o vídeo
        if not os.path.exists(video_path):
            video.download(filename=video_path)
            print(f"Download concluído: {yt.title} (Arquivo: {arquivo_uuid}.mp4)")
        else:
            print(f"Vídeo já baixado: {yt.title} (Arquivo: {arquivo_uuid}.mp4)")

        # Converte vídeo para áudio
        if not os.path.exists(caminho_audio):
            comando_conversao = ["ffmpeg", "-i", video_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", caminho_audio]
            subprocess.run(comando_conversao)
            print(f"Conversão concluída para: {yt.title} (Arquivo: {arquivo_uuid}.wav)")
        else:
            print(f"Áudio WAV já existente para: {yt.title} (Arquivo: {arquivo_uuid}.wav)")

        # Transcreve o áudio
        comando_transcricao = [f"{diretorio_whisper}/main", "-f", caminho_audio, "-l", idioma, "-m", f"{diretorio_whisper}/{modelo}", "--output-txt", "--output-srt", "-pp", "--output-file", os.path.splitext(video_path)[0]]
        subprocess.run(comando_transcricao)
        print(f"Transcrição concluída para: {yt.title} (Arquivo: {arquivo_uuid})")

    except Exception as e:
        print(f"Erro ao processar o vídeo {url}: {e}")

print("Processo de download, conversão e transcrição de todos os vídeos concluído.")
```

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests com melhorias ou correções.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

Espero que este script seja útil para seus projetos. Se você tiver alguma dúvida ou sugestão, por favor, entre em contato.

![Ilustração Técnica do Fluxo de Trabalho](sandbox:/mnt/data/A_technical_illustration_showing_a_workflow_of_dow.png)
