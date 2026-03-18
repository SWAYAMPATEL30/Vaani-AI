"""
OpenAI Service for AI Conversation
"""
import openai
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for handling OpenAI GPT conversations"""
    
    def __init__(self, api_key=None, model=None, max_tokens=None, temperature=None):
        """
        Initialize OpenAI service
        
        Args:
            api_key: OpenAI API key (from config if None)
            model: Model to use (from config if None)
            max_tokens: Maximum tokens in response (from config if None)
            temperature: Response creativity (from config if None)
        """
        from config import Config
        
        api_key = api_key or Config.OPENAI_API_KEY
        if not api_key:
            logger.warning("OpenAI API key not found. AI responses will not work.")
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=api_key)
        
        self.model = model or Config.OPENAI_MODEL
        self.max_tokens = max_tokens or Config.OPENAI_MAX_TOKENS
        self.temperature = temperature or Config.OPENAI_TEMPERATURE
        
        # System prompt for voice agent
        self.system_prompt = """You are a helpful and professional voice assistant for a call center. 
You are speaking to customers over the phone. Keep your responses:
- Concise and natural (as if speaking, not writing)
- Friendly and professional
- Under 2-3 sentences when possible
- Clear and easy to understand
- Focused on helping the customer

Remember: You are having a voice conversation, so be conversational and natural."""
        
        logger.info(f"OpenAI service initialized with model: {model}")
    
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
            logger.error("OpenAI client not initialized. Please check API key.")
            return "I apologize, but I'm having trouble processing that. Could you please repeat?"
        
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
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"Generated response for call {call_id}: {ai_response[:100]}...")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}", exc_info=True)
            return "I apologize, but I'm having trouble processing that. Could you please repeat?"
    
    def update_system_prompt(self, new_prompt):
        """
        Update the system prompt for different use cases
        
        Args:
            new_prompt: New system prompt text
        """
        self.system_prompt = new_prompt
        logger.info("System prompt updated")
    
    def get_conversation_summary(self, conversation_history):
        """
        Generate a summary of the conversation
        
        Args:
            conversation_history: List of conversation messages
        
        Returns:
            str: Conversation summary
        """
        try:
            summary_prompt = "Summarize the following conversation in 2-3 sentences:"
            messages = [
                {"role": "system", "content": summary_prompt},
                {"role": "user", "content": "\n".join([f"{m['role']}: {m['content']}" for m in conversation_history])}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}", exc_info=True)
            return None

