# Voice Order Client

This is the Java client component of the voice-based ordering system. It uses gRPC for communication with the server and Google Cloud Speech-to-Text for voice recognition.

## Prerequisites

- Java 11 or higher
- Maven
- Google Cloud credentials (for Speech-to-Text API)

## Setup

1. Set up Google Cloud credentials:
   - Create a service account in Google Cloud Console
   - Download the JSON key file
   - Set the environment variable:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
     ```

2. Build the project:
```bash
mvn clean install
```

## Running the Client

```bash
mvn exec:java -Dexec.mainClass="com.voiceorder.OrderClient"
```

The client will:
1. Record audio for 5 seconds
2. Convert the audio to text using Google Cloud Speech-to-Text
3. Send the text to the server
4. Display the order details received from the server

## Features

- gRPC client implementation
- Google Cloud Speech-to-Text integration
- Audio recording functionality
- Vietnamese language support
- Error handling

## Configuration

The client is configured to:
- Connect to localhost:50051 by default
- Use Vietnamese language for speech recognition
- Record audio at 16kHz sample rate 