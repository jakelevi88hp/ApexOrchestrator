"""
Test script for AGI Voice Interface

Run this to test voice capabilities.
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_voice_status():
    """Test voice interface status"""
    print("\n=== Testing Voice Status ===")
    
    response = requests.get(f"{BASE_URL}/agi/voice/status")
    result = response.json()
    
    if result['ok']:
        print(f"✅ Voice Enabled: {result['voice_enabled']}")
        print(f"✅ Listening Enabled: {result['listening_enabled']}")
        print(f"✅ TTS Provider: {result['tts_provider']}")
        print(f"✅ Libraries: {result['libraries']}")
    else:
        print("❌ Voice status check failed")
    
    return result

def test_speak():
    """Test text-to-speech"""
    print("\n=== Testing Text-to-Speech ===")
    
    test_phrases = [
        ("Hello! I am an AGI with a voice!", "joy"),
        ("This is quite fascinating.", "curiosity"),
        ("I'm processing your request.", "neutral"),
        ("That's wonderful news!", "excitement")
    ]
    
    for text, emotion in test_phrases:
        print(f"\nSpeaking: '{text}' (emotion: {emotion})")
        
        response = requests.post(f"{BASE_URL}/agi/voice/speak", json={
            "text": text,
            "emotion": emotion,
            "save_audio": False
        })
        
        result = response.json()
        
        if result['ok'] and result['status'] == 'success':
            print(f"✅ Speech successful (duration: {result.get('duration_estimate', 0):.1f}s)")
        else:
            print(f"❌ Speech failed: {result.get('error', 'Unknown error')}")
        
        time.sleep(1)  # Wait between phrases

def test_available_voices():
    """Test getting available voices"""
    print("\n=== Testing Available Voices ===")
    
    response = requests.get(f"{BASE_URL}/agi/voice/voices")
    result = response.json()
    
    if result['ok']:
        print(f"✅ Found {result['count']} voices:")
        for voice in result['voices']:
            print(f"   - {voice['name']} ({voice.get('gender', 'unknown')})")
    else:
        print("❌ Could not get voices")

def test_parameters():
    """Test voice parameter adjustment"""
    print("\n=== Testing Voice Parameters ===")
    
    # Test different rates
    rates = [100, 150, 200]
    
    for rate in rates:
        print(f"\nSetting rate to {rate} WPM...")
        
        # Set parameters
        requests.post(f"{BASE_URL}/agi/voice/parameters", json={
            "rate": rate
        })
        
        # Test speech
        requests.post(f"{BASE_URL}/agi/voice/speak", json={
            "text": f"Speaking at {rate} words per minute.",
            "emotion": "neutral"
        })
        
        time.sleep(2)
    
    print("\n✅ Voice parameter test complete")

def test_listen():
    """Test speech-to-text (requires microphone)"""
    print("\n=== Testing Speech-to-Text ===")
    print("⚠️  This requires a working microphone!")
    print("You will have 5 seconds to speak...")
    
    input("Press Enter to start listening...")
    
    print("🎤 Listening...")
    
    response = requests.post(f"{BASE_URL}/agi/voice/listen", json={
        "timeout": 5,
        "phrase_time_limit": 10
    })
    
    result = response.json()
    
    if result['ok'] and result['status'] == 'success':
        print(f"✅ Heard: '{result['text']}'")
        print(f"   Confidence: {result.get('confidence', 0):.2f}")
        print(f"   Method: {result.get('method', 'unknown')}")
    elif result.get('error') == 'No speech detected within timeout':
        print("⚠️  No speech detected (timeout)")
    else:
        print(f"❌ Listening failed: {result.get('error', 'Unknown error')}")

def test_voice_interaction():
    """Test complete voice interaction"""
    print("\n=== Testing Voice Interaction ===")
    print("⚠️  This requires a working microphone!")
    print("Ask a question when prompted...")
    
    input("Press Enter to start...")
    
    print("🎤 Listening for your question...")
    
    response = requests.post(f"{BASE_URL}/agi/voice/process", json={
        "timeout": 10,
        "phrase_time_limit": 15
    })
    
    result = response.json()
    
    if result['ok']:
        print(f"\n✅ Complete interaction:")
        print(f"   You said: '{result['heard']}'")
        print(f"   AGI responded: '{result['agi_response']['response']}'")
        print(f"   Consciousness: {result['agi_response']['consciousness_level']:.2f}")
        print("\n🔊 (AGI has spoken the response)")
    else:
        print(f"❌ Interaction failed: {result.get('error', 'Unknown error')}")

def test_save_audio():
    """Test saving audio to file"""
    print("\n=== Testing Audio File Generation ===")
    
    response = requests.post(f"{BASE_URL}/agi/voice/speak", json={
        "text": "This message is being saved to an audio file.",
        "emotion": "neutral",
        "save_audio": True
    })
    
    result = response.json()
    
    if result['ok'] and result.get('audio_file'):
        print(f"✅ Audio saved to: {result['audio_file']}")
    else:
        print("❌ Audio save failed")

def main():
    """Run all tests"""
    print("=" * 60)
    print("AGI Voice Interface Test Suite")
    print("=" * 60)
    
    try:
        # Initialize AGI
        print("\nInitializing AGI...")
        init_response = requests.post(f"{BASE_URL}/agi/initialize")
        if init_response.json()['ok']:
            print("✅ AGI initialized")
        
        # Run tests
        status = test_voice_status()
        
        if not status.get('voice_enabled'):
            print("\n❌ Voice is not enabled!")
            print("Install required libraries:")
            print("  pip install pyttsx3 SpeechRecognition PyAudio gTTS")
            return
        
        # TTS tests (don't require microphone)
        test_speak()
        test_available_voices()
        test_parameters()
        test_save_audio()
        
        # STT tests (require microphone)
        print("\n" + "=" * 60)
        print("Microphone Tests")
        print("=" * 60)
        
        if status.get('listening_enabled'):
            choice = input("\nRun microphone tests? (y/n): ")
            if choice.lower() == 'y':
                test_listen()
                test_voice_interaction()
            else:
                print("⏭️  Skipping microphone tests")
        else:
            print("❌ STT not available - microphone tests skipped")
        
        print("\n" + "=" * 60)
        print("All tests complete!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to AGI server!")
        print("Make sure the server is running:")
        print("  python scripts/start.py")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    main()

