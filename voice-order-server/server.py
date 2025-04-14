import io
import logging
import os
import speech_recognition as sr
from concurrent import futures
import grpc
import voice_service_pb2
import voice_service_pb2_grpc
import google.generativeai as genai
import wave
from datetime import datetime
import tempfile
import subprocess
import json

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
            # Create a temporary file to store the input audio
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as input_file:
                input_file.write(audio_data)
                input_file.flush()
                input_path = input_file.name
                logger.info("Saved input audio to: %s", input_path)

            # Create a temporary file for the output WAV
            output_path = input_path.replace('.webm', '.wav')
            logger.info("Output WAV will be saved to: %s", output_path)

            # Convert using ffmpeg
            cmd = [
                'ffmpeg', '-i', input_path,
                '-acodec', 'pcm_s16le',  # 16-bit PCM
                '-ar', '16000',          # 16kHz sample rate
                '-ac', '1',              # Mono
                '-y',                    # Overwrite output file
                output_path
            ]
            logger.info("Running ffmpeg command: %s", ' '.join(cmd))
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("FFmpeg conversion failed: %s", result.stderr)
                raise Exception("Failed to convert audio to WAV format")

            # Read the converted WAV file
            with open(output_path, 'rb') as wav_file:
                wav_data = wav_file.read()
                logger.info("Successfully converted to WAV format, length: %d bytes", len(wav_data))

            # Clean up temporary files
            os.unlink(input_path)
            os.unlink(output_path)
            
            return wav_data
        except Exception as e:
            logger.error("Error converting audio: %s", str(e), exc_info=True)
            raise

    def audio_to_text(self, audio_data):
        try:
            logger.info("Starting speech recognition")
            logger.info("Audio data type: %s", type(audio_data))
            logger.info("Audio data length: %d bytes", len(audio_data))
            
            # Save audio data for debugging
            with open("debug_audio.wav", "wb") as f:
                f.write(audio_data)
            logger.info("Saved audio data to debug_audio.wav for inspection")
            
            audio_file = io.BytesIO(audio_data)
            with sr.AudioFile(audio_file) as source:
                # Adjust for ambient noise
                logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Record the audio
                logger.info("Recording audio...")
                audio = self.recognizer.record(source)
                logger.info("Audio recorded successfully")
                
                # Try to recognize the speech
                logger.info("Recognizing speech...")
                try:
                    # Try with Vietnamese first
                    text = self.recognizer.recognize_google(audio, language="vi-VN")
                    logger.info("Speech recognition completed with Vietnamese: '%s'", text)
                    return text
                except sr.UnknownValueError:
                    logger.warning("Google Speech Recognition could not understand audio with Vietnamese")
                    try:
                        # Try with English as fallback
                        text = self.recognizer.recognize_google(audio, language="en-US")
                        logger.info("Speech recognition completed with English: '%s'", text)
                        return text
                    except sr.UnknownValueError:
                        logger.warning("Google Speech Recognition could not understand audio with English")
                        return "Không thể nhận dạng giọng nói"
                except sr.RequestError as e:
                    logger.error("Could not request results from Google Speech Recognition service: %s", str(e))
                    return "Lỗi kết nối đến dịch vụ nhận dạng giọng nói"
        except Exception as e:
            logger.error("Error in speech recognition: %s", str(e), exc_info=True)
            raise

    def process_order(self, text):
        try:
            logger.info("Processing order text with Gemini: '%s'", text)
            
            # Use Gemini to process the text
            prompt = f"""
            Phân tích đơn hàng sau và trả về danh sách sản phẩm theo format JSON:
            Đơn hàng: {text}
            
            Menu sản phẩm: {self.menu}
            
            Format trả về:
            {{
                "products": [
                    {{
                        "name": "tên sản phẩm",
                        "sap_code": "mã SAP",
                        "quantity": số lượng
                    }}
                ],
                "products_error": [
                    {{
                        "name": "tên sản phẩm không tìm thấy",
                        "quantity": số lượng
                    }}
                ]
            }}
            """
            
            logger.info("Sending prompt to Gemini: %s", prompt)
            response = model.generate_content(prompt)
            logger.info("Received response from Gemini: %s", response.text)
            
            try:
                # Parse Gemini response
                result = json.loads(response.text)
                products = result.get("products", [])
                products_error = result.get("products_error", [])
                
                logger.info("Order processing completed - Products: %s, Errors: %s", products, products_error)
                return products, products_error
            except json.JSONDecodeError:
                logger.error("Failed to parse Gemini response as JSON: %s", response.text)
                # Fallback to original processing if Gemini fails
                return self._process_order_fallback(text)
                
        except Exception as e:
            logger.error("Error processing order with Gemini: %s", str(e), exc_info=True)
            # Fallback to original processing if Gemini fails
            return self._process_order_fallback(text)

    def _process_order_fallback(self, text):
        """Fallback method for processing orders when Gemini fails"""
        try:
            logger.info("Using fallback method to process order text: '%s'", text)
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
            
            logger.info("Fallback order processing completed - Products: %s, Errors: %s", products, products_error)
            return products, products_error
        except Exception as e:
            logger.error("Error in fallback order processing: %s", str(e), exc_info=True)
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