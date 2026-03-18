"""
Google Gemini Service for AI Conversation
"""
import google.generativeai as genai
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for handling Google Gemini AI conversations"""
    
    def __init__(self, api_key=None, model=None):
        """
        Initialize Gemini service
        
        Args:
            api_key: Gemini API key (from config if None)
            model: Model to use (from config if None)
        """
        from config import Config
        
        api_key = api_key or Config.GEMINI_API_KEY
        if not api_key:
            logger.warning("Gemini API key not found. AI responses will not work.")
            self.client = None
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model_name = model or Config.GEMINI_MODEL or 'gemini-pro'
            try:
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini service initialized with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Error initializing Gemini model: {str(e)}")
                self.model = None
                self.client = None
        
        # System prompt for voice agent
        self.system_prompt = """You are a helpful and professional voice assistant for a call center. 
You are speaking to customers over the phone. Keep your responses:
- Concise and natural (as if speaking, not writing)
- Friendly and professional
- Under 2-3 sentences when possible
- Clear and easy to understand
- Focused on helping the customer

Remember: You are having a voice conversation, so be conversational and natural."""
    
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
        if not self.model:
            logger.error("Gemini model not initialized. Please check API key.")
            return "I apologize, but I'm having trouble processing that. Could you please repeat?"
        
        try:
            # Build conversation context
            prompt = self.system_prompt + "\n\n"
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    if role == 'user':
                        prompt += f"User: {content}\n"
                    elif role == 'assistant':
                        prompt += f"Assistant: {content}\n"
            
            # Add current user input
            prompt += f"User: {user_input}\nAssistant:"
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                )
            )
            
            ai_response = response.text.strip()
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
        if not self.model:
            return None
        
        try:
            summary_prompt = "Summarize the following conversation in 2-3 sentences:\n\n"
            summary_prompt += "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in conversation_history])
            
            response = self.model.generate_content(
                summary_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=200,
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}", exc_info=True)
            return None




