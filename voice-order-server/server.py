import base64
import io
import logging
import os
import speech_recognition as sr
from concurrent import futures
import grpc
import voice_service_pb2
import voice_service_pb2_grpc
import google.generativeai as genai
import tempfile
import subprocess
import json
import wave
from datetime import datetime

# Configure logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# Menu items with SAP codes
MENU_ITEMS = {
    "coca cola": "1001",
    "pepsi": "1002",
    "7up": "1003",
    "fanta": "1004",
    "sprite": "1005",
    "mirinda": "1006",
    "sting": "1007",
    "number one": "1008",
    "revive": "1009",
    "tiger": "1010",
    "heineken": "1011",
    "saigon": "1012",
    "333": "1013",
    "huda": "1014",
    "larue": "1015",
    "hanoi": "1016",
    "bia hơi": "1017",
    "bia tươi": "1017",
    "bia đen": "1018",
    "bia nâu": "1019",
    "bia đỏ": "1020",
    "bia vàng": "1021",
    "bia trắng": "1022",
    "bia xanh": "1023",
    "bia tím": "1024",
    "bia hồng": "1025",
    "bia cam": "1026",
    "bia lục": "1027",
    "bia lam": "1028",
    "bia chai": "1029",
    "bia lon": "1030",
    "bia thùng": "1031",
    "bia két": "1032",
    "bia bock": "1033",
    "bia pilsner": "1034",
    "bia lager": "1035",
    "bia ale": "1036",
    "bia stout": "1037",
    "bia porter": "1038",
    "bia wheat": "1039",
    "bia ipa": "1040",
    "bia apa": "1050"
}

class VoiceServiceServicer(voice_service_pb2_grpc.VoiceServiceServicer):
    def __init__(self):
        super().__init__()  # Call parent class constructor
        self.recognizer = sr.Recognizer()
        self.menu = MENU_ITEMS
        logger.info("VoiceServiceServicer initialized with menu: %s", self.menu)

    def ProcessVoice(self, request, context):
        try:
            # Log client connection
            peer = context.peer()
            logger.info("Received connection from client: %s", peer)
            
            logger.info("Audio data length: %d bytes", len(request.audio_data))
            
            # Get audio data directly
            audio_data = request.audio_data
            logger.info("Audio data length: %d bytes", len(audio_data))
            
            # Save audio data to a temporary file for debugging
            with open("temp_audio.webm", "wb") as f:
                f.write(audio_data)
            logger.info("Saved audio data to temp_audio.webm")
            
            # Convert to WAV format
            wav_data = self.convert_to_wav(audio_data)
            logger.info("Converted to WAV format, length: %d bytes", len(wav_data))
            
            # Save WAV data for debugging
            with open("temp_audio.wav", "wb") as f:
                f.write(wav_data)
            logger.info("Saved WAV data to temp_audio.wav")
            
            # Convert audio to text
            text = self.audio_to_text(wav_data)
            logger.info("Converted audio to text: '%s'", text)
            
            # Process the order
            products, products_error = self.process_order(text)
            logger.info("Processed order - Products: %s, Errors: %s", products, products_error)
            
            # Create response
            response = voice_service_pb2.VoiceResponse()
            response.status = "success"
            response.message = "Order processed successfully"
            response.transcript = text
            
            # Add products to response
            for product in products:
                p = response.products.add()
                p.name = product["name"]
                p.sap_code = product["sap_code"]
                p.quantity = product["quantity"]
            
            # Add error products to response
            for product in products_error:
                p = response.products_error.add()
                p.name = product["name"]
                p.quantity = product["quantity"]
            
            return response
            
        except Exception as e:
            logger.error("Error processing voice request: %s", str(e), exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return voice_service_pb2.VoiceResponse(
                status="error",
                message=str(e)
            )

    def convert_to_wav(self, audio_data):
        try:
            logger.info("Starting audio conversion")
            # Create a BytesIO object to hold the audio data
            audio_file = io.BytesIO(audio_data)
            
            # Create a WAV file
            wav_file = io.BytesIO()
            with wave.open(wav_file, 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(16000)  # 16kHz
                wf.writeframes(audio_data)
            
            logger.info("Audio conversion completed successfully")
            return wav_file.getvalue()
        except Exception as e:
            logger.error("Error converting audio: %s", str(e), exc_info=True)
            raise

    def audio_to_text(self, audio_data):
        try:
            logger.info("Starting speech recognition")
            audio_file = io.BytesIO(audio_data)
            with sr.AudioFile(audio_file) as source:
                # Adjust for ambient noise
                logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source)
                
                # Record the audio
                logger.info("Recording audio...")
                audio = self.recognizer.record(source)
                
                # Try to recognize the speech
                logger.info("Recognizing speech...")
                try:
                    text = self.recognizer.recognize_google(audio, language="vi-VN")
                    logger.info("Speech recognition completed: '%s'", text)
                    return text
                except sr.UnknownValueError:
                    logger.warning("Google Speech Recognition could not understand audio")
                    return "Không thể nhận dạng giọng nói"
                except sr.RequestError as e:
                    logger.error("Could not request results from Google Speech Recognition service: %s", str(e))
                    return "Lỗi kết nối đến dịch vụ nhận dạng giọng nói"
        except Exception as e:
            logger.error("Error in speech recognition: %s", str(e), exc_info=True)
            raise

    def process_order(self, text):
        try:
            logger.info("Processing order text: '%s'", text)
            products = []
            products_error = []
            
            # Convert text to lowercase for case-insensitive matching
            text = text.lower()
            
            # Split text into words
            words = text.split()
            logger.info("Split text into words: %s", words)
            
            i = 0
            while i < len(words):
                # Look for quantity
                if words[i].isdigit():
                    quantity = int(words[i])
                    logger.info("Found quantity: %d", quantity)
                    
                    # Look for product name
                    product_name = None
                    for name in self.menu.keys():
                        if " ".join(words[i+1:i+1+len(name.split())]).lower() == name:
                            product_name = name
                            logger.info("Found product name: %s", product_name)
                            break
                    
                    if product_name:
                        products.append({
                            "name": product_name,
                            "sap_code": self.menu[product_name],
                            "quantity": quantity
                        })
                        i += 1 + len(product_name.split())
                    else:
                        # If product not found, add to error list
                        products_error.append({
                            "name": " ".join(words[i+1:i+3]),
                            "quantity": quantity
                        })
                        i += 3
                else:
                    i += 1
            
            logger.info("Order processing completed - Products: %s, Errors: %s", products, products_error)
            return products, products_error
        except Exception as e:
            logger.error("Error processing order: %s", str(e), exc_info=True)
            raise

def serve():
    try:
        logger.info("Starting gRPC server...")
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        voice_service_pb2_grpc.add_VoiceServiceServicer_to_server(
            VoiceServiceServicer(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        logger.info("Server started on port 50051")
        server.wait_for_termination()
    except Exception as e:
        logger.error("Error starting server: %s", str(e), exc_info=True)

if __name__ == '__main__':
    serve() 