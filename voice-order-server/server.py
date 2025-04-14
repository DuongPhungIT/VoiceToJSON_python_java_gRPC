import io
import logging
import os
import speech_recognition as sr
from concurrent import futures
import grpc
import voice_service_pb2
import voice_service_pb2_grpc
import google.generativeai as genai
from datetime import datetime
import tempfile
import subprocess
import json
from product_menu import get_menu 

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
GEMINI_API_KEY="AIzaSyC7aoIVhPcI8lJHEIfku-QKJPG-1BAOZBc"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

class VoiceServiceServicer(voice_service_pb2_grpc.VoiceServiceServicer):
    def __init__(self):
        super().__init__()  # Call parent class constructor
        self.recognizer = sr.Recognizer()
        self.menu = get_menu()  # Call get_menu() function to get menu items

    def ProcessVoice(self, request, context):
        try:
            # Log client connection
            peer = context.peer()
            logger.info("Received connection from client: %s", peer)
            
            logger.info("Audio data length: %d bytes", len(request.audio_data))
            print("Audio data======:", request.audio_data)
            
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
            logger.info("Processing order text: '%s'", text)
            
            # Use Gemini to process the text
            prompt = f"""
            Bạn là một hệ thống xử lý đơn hàng bánh bao. Nhiệm vụ của bạn là phân tích đơn hàng và tìm sản phẩm chính xác trong menu.
            Bạn phải trả về danh sách sản phẩm theo format JSON.
            Lưu ý quan trọng:
            1. Chỉ chấp nhận tên sản phẩm CHÍNH XÁC có trong menu (100% khớp)
            2. Không chấp nhận tên gần giống, tên khác, thương hiệu khác, trọng lượng khác
            3. Chuyển đổi số lượng từ chữ sang số:
               - "một" -> 1, "hai" -> 2, ..., "chín" -> 9
               - "mười" -> 10, "hai mươi" -> 20, ..., "chín mươi" -> 90
               - "một trăm" -> 100, ..., "chín trăm" -> 900
               - "một nghìn" -> 1000, ..., "chín nghìn" -> 9000
               ...
            4. Ưu tiên số lượng:
               - Lấy số lượng gần nhất với từ "cái"
               - Số đầu câu là số thứ tự, không phải số lượng
               - Nếu không xác định được số lượng, mặc định là 1
               - Số lượng phải là số nguyên dương
            5. Nếu sản phẩm không tồn tại trong menu, đưa vào productsError
            
            Đơn hàng: {text}
            
            Menu sản phẩm: {self.menu}
            
            Format trả về:
            {{
                "products": [
                    {{
                        "name": "Tên sản phẩm từ menu",
                        "quantity": số_lượng,
                        "sap_code": mã_sản_phẩm
                    }}
                ],
                "productsError": [
                    {{
                        "name": "Tên sản phẩm không tìm thấy",
                        "quantity": số_lượng
                    }}
                ]
            }}
            
            Ví dụ:
            - "Tôi muốn 2 cái bánh bao thọ phát thịt heo 1 cút 480g" -> {{"products": [{{"name": "Bánh bao Thọ Phát Thịt Heo 1 Cút 480g (120gx4)", "quantity": 2, "sap_code": "5000154"}}], "productsError": []}}
            - "Cho tôi một cái bánh bao mỹ hương bí đỏ sữa tươi 300g và 3 cái bánh bao thọ phát đậu xanh 280g" -> {{"products": [{{"name": "Bánh bao Mỹ Hương Bí Đỏ Sữa Tươi 300g(25gx12)", "quantity": 1, "sap_code": "5000072"}}, {{"name": "Bánh Bao Thọ Phát Đậu Xanh 280g (70gx4)", "quantity": 3, "sap_code": "5000082"}}], "productsError": []}}
            - "Tôi muốn 2 cái bánh bao thọ phát thập cẩm 2 cút 600g và 1 cái bánh bao thọ phát gà nướng phô mai 400g" -> {{"products": [{{"name": "Bánh bao Thọ Phát Thập Cẩm 2 Cút 600g (150gx4)", "quantity": 2, "sap_code": "5000190"}}, {{"name": "Bánh Bao Thọ Phát Gà Nướng Phô Mai 400g (100gx4)", "quantity": 1, "sap_code": "5000282"}}], "productsError": []}}
            - "Cho tôi 1 cái bánh bao không có trong menu" -> {{"products": [], "productsError": [{{"name": "bánh bao không có trong menu", "quantity": 1}}]}}
            
            Ví dụ với từ khóa:
            - "Tôi muốn 2 cái bánh bao heo 1 cút" -> {{"products": [{{"name": "Bánh bao Thọ Phát Thịt Heo 1 Cút 480g (120gx4)", "quantity": 2, "sap_code": "5000154"}}], "productsError": []}}
            - "Cho tôi một cái bánh bao bí đỏ và 3 cái bánh bao đậu xanh" -> {{"products": [{{"name": "Bánh bao Mỹ Hương Bí Đỏ Sữa Tươi 300g(25gx12)", "quantity": 1, "sap_code": "5000072"}}, {{"name": "Bánh Bao Thọ Phát Đậu Xanh 280g (70gx4)", "quantity": 3, "sap_code": "5000082"}}], "productsError": []}}
            - "Tôi muốn 2 cái bánh bao thập cẩm và 1 cái bánh bao gà" -> {{"products": [{{"name": "Bánh bao Thọ Phát Thập Cẩm 2 Cút 600g (150gx4)", "quantity": 2, "sap_code": "5000190"}}, {{"name": "Bánh Bao Thọ Phát Gà Nướng Phô Mai 400g (100gx4)", "quantity": 1, "sap_code": "5000282"}}], "productsError": []}}
            - "Cho tôi 1 cái bánh bao không có trong menu" -> {{"products": [], "productsError": [{{"name": "bánh bao không có trong menu", "quantity": 1}}]}}
            """
            
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