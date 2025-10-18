"""
Voice Engine for Pulse System
Provides text-to-speech capabilities for alerts, notifications, and dashboard interactions
"""

import asyncio
import logging
import threading
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

try:
    import pyttsx3
    import pygame
    from pydub import AudioSegment
    from pydub.playback import play
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    pyttsx3 = None
    pygame = None
    AudioSegment = None
    play = None

# Check if we're in a headless environment
import os
HEADLESS = os.environ.get('DISPLAY') is None and os.environ.get('SSH_CONNECTION') is not None

logger = logging.getLogger(__name__)

class VoicePriority(Enum):
    """Voice message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class VoiceMessage:
    """Voice message data structure"""
    text: str
    priority: VoicePriority
    voice_id: Optional[str] = None
    rate: Optional[int] = None
    volume: Optional[float] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class PulseVoiceEngine:
    """Voice engine for Pulse system with text-to-speech capabilities"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.engine = None
        self.voices = {}
        self.message_queue = []
        self.is_speaking = False
        self.voice_thread = None
        self.stop_event = threading.Event()
        
        # Voice settings
        self.default_rate = self.config.get('default_rate', 200)
        self.default_volume = self.config.get('default_volume', 0.8)
        self.max_queue_size = self.config.get('max_queue_size', 50)
        self.voice_timeout = self.config.get('voice_timeout', 30)
        
        # Priority settings
        self.priority_settings = {
            VoicePriority.LOW: {'rate': 150, 'volume': 0.6},
            VoicePriority.NORMAL: {'rate': 200, 'volume': 0.8},
            VoicePriority.HIGH: {'rate': 250, 'volume': 0.9},
            VoicePriority.CRITICAL: {'rate': 300, 'volume': 1.0}
        }
        
        if VOICE_AVAILABLE and self.enabled and not HEADLESS:
            self._initialize_engine()
        else:
            if HEADLESS:
                logger.info("Voice engine disabled in headless environment")
            else:
                logger.warning("Voice engine not available or disabled")
    
    def _initialize_engine(self):
        """Initialize the text-to-speech engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            for i, voice in enumerate(voices):
                voice_id = f"voice_{i}"
                self.voices[voice_id] = {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': getattr(voice, 'languages', []),
                    'gender': getattr(voice, 'gender', 'unknown')
                }
            
            # Set default voice
            if voices:
                self.engine.setProperty('voice', voices[0].id)
            
            # Set default properties
            self.engine.setProperty('rate', self.default_rate)
            self.engine.setProperty('volume', self.default_volume)
            
            # Start voice thread
            self.voice_thread = threading.Thread(target=self._voice_worker, daemon=True)
            self.voice_thread.start()
            
            logger.info(f"Voice engine initialized with {len(self.voices)} voices")
            
        except Exception as e:
            logger.error(f"Failed to initialize voice engine: {e}")
            self.enabled = False
    
    def _voice_worker(self):
        """Background worker for processing voice messages"""
        while not self.stop_event.is_set():
            try:
                if self.message_queue and not self.is_speaking:
                    message = self.message_queue.pop(0)
                    self._speak_message(message)
                else:
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in voice worker: {e}")
                time.sleep(1)
    
    def _speak_message(self, message: VoiceMessage):
        """Speak a voice message"""
        if not self.engine or not self.enabled:
            return
        
        try:
            self.is_speaking = True
            
            # Set voice properties based on priority
            priority_settings = self.priority_settings.get(message.priority, {})
            rate = message.rate or priority_settings.get('rate', self.default_rate)
            volume = message.volume or priority_settings.get('volume', self.default_volume)
            
            # Set voice if specified
            if message.voice_id and message.voice_id in self.voices:
                self.engine.setProperty('voice', self.voices[message.voice_id]['id'])
            
            # Set rate and volume
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            
            # Speak the message
            logger.info(f"Speaking: {message.text[:50]}...")
            self.engine.say(message.text)
            self.engine.runAndWait()
            
        except Exception as e:
            logger.error(f"Error speaking message: {e}")
        finally:
            self.is_speaking = False
    
    def speak(self, text: str, priority: VoicePriority = VoicePriority.NORMAL, 
              voice_id: Optional[str] = None, rate: Optional[int] = None, 
              volume: Optional[float] = None) -> bool:
        """Add a message to the voice queue"""
        if not self.enabled or not self.engine:
            logger.warning("Voice engine not available")
            return False
        
        # Check queue size
        if len(self.message_queue) >= self.max_queue_size:
            logger.warning("Voice queue is full, dropping message")
            return False
        
        message = VoiceMessage(
            text=text,
            priority=priority,
            voice_id=voice_id,
            rate=rate,
            volume=volume
        )
        
        # Insert based on priority (higher priority first)
        if priority == VoicePriority.CRITICAL:
            self.message_queue.insert(0, message)
        elif priority == VoicePriority.HIGH:
            # Insert after critical messages
            insert_pos = 0
            for i, existing in enumerate(self.message_queue):
                if existing.priority != VoicePriority.CRITICAL:
                    insert_pos = i
                    break
            self.message_queue.insert(insert_pos, message)
        else:
            self.message_queue.append(message)
        
        logger.debug(f"Added voice message to queue: {text[:30]}... (priority: {priority.value})")
        return True
    
    def speak_alert(self, alert_type: str, message: str, severity: str = "normal"):
        """Speak an alert message with appropriate priority"""
        priority_map = {
            "low": VoicePriority.LOW,
            "normal": VoicePriority.NORMAL,
            "high": VoicePriority.HIGH,
            "critical": VoicePriority.CRITICAL
        }
        
        priority = priority_map.get(severity.lower(), VoicePriority.NORMAL)
        
        # Format alert message
        if alert_type == "system":
            formatted_text = f"System alert: {message}"
        elif alert_type == "performance":
            formatted_text = f"Performance alert: {message}"
        elif alert_type == "error":
            formatted_text = f"Error alert: {message}"
        else:
            formatted_text = f"{alert_type.title()} alert: {message}"
        
        return self.speak(formatted_text, priority)
    
    def speak_metrics(self, metrics: Dict[str, Any]):
        """Speak current system metrics"""
        cpu = metrics.get('cpu_percent', 0)
        memory = metrics.get('memory_percent', 0)
        health = metrics.get('health_score', 0)
        
        text = f"System status: CPU at {cpu:.1f} percent, Memory at {memory:.1f} percent, Health score {health}"
        return self.speak(text, VoicePriority.NORMAL)
    
    def speak_health_report(self, health_data: Dict[str, Any]):
        """Speak a health report"""
        overall_health = health_data.get('overall_health', 'unknown')
        health_score = health_data.get('health_score', 0)
        
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 75:
            status = "good"
        elif health_score >= 50:
            status = "fair"
        else:
            status = "poor"
        
        text = f"Health report: System is {status} with a score of {health_score}. Overall health: {overall_health}"
        return self.speak(text, VoicePriority.NORMAL)
    
    def speak_event(self, event_type: str, message: str, severity: str = "normal"):
        """Speak an event notification"""
        priority_map = {
            "low": VoicePriority.LOW,
            "normal": VoicePriority.NORMAL,
            "high": VoicePriority.HIGH,
            "critical": VoicePriority.CRITICAL
        }
        
        priority = priority_map.get(severity.lower(), VoicePriority.NORMAL)
        
        # Format event message
        if event_type == "api_request":
            formatted_text = f"API request: {message}"
        elif event_type == "tool_execution":
            formatted_text = f"Tool execution: {message}"
        elif event_type == "agent_action":
            formatted_text = f"Agent action: {message}"
        elif event_type == "error":
            formatted_text = f"Error occurred: {message}"
        else:
            formatted_text = f"{event_type.replace('_', ' ').title()}: {message}"
        
        return self.speak(formatted_text, priority)
    
    def get_voices(self) -> Dict[str, Dict[str, Any]]:
        """Get available voices"""
        return self.voices.copy()
    
    def set_voice(self, voice_id: str) -> bool:
        """Set the default voice"""
        if voice_id in self.voices and self.engine:
            self.engine.setProperty('voice', self.voices[voice_id]['id'])
            return True
        return False
    
    def set_rate(self, rate: int) -> bool:
        """Set the speech rate"""
        if self.engine:
            self.engine.setProperty('rate', rate)
            return True
        return False
    
    def set_volume(self, volume: float) -> bool:
        """Set the speech volume (0.0 to 1.0)"""
        if self.engine:
            self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
            return True
        return False
    
    def stop_speaking(self):
        """Stop current speech"""
        if self.engine:
            self.engine.stop()
        self.is_speaking = False
    
    def clear_queue(self):
        """Clear the voice message queue"""
        self.message_queue.clear()
        logger.info("Voice message queue cleared")
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice engine status"""
        return {
            'enabled': self.enabled,
            'available': VOICE_AVAILABLE,
            'is_speaking': self.is_speaking,
            'queue_size': len(self.message_queue),
            'max_queue_size': self.max_queue_size,
            'voices_count': len(self.voices),
            'current_rate': self.engine.getProperty('rate') if self.engine else None,
            'current_volume': self.engine.getProperty('volume') if self.engine else None
        }
    
    def shutdown(self):
        """Shutdown the voice engine"""
        logger.info("Shutting down voice engine...")
        self.stop_event.set()
        self.clear_queue()
        self.stop_speaking()
        
        if self.voice_thread and self.voice_thread.is_alive():
            self.voice_thread.join(timeout=5)
        
        if self.engine:
            self.engine.stop()
            del self.engine
            self.engine = None
        
        logger.info("Voice engine shutdown complete")

# Global voice engine instance
_voice_engine: Optional[PulseVoiceEngine] = None

def initialize_voice_engine(config: Optional[Dict[str, Any]] = None) -> PulseVoiceEngine:
    """Initialize the global voice engine"""
    global _voice_engine
    if _voice_engine is None:
        _voice_engine = PulseVoiceEngine(config)
    return _voice_engine

def get_voice_engine() -> Optional[PulseVoiceEngine]:
    """Get the global voice engine instance"""
    return _voice_engine

def speak_alert(alert_type: str, message: str, severity: str = "normal") -> bool:
    """Speak an alert message"""
    engine = get_voice_engine()
    if engine:
        return engine.speak_alert(alert_type, message, severity)
    return False

def speak_metrics(metrics: Dict[str, Any]) -> bool:
    """Speak current metrics"""
    engine = get_voice_engine()
    if engine:
        return engine.speak_metrics(metrics)
    return False

def speak_event(event_type: str, message: str, severity: str = "normal") -> bool:
    """Speak an event notification"""
    engine = get_voice_engine()
    if engine:
        return engine.speak_event(event_type, message, severity)
    return False

def cleanup_voice_engine():
    """Cleanup the global voice engine"""
    global _voice_engine
    if _voice_engine:
        _voice_engine.shutdown()
        _voice_engine = None