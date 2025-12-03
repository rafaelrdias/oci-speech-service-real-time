import asyncio
import pyaudio
from collections import deque
import logging

from oci import config as oci_config
from oci_ai_speech_realtime import (
    RealtimeSpeechClient, 
    RealtimeSpeechClientListener
)
from oci.ai_speech.models import (
    RealtimeParameters,
)

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fila FIFO para enviar áudio
queue = asyncio.Queue()

# Parâmetros de áudio
SAMPLE_RATE = 16000
FORMAT = pyaudio.paInt16
CHANNELS = 1
BUFFER_DURATION_MS = 96
FRAMES_PER_BUFFER = int(SAMPLE_RATE * BUFFER_DURATION_MS / 1000)


def audio_callback(in_data, frame_count, time_info, status):
    # Chamado pelo PyAudio quando há novos dados
    queue.put_nowait(in_data)
    return (None, pyaudio.paContinue)


class MyListener(RealtimeSpeechClientListener):
    def on_result(self, result):
        try:
            t = result["transcriptions"][0]
            if t["isFinal"]:
                logger.info(f"[FINAL] {t['transcription']}")
            else:
                logger.info(f"[PARCIAL] {t['transcription']}")
        except Exception as e:
            logger.error(f"Erro ao processar resultado: {e} - payload: {result}")

    def on_ack_message(self, ackmessage):
        logger.debug(f"ACK: {ackmessage}")
        return super().on_ack_message(ackmessage)

    def on_connect(self):
        logger.info("Conectado ao Realtime Speech")
        return super().on_connect()

    def on_connect_message(self, connectmessage):
        logger.info(f"Connect message: {connectmessage}")
        return super().on_connect_message(connectmessage)

    def on_network_event(self, ackmessage):
        logger.debug(f"Network event: {ackmessage}")
        return super().on_network_event(ackmessage)

    def on_error(self):
        logger.error("Erro no cliente Realtime Speech")
        return super().on_error()

    def on_close(self, error_code, error_message):
        logger.error(f"Conexão fechada: {error_code} - {error_message}")
        return super().on_close(error_code, error_message)


async def send_audio(client: RealtimeSpeechClient):
    """Loop assíncrono que pega dados da queue e envia via WebSocket."""
    try:
        while True:
            data = await queue.get()
            await client.send_data(data)
    except asyncio.CancelledError:
        logger.info("Loop de envio de áudio cancelado")
    except Exception as e:
        logger.error(f"Erro ao enviar áudio: {e}")


async def main():
    # Carrega config padrão (~/.oci/config, profile DEFAULT)
    config = oci_config.from_file()
    region = config["region"]

    # ATENÇÃO: use aqui o OCID **do compartment**
    COMPARTMENT_ID = "ocid1.compartment.oc1.."  # <-- ajuste aqui

    # Monta a URL do Realtime Speech a partir da região
    realtime_speech_url = f"wss://realtime.aiservice.{region}.oci.oraclecloud.com"

    # Define os parâmetros de transcrição
    realtime_speech_parameters = RealtimeParameters(

        language_code="pt",                 # Whisper: idioma "pt"
        model_type="WHISPER",               # modelo Whisper
        encoding="audio/raw;rate=16000",
        punctuation=RealtimeParameters.PUNCTUATION_AUTO
        )

    # Inicializa PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER,
        stream_callback=audio_callback,
    )
    stream.start_stream()

    # Cria o cliente RealtimeSpeech
    client = RealtimeSpeechClient(
        realtime_speech_parameters=realtime_speech_parameters,
        config=config,
        listener=MyListener(),
        service_endpoint=realtime_speech_url,
        signer=None,            
        compartment_id=COMPARTMENT_ID,
    )

    # Cria tarefa para enviar áudio
    send_task = asyncio.create_task(send_audio(client))

    try:
        # Estabelece a conexão WebSocket (bloqueia até encerrar)
        await client.connect()
    finally:
        # Limpa recursos ao sair
        send_task.cancel()
        if stream.is_active():
            stream.stop_stream()
        stream.close()
        p.terminate()
        logger.info("Encerrado")


if __name__ == "__main__":
    asyncio.run(main())