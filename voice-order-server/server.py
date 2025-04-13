import grpc
from concurrent import futures
import order_service_pb2
import order_service_pb2_grpc
import google.generativeai as genai
import os
from dotenv import load_dotenv
import speech_recognition as sr
import io
import wave

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = "AIzaSyC7aoIVhPcI8lJHEIfku-QKJPG-1BAOZBc"
# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Predefined menu with SAP codes
MENU = {
    "Pho Bo": "PHO001",
    "Bun Bo Hue": "BUN001",
    "Com Tam": "COM001",
    "Banh Mi": "BAN001",
    "Goi Cuon": "GOI001"
}

class OrderServiceServicer(order_service_pb2_grpc.OrderServiceServicer):
    def ProcessAudioOrder(self, request, context):
        try:
            # Convert audio data to WAV format
            audio_data = request.audio_data
            audio_format = request.audio_format
            
            # Save audio to a temporary file
            with wave.open('temp.wav', 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(audio_data)
            
            # Convert speech to text
            recognizer = sr.Recognizer()
            with sr.AudioFile('temp.wav') as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio, language='vi-VN')
            
            # Process text using Gemini
            prompt = f"""
            Analyze this voice input for food orders: {text}
            The available menu items are: {list(MENU.keys())}
            Extract the ordered items and quantities.
            Return the response in this format:
            [item_name] x [quantity]
            Each item on a new line.
            """
            
            response = model.generate_content(prompt)
            processed_order = response.text
            
            # Parse the response and create products
            products = []
            products_error = []
            
            for line in processed_order.split('\n'):
                if 'x' in line:
                    parts = line.split('x')
                    item_name = parts[0].strip()
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
            
            # Create response
            return order_service_pb2.AudioOrderResponse(
                products=products,
                products_error=products_error,
                status="SUCCESS",
                message="Order processed successfully"
            )
            
        except Exception as e:
            return order_service_pb2.AudioOrderResponse(
                status="ERROR",
                message=str(e)
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    order_service_pb2_grpc.add_OrderServiceServicer_to_server(OrderServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve() 