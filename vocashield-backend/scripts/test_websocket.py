import asyncio
import websockets
import json
import argparse
import sys
import wave

async def test_stream(audio_path):
    uri = "ws://127.0.0.1:8006/ws/call/TEST_CALL_001"
    
    # Read wave
    wf = wave.open(audio_path, 'rb')
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        print("Warning: Client should send 16kHz Mono 16-bit PCM.")
    
    raw_audio = wf.readframes(wf.getnframes())
    wf.close()
    
    # Chunk sizes (approx 1 second chunks = 16000 * 2 bytes = 32000 bytes)
    chunk_size = 32000
    
    async with websockets.connect(uri) as ws:
        # Send Start
        await ws.send(json.dumps({"type": "start"}))
        
        # Async reader to print server messages independent of sending
        async def receive_messages():
            try:
                 while True:
                     msg = await ws.recv()
                     data = json.loads(msg)
                     # Pretty print
                     print("\n[SERVER MSG]", data.get("type"))
                     if data.get("type") == "session_summary":
                         print(json.dumps(data, indent=2))
                     elif data.get("type") == "error":
                         print(json.dumps(data, indent=2))
                         break
                     else:
                         print("...") # to avoid flooding terminal
            except websockets.exceptions.ConnectionClosed:
                 print("\n[CLIENT] Connection closed.")
                 
        recv_task = asyncio.create_task(receive_messages())
        
        # Send chunks
        for i in range(0, len(raw_audio), chunk_size):
            chunk = raw_audio[i:i+chunk_size]
            await ws.send(chunk)
            print(f"[CLIENT] Sent {len(chunk)} bytes...")
            await asyncio.sleep(1.0) # simulate real-time
            
        # Send stop
        await ws.send(json.dumps({"type": "stop"}))
        # Wait for summary
        await asyncio.sleep(1.0) # small buffer to allow summary print
        
        recv_task.cancel()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_websocket.py <path_to_16k_wav>")
        sys.exit(1)
        
    asyncio.run(test_stream(sys.argv[1]))
