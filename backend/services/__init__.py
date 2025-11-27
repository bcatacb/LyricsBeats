import os
import logging
from models import LyricsRequest, LyricsResponse

try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    AI_SERVICES_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).warning(f"AI services dependencies not installed: {e}")
    AI_SERVICES_AVAILABLE = False

logger = logging.getLogger(__name__)


def get_llm_chat():
    """Initialize LLM Chat for lyric generation"""
    if not AI_SERVICES_AVAILABLE:
        raise Exception("AI services dependencies not installed")
        
    return LlmChat(
        api_key=os.environ.get('EMERGENT_LLM_KEY'),
        session_id="beat_maker_session",
        system_message="You are a professional rap lyricist and songwriter. You create original, creative rap lyrics in various styles. You understand different rap genres like trap, boom bap, drill, conscious rap, and more. You can adapt to different flows, rhyme schemes, and themes."
    ).with_model("openai", "gpt-4o")


async def generate_lyrics(request: LyricsRequest) -> LyricsResponse:
    """
    Generate rap lyrics based on style and optional custom prompt
    """
    if not AI_SERVICES_AVAILABLE:
        raise Exception("AI services dependencies not installed")
        
    try:
        llm = get_llm_chat()
        
        # Build the prompt based on request parameters
        base_prompt = f"Create original rap lyrics in the {request.style} style."
        
        if request.custom_prompt:
            base_prompt += f" Additional instructions: {request.custom_prompt}"
        
        base_prompt += """
        
        Please provide:
        1. Original, creative lyrics (avoid clichés when possible)
        2. Good rhyme schemes and flow
        3. Appropriate content for the specified style
        4. 2-3 verses and a chorus structure
        5. Make it copyright-ready and original
        
        Format the response clearly with verse/chorus labels.
        """
        
        # Generate lyrics
        response = await llm.acreate([UserMessage(content=base_prompt)])
        
        # Extract the lyrics from response
        lyrics = response.content if hasattr(response, 'content') else str(response)
        
        logger.info(f"Generated lyrics in {request.style} style")
        
        return LyricsResponse(
            lyrics=lyrics,
            style=request.style
        )
        
    except Exception as e:
        logger.error(f"Error generating lyrics: {str(e)}")
        raise Exception(f"Failed to generate lyrics: {str(e)}")


async def generate_lyrics_with_user_style(user_style, custom_prompt=None) -> str:
    """
    Generate lyrics based on a user's custom style
    """
    try:
        llm = get_llm_chat()
        
        prompt = f"""
        Create original rap lyrics based on this style profile:
        
        Style Name: {user_style['name']}
        Description: {user_style['description']}
        Sample Lyrics: {user_style['sample_lyrics']}
        
        {"Additional instructions: " + custom_prompt if custom_prompt else ""}
        
        Please create original lyrics that match this style while being completely unique and copyright-ready.
        Include 2-3 verses and a chorus.
        """
        
        response = await llm.acreate([UserMessage(content=prompt)])
        lyrics = response.content if hasattr(response, 'content') else str(response)
        
        logger.info(f"Generated lyrics for user style: {user_style['name']}")
        return lyrics
        
    except Exception as e:
        logger.error(f"Error generating lyrics with user style: {str(e)}")
        raise Exception(f"Failed to generate lyrics: {str(e)}")
