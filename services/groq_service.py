"""
Groq LLM Service for AI Conversation
"""
from groq import Groq
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class GroqService:
    """Service for handling Groq LLM conversations"""
    
    def __init__(self, api_key=None, model=None):
        """
        Initialize Groq service
        
        Args:
            api_key: Groq API key (from config if None)
            model: Model to use (from config if None)
        """
        from config import Config
        
        api_key = api_key or Config.GROQ_API_KEY
        if not api_key:
            logger.warning("Groq API key not found. AI responses will not work.")
            self.client = None
            self.model = None
        else:
            try:
                self.client = Groq(api_key=api_key)
                self.model = model or Config.GROQ_MODEL or 'llama-3.3-70b-versatile'
                logger.info(f"Groq service initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Error initializing Groq: {str(e)}")
                self.client = None
                self.model = None
        
        # System prompt for interactive voice agent - Hindi language
        self.system_prompt = """आप एक सहायक और पेशेवर वॉइस असिस्टेंट हैं जो कॉल सेंटर के लिए काम करते हैं।
आप फोन पर ग्राहकों से हिंदी में बात कर रहे हैं, एक प्राकृतिक, बातचीत के तरीके से।

महत्वपूर्ण: आपको चाहिए:
- ग्राहक की जरूरतों को समझने के लिए जुड़ाव वाले प्रश्न पूछें
- बातचीत करने वाले और दोस्ताना बनें
- जवाब संक्षिप्त रखें (अधिकतम 2-3 वाक्य)
- जब उचित हो तो अनुवर्ती प्रश्न पूछें
- मदद करने में वास्तविक रुचि दिखाएं
- प्राकृतिक बोलचाल के पैटर्न का उपयोग करें (औपचारिक लेखन नहीं)
- हमेशा हिंदी में जवाब दें

अच्छे जवाबों के उदाहरण:
- "नमस्ते! आपसे बात करके खुशी हुई। मैं आपकी कैसे मदद कर सकती हूं?"
- "यह दिलचस्प लगता है! क्या आप मुझे इसके बारे में और बता सकते हैं?"
- "मैं इसमें आपकी मदद करने में खुशी होगी। आपको क्या विशिष्ट जानकारी चाहिए?"

याद रखें: आप एक वास्तविक बातचीत कर रहे हैं, इसलिए गर्मजोशी से बात करें, प्रश्न पूछें और स्वाभाविक रूप से जुड़ें! हमेशा हिंदी में जवाब दें।"""
    
    def generate_response(self, user_input, call_id=None, conversation_history=None):
        """
        Generate AI response to user input
        
        Args:
            user_input: User's spoken input (transcribed text)
            call_id: Optional call ID for context
            conversation_history: Optional list of previous messages
        
        Returns:
            str: AI response text
        """
        if not self.client:
            logger.error("Groq client not initialized. Please check API key.")
            return "मुझे खेद है, लेकिन मुझे इसे संसाधित करने में परेशानी हो रही है। क्या आप कृपया दोहरा सकते हैं?"
        
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=150,  # Keep responses short for voice
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"Generated response for call {call_id}: {ai_response[:100]}...")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}", exc_info=True)
            return "मुझे खेद है, लेकिन मुझे इसे संसाधित करने में परेशानी हो रही है। क्या आप कृपया दोहरा सकते हैं?"
    
    def generate_question(self, context=None):
        """
        Generate an engaging question to start or continue conversation
        
        Args:
            context: Optional context about the conversation
        
        Returns:
            str: Engaging question
        """
        if not self.client:
            return "मैं आज आपकी कैसे मदद कर सकती हूं?"
        
        try:
            prompt = "Generate a friendly, engaging question to start a phone conversation with a customer. Keep it short (one sentence) and natural."
            if context:
                prompt += f"\n\nContext: {context}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=50,
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating question: {str(e)}")
            return "मैं आज आपकी कैसे मदद कर सकती हूं?"
    
    def update_system_prompt(self, new_prompt):
        """
        Update the system prompt for different use cases
        
        Args:
            new_prompt: New system prompt text
        """
        self.system_prompt = new_prompt
        logger.info("System prompt updated")

