import asyncio
import websockets
import json
import time

async def simulate_android():
    uri = "ws://127.0.0.1:8000/ws/call/ANDROID_TEST_SESSION"
    try:
        async with websockets.connect(uri) as ws:
            # 1. Send START
            start_payload = {
                "type": "START",
                "caller": {
                    "phone_number": "+919876543210",
                    "call_direction": "INCOMING"
                }
            }
            await ws.send(json.dumps(start_payload))
            print("=> Sent START metadata.")
            ctx = await ws.recv()
            print("<= Received:", ctx)
            
            # 3. Simulate audio stream blocks (silence for basic test)
            print("=> Sending PCM chunks...")
            chunk = bytearray(32000) # 1 sec blank audio
            await ws.send(bytes(chunk))
            
            # 4. Wait for analysis event
            print("<= Waiting for analysis output...")
            analysis = await ws.recv()
            print(f"<= Received Event: {json.loads(analysis)['type']}")
            
            # 5. Send verification status update
            verify_payload = {
                "type": "VERIFICATION",
                "status": "FAILED"
            }
            await ws.send(json.dumps(verify_payload))
            print("=> Sent Verification: FAILED")
            
            # 7. Stop Session
            stop_payload = {"type": "STOP"}
            await ws.send(json.dumps(stop_payload))
            
            # Pull until summary
            while True:
                msg = await ws.recv()
                msg_json = json.loads(msg)
                print(f"<= Received: {msg_json['type']}")
                if msg_json["type"] == "session_summary":
                    break
                    
    except websockets.exceptions.ConnectionClosed:
         print("Connection securely closed")
    except Exception as e:
         print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(simulate_android())
