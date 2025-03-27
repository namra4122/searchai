"""
Gemini LLM integration module for the SearchAI application.
Handles reasoning and document content generation using Gemini.
"""

import asyncio
import logging
import time
import json
from typing import List, Dict, Any

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from searchai.config import GEMINI_API_KEY, GEMINI_MODEL

# Configure logging
from searchai.utils.logging_config import get_logger

logger = get_logger(__name__)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

from searchai.utils.exceptions import LLMError, ConfigurationError

class GeminiReasoner:
    """
    Provides reasoning and document content generation capabilities using Gemini LLM.
    """
    
    def __init__(self, model_name=GEMINI_MODEL):
        try:
            if not GEMINI_API_KEY:
                raise ConfigurationError("GEMINI_API_KEY is not configured")
                
            genai.configure(api_key=GEMINI_API_KEY)
            self.model_name = model_name
            self.model = genai.GenerativeModel(model_name=model_name)
            
            # Test the model
            self._test_model()
            
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize Gemini: {str(e)}")
    
    def _test_model(self):
        """Test the model connection"""
        try:
            test_response = self.model.generate_content("test")
            if not test_response or not test_response.text:
                raise LLMError("Model test generated no response")
        except Exception as e:
            raise LLMError(f"Model connection test failed: {str(e)}")
    
    async def generate_content(self, query: str, search_results: List[Dict[str, Any]], output_format: str) -> str:
        """
        Generate document content based on search results using Gemini.
        
        Args:
            query (str): The original user query
            search_results (List[Dict[str, Any]]): The search results from Crew AI
            output_format (str): The desired output format (markdown, pdf, ppt)
            
        Returns:
            str: Generated document content
        """

        logger.info(f"Generating content for query: {query}")
        start_time = time.time()
        
        try:
            # Validate inputs
            if not isinstance(search_results, list):
                raise ValueError("Invalid search results format")
            
            # Prepare the prompt for Gemini
            prompt = self._create_prompt(query, search_results, output_format)

            
            # Set generation config based on output format

            generation_config = self._get_generation_config(output_format)

            
            # Run Gemini in a separate thread to avoid blocking the event loop
            loop = asyncio.get_running_loop()
            try:
                response = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(
                        prompt,
                        generation_config=generation_config
                    )
                )
            except Exception as e:
                raise LLMError(f"Content generation failed: {str(e)}")
            
            if not response or not response.text:
                raise LLMError("Model generated empty response")
            
            content = response.text

            duration = time.time() - start_time
            logger.info(f"Content generation completed in {duration:.2f} seconds")
            
            return content
            
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"Unexpected error during content generation: {str(e)}")
    
    def _create_prompt(self, query: str, search_results: List[Dict[str, Any]], output_format: str) -> str:
        """
        Create a prompt for Gemini based on the query and search results.
        
        Args:
            query (str): The original user query
            search_results (List[Dict[str, Any]]): The search results
            output_format (str): The desired output format
            
        Returns:
            str: Formatted prompt for Gemini
        """

        # Format search results as a string
        results_text = ""
        for i, result in enumerate(search_results, 1):
            results_text += f"Source {i}:\n"
            results_text += f"Title: {result.get('title', 'Untitled')}\n"
            results_text += f"URL: {result.get('url', 'No URL')}\n"
            results_text += f"Summary: {result.get('snippet', 'No description')}\n\n"
        
        # Create format-specific instructions
        format_instructions = self._get_format_instructions(output_format)
        
        # Build the complete prompt
        prompt = f"""
        You are an expert researcher and writer. Your task is to create a comprehensive and well-structured document
        based on the following search results. The document should address this query: "{query}"
        
        Here are the search results to use as your source material:
        
        {results_text}
        
        {format_instructions}
        
        Make sure your response is informative, accurate, and directly answers the query. Use the provided search results
        as your primary source of information. If you need to make educated guesses or inferences, clearly indicate them.
        
        Write the document now.
        """

        
        return prompt
    
    def _get_format_instructions(self, output_format: str) -> str:
        """
        Get format-specific instructions for the LLM.
        
        Args:
            output_format (str): The desired output format
            
        Returns:
            str: Format-specific instructions
        """
        if output_format.lower() == "markdown":
            return """
            Format your response as a Markdown document with:
            1. A clear title (use # for the main title)
            2. Section headers (use ## for major sections and ### for subsections)
            3. Bullet points or numbered lists where appropriate
            4. Bold or italics for emphasis
            5. Code blocks if needed
            6. Citations to the source material
            
            IMPORTANT: Do NOT wrap the entire response in markdown code blocks (```).
            Write the content directly in markdown format.
            """
        
        elif output_format.lower() == "pdf":
            return """
            Format your response as a clean document suitable for PDF conversion with:
            1. A clear title at the top (no special formatting needed)
            2. Section headers should be plain text, not markdown formatting
            3. Concise paragraphs with clear spacing between them
            4. Use plain bullet points (•) for lists
            5. Use numbers (1., 2., etc.) for numbered lists
            6. Do not use markdown formatting like **, __, or ##
            7. Citations should be numbered [1], [2], etc.
            8. Include a "References" section at the end with numbered sources
            
            Example format:

            Understanding Machine Learning
            
            Introduction
            Machine learning is a branch of artificial intelligence...
            
            Key Concepts
            • Supervised Learning: Training with labeled data...
            • Unsupervised Learning: Finding patterns in unlabeled data...
            
            Applications
            1. Healthcare: Diagnosis and treatment planning [1]
            2. Finance: Fraud detection and risk assessment [2]
            
            References
            [1] Source Title 1 - URL
            [2] Source Title 2 - URL
            """
        
        elif output_format.lower() == "ppt":
            return """
            Format your response as an engaging PowerPoint presentation with:
            
            1. Title Slide:
            --- Slide: Title ---
            Title: [Main Title]
            Subtitle: [Brief Description]
            Theme: [tech/business/science/education] (This helps choose appropriate styling)
            
            2. Agenda/Overview Slide:
            --- Slide: Overview ---
            • [Key Point 1]
            • [Key Point 2]
            • [Key Point 3]
            
            3. Content Slides (3-5 points per slide):
            --- Slide: [Section Title] ---
            • [Main Point]
            • [Supporting Point]
            • [Example/Application]
            Image Suggestion: [Brief description of relevant image]
            Color Theme: [suggested color - blue/green/orange/etc.]
            
            4. Visual Elements:
            - Suggest relevant images for each slide
            - Indicate important terms to highlight
            - Suggest color schemes based on topic
            - Indicate any data that could be shown as charts
            
            5. Conclusion Slide:
            --- Slide: Key Takeaways ---
            • [Main Takeaway 1]
            • [Main Takeaway 2]
            • [Call to Action/Next Steps]
            
            For each slide, include:
            Notes: [Detailed speaking notes for presenter]
            Layout: [simple/two-column/comparison/image-focus]
            Emphasis: [key terms to highlight]
            
            Example:
            --- Slide: Introduction to Deep Learning ---
            Title: What is Deep Learning?
            Theme: tech
            Layout: image-focus
            • Neural networks inspired by human brain
            • Subset of machine learning
            • Powers modern AI applications
            Image Suggestion: Neural network diagram with glowing connections
            Color Theme: deep blue and white
            Emphasis: "neural networks", "machine learning"
            
            Notes: Deep learning is a revolutionary approach to artificial intelligence...
            ---
            """
            
        else:
            return "Format your response as a clear, well-structured document that directly answers the query."
    
    def _get_generation_config(self, output_format: str) -> GenerationConfig:
        """
        Create generation configuration based on the output format.
        
        Args:
            output_format (str): The desired output format
            
        Returns:
            GenerationConfig: Configuration for Gemini generation
        """
        # Base configuration that works for all formats
        config = {
            "temperature": 0.2,  # Lower temperature for factual content
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 4096,  # Adjust based on expected document length
        }
        
        # Format-specific adjustments
        if output_format.lower() == "ppt":
            # Higher temperature for more creative presentation content
            config["temperature"] = 0.4
            # Shorter output for presentation slides
            config["max_output_tokens"] = 2048
        
        return GenerationConfig(**config)

async def process_with_gemini(query: str, search_results: List[Dict[str, Any]], output_format: str) -> str:
    """
    Public function to process search results with Gemini.
    
    Args:
        query (str): The original user query
        search_results (List[Dict[str, Any]]): The search results from Crew AI
        output_format (str): The desired output format (markdown, pdf, ppt)
        
    Returns:
        str: Generated document content
    """

    
    # Validate search_results
    if not isinstance(search_results, list):
        logger.error(f"Invalid search_results type: {type(search_results)}")
        search_results = [search_results] if search_results else []
    

    reasoner = GeminiReasoner()

    
    try:
        # Set a timeout for the LLM processing

        content = await asyncio.wait_for(
            reasoner.generate_content(query, search_results, output_format),
            timeout=300.0
        )
        
        # Process and validate content
        if not content:
            raise LLMError("Generated content is empty")
        
        # Remove any wrapping markdown code blocks
        content = content.strip()
        if content.startswith("```markdown"):
            content = content[len("```markdown"):].strip()
        if content.startswith("```"):
            content = content[3:].strip()
        if content.endswith("```"):
            content = content[:-3].strip()
            

        return content
    except asyncio.TimeoutError:
        raise LLMError("LLM processing timed out after 300 seconds")
    except Exception as e:
        raise LLMError(f"Unexpected error during LLM processing: {str(e)}")