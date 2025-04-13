# Voice Order Server

This is the Python server component of the voice-based ordering system. It uses gRPC for communication and Gemini for processing voice input.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Generate gRPC code:
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. order_service.proto
```

4. Create a `.env` file with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

## Running the Server

```bash
python server.py
```

The server will start on port 50051.

## Features

- gRPC server implementation
- Gemini integration for voice processing
- Predefined menu with Vietnamese dishes
- Error handling and response formatting

## Menu Items

The server has a predefined menu with the following items:
- Pho Bo (50,000 VND)
- Bun Bo Hue (45,000 VND)
- Com Tam (40,000 VND)
- Banh Mi (25,000 VND)
- Goi Cuon (30,000 VND) 