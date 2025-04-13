import grpc
import order_service_pb2
import order_service_pb2_grpc
import google.generativeai as genai
import os
import tempfile
import subprocess
import speech_recognition as sr
from concurrent import futures

# Set Google API Key
GOOGLE_API_KEY = "AIzaSyC7aoIVhPcI8lJHEIfku-QKJPG-1BAOZBc"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Initialize Gemini API
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Menu items and their SAP codes
MENU = {
    "Coca Cola": "CC001",
    "Pepsi": "PS001",
    "Sprite": "SP001",
    "Fanta": "FT001",
    "7Up": "7U001",
    "Mountain Dew": "MD001",
    "Mirinda": "MR001",
    "Sting": "ST001",
    "Red Bull": "RB001",
    "Monster": "MN001"
}

class OrderServiceServicer(order_service_pb2_grpc.OrderServiceServicer):
    def ProcessAudioOrder(self, request, context):
        try:
            # Save audio data to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_audio:
                temp_audio.write(request.audio_data)
                temp_audio_path = temp_audio.name

            try:
                # Convert webm to wav using ffmpeg
                temp_wav_path = temp_audio_path + '.wav'
                subprocess.run([
                    'ffmpeg', '-i', temp_audio_path,
                    '-acodec', 'pcm_s16le',
                    '-ar', '16000',
                    '-ac', '1',
                    temp_wav_path
                ], check=True)

                # Initialize recognizer
                recognizer = sr.Recognizer()

                # Read the audio file
                with sr.AudioFile(temp_wav_path) as source:
                    # Adjust for ambient noise
                    recognizer.adjust_for_ambient_noise(source)
                    # Record the audio
                    audio = recognizer.record(source)

                try:
                    # Recognize speech using Google Speech Recognition
                    transcript = recognizer.recognize_google(audio, language="vi-VN")
                    print(f"Recognized text: {transcript}")
                except sr.UnknownValueError:
                    return order_service_pb2.AudioOrderResponse(
                        status="ERROR",
                        message="Không thể nhận dạng giọng nói"
                    )
                except sr.RequestError as e:
                    return order_service_pb2.AudioOrderResponse(
                        status="ERROR",
                        message=f"Lỗi kết nối đến dịch vụ nhận dạng giọng nói: {str(e)}"
                    )

                # Process text with Gemini
                try:
                    response = model.generate_content([
                        "Bạn là một hệ thống xử lý đơn hàng. Hãy trích xuất thông tin đơn hàng từ văn bản sau. " +
                        "Định dạng phản hồi dưới dạng danh sách các mặt hàng và số lượng, mỗi dòng một mục. " +
                        "Mỗi dòng phải có định dạng: 'tên mặt hàng x số lượng'",
                        transcript
                    ])
                    print(f"Gemini response: {response.text}")
                    processed_order = response.text
                except Exception as e:
                    return order_service_pb2.AudioOrderResponse(
                        status="ERROR",
                        message=f"Lỗi khi xử lý với Gemini: {str(e)}"
                    )

                # Parse the response
                products = []
                products_error = []
                
                for line in processed_order.split('\n'):
                    if 'x' in line:
                        parts = line.split('x')
                        item_name = parts[0].strip()
                        try:
                            quantity = int(parts[1].strip())
                            
                            # Check if item exists in menu
                            if item_name in MENU:
                                product = order_service_pb2.Product(
                                    name=item_name,
                                    sap_code=MENU[item_name],
                                    quantity=quantity
                                )
                                products.append(product)
                            else:
                                product_error = order_service_pb2.ProductError(
                                    name=item_name,
                                    quantity=quantity
                                )
                                products_error.append(product_error)
                        except ValueError:
                            continue
                
                # Create response
                return order_service_pb2.AudioOrderResponse(
                    products=products,
                    products_error=products_error,
                    status="SUCCESS",
                    message="Đã xử lý đơn hàng thành công"
                )

            finally:
                # Clean up temporary files
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
                if os.path.exists(temp_wav_path):
                    os.unlink(temp_wav_path)
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return order_service_pb2.AudioOrderResponse(
                status="ERROR",
                message=str(e)
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    order_service_pb2_grpc.add_OrderServiceServicer_to_server(
        OrderServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server đã khởi động trên cổng 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve() 