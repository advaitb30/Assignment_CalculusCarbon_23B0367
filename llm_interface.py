"""
LLM Interface - Phase 3
Groq API integration for natural language responses

TECHNICAL EXPLANATION:
- Uses Groq's Llama 3.1 70B model
- Temperature 0.3 for factual, consistent responses
- Context is formatted query results + prompt engineering
- Generates natural language from structured data
"""

from groq import Groq
import json

class LLMInterface:
    """Interface to Groq API for generating responses"""
    
    def __init__(self):
        # Hardcoded API key (as requested)
        self.api_key = "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"
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"  # Fast and capable (updated model)
        
        # Model specs for reference:
        # - 70 billion parameters
        # - 128K context window
        # - ~80 tokens/second generation speed
    
    def generate_response(self, user_query, context_data, query_type=None):
        """
        Generate natural language response from query results
        
        FLOW:
        1. Build system prompt (sets AI personality/instructions)
        2. Format context_data into readable text
        3. Combine into user message
        4. Send to Groq API
        5. Receive generated text
        
        Args:
            user_query: Original user question
            context_data: Data retrieved from query engine
            query_type: Type of query for specialized prompts
        """
        
        # System prompt - defines AI behavior
        system_prompt = """You are an AI assistant for Calculus Carbon, a firm specializing in Nature-based Solutions (NbS) investments.

Your role is to help the deal team by answering questions about:
- Project developers and their projects
- Investor mandates and preferences
- Communications history
- Matching opportunities

Guidelines:
- Be concise and factual
- Always cite sources (project IDs, email IDs, etc.)
- Highlight key metrics (hectares, ticket sizes, regions)
- Format responses clearly with bullet points when appropriate
- If data is missing, acknowledge it clearly

Remember: You're providing business intelligence, not creative writing."""
        
        # Format context based on query type
        context = self._format_context(context_data, query_type)
        
        # Build user message (combines question + data)
        user_message = f"""Question: {user_query}

Context:
{context}

Please provide a clear, professional answer based on this data."""
        
        # Call Groq API
        # This sends ~200-500 tokens, receives ~300-800 tokens back
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,  # Low temp = more deterministic, factual
            max_tokens=1000,   # Limit response length
            top_p=1.0,         # Nucleus sampling (1.0 = consider all tokens)
            stream=False       # Get complete response at once
        )
        
        # Extract generated text
        return response.choices[0].message.content
    
    def _format_context(self, context_data, query_type):
        """
        Format query results into readable context for LLM
        
        WHY: LLM needs well-structured text, not raw Python objects
        """
        
        if query_type == 'developers_by_region':
            return self._format_developers_context(context_data)
        
        elif query_type == 'matching_investors':
            return self._format_investors_context(context_data)
        
        elif query_type == 'communications_summary':
            return self._format_communications_context(context_data)
        
        elif query_type == 'meeting_actionables':
            return self._format_meeting_context(context_data)
        
        else:
            # Generic formatting for semantic search results
            return json.dumps(context_data, indent=2)
    
    def _format_developers_context(self, results):
        """Format developer query results"""
        if not results:
            return "No developers found matching the criteria."
        
        context = f"Found {len(results)} developers:\n\n"
        for dev in results:
            context += f"- {dev['developer']} ({dev['developer_id']})\n"
            context += f"  Project: {dev['project_id']}\n"
            context += f"  Country: {dev['country']}\n"
            context += f"  Hectares: {dev.get('hectares', 'N/A')}\n"
            context += f"  Est. Credits/Year: {dev.get('credits', 'N/A')}\n"
            context += f"  Status: {dev.get('status', 'N/A')}\n\n"
        
        return context
    
    def _format_investors_context(self, results):
        """Format investor matching results"""
        if not results or not results.get('matching_investors'):
            return "No matching investors found."
        
        project = results['project']
        investors = results['matching_investors']
        
        context = f"Project Details:\n"
        context += f"- ID: {project.get('ProjectID')}\n"
        context += f"- Developer: {project.get('DeveloperName')}\n"
        context += f"- Type: {project.get('ProjectType')}\n"
        context += f"- Country: {project.get('Country')}\n"
        context += f"- Hectares: {project.get('Hectares')}\n\n"
        
        context += f"Matching Investors ({len(investors)}):\n\n"
        for inv in investors:
            context += f"- {inv['investor']} ({inv['investor_id']})\n"
            context += f"  Sector Focus: {inv['sector_focus']}\n"
            context += f"  Region Focus: {inv['region_focus']}\n"
            context += f"  Ticket Size: {inv['ticket_min']}-{inv['ticket_max']} {inv['currency']}\n"
            context += f"  Contact: {inv['contact']} ({inv['email']})\n\n"
        
        return context
    
    def _format_communications_context(self, results):
        """Format communications summary"""
        if not results or results.get('total_count', 0) == 0:
            return "No communications found for this entity."
        
        entity = results['entity']
        comms = results['communications']
        
        context = f"Entity: {entity['canonical_name']} ({entity['entity_id']})\n"
        context += f"Total Communications: {results['total_count']}\n\n"
        
        context += "Communications:\n\n"
        for comm in comms:
            context += f"[{comm['type'].upper()}] {comm['id']}\n"
            if comm.get('date'):
                context += f"Date: {comm['date']}\n"
            if comm.get('from'):
                context += f"From: {comm['from']}\n"
            if comm.get('subject'):
                context += f"Subject: {comm['subject']}\n"
            
            # Truncate long bodies
            body = comm.get('body', '')
            if len(body) > 300:
                body = body[:300] + "..."
            context += f"Content: {body}\n\n"
        
        return context
    
    def _format_meeting_context(self, results):
        """Format meeting transcript results"""
        if not results:
            return "No meeting transcripts found for this entity."
        
        entity = results['entity']
        
        context = f"Entity: {entity['canonical_name']} ({entity['entity_id']})\n"
        context += f"Transcript ID: {results['transcript_id']}\n\n"
        context += f"Meeting Transcript:\n{results['transcript_text']}\n\n"
        context += "Please extract actionable items, next steps, and key decisions from this transcript."
        
        return context
    
    def extract_actionables(self, transcript_text):
        """
        Specialized function to extract action items from transcript
        
        TECHNICAL NOTE:
        - Uses lower temperature (0.2) for more structured extraction
        - Specialized prompt engineering for task-specific output
        - Good for extracting structured info from unstructured text
        """
        
        system_prompt = """You are an expert at extracting actionable items from meeting transcripts.

Extract and list:
1. Action items (who needs to do what)
2. Deadlines or timeframes mentioned
3. Key decisions made
4. Next steps

Format as clear bullet points."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract actionables from this meeting transcript:\n\n{transcript_text}"}
            ],
            temperature=0.2,  # Even lower for structured extraction
            max_tokens=800
        )
        
        return response.choices[0].message.content


"""
===============================================================================
TECHNICAL DEEP DIVE: How This Works
===============================================================================

1. TOKENIZATION (Groq's side, automatic):
   Input text → Broken into tokens → Token IDs
   Example: "VerdeNova Solutions" → ["Verde", "Nova", "Solutions"] 
                                  → [23451, 8976, 45123]

2. EMBEDDING (Model's internal layers):
   Each token ID → 8192-dim vector (for Llama 3.1 70B)
   These vectors capture semantic meaning

3. TRANSFORMER PROCESSING (80 layers):
   - Self-attention: Tokens "attend" to relevant other tokens
   - Feed-forward: Process and transform information
   - Residual connections: Preserve information flow
   
   Example attention pattern:
   "developers" → strong attention to "ARR", "Latin America", "projects"
   "have" → weak attention (function word)

4. NEXT TOKEN PREDICTION (Iterative):
   Model outputs probability distribution over all ~128K tokens
   
   Temperature 0.3 sharpens distribution:
   - High prob tokens become more likely
   - Low prob tokens suppressed
   - Result: Consistent, factual output
   
   Generation loop:
   Start: "<|start|>"
   → predict "Based" (p=0.82)
   → predict "on" (p=0.91)
   → predict "the" (p=0.95)
   → ... continues until <|end|> or max_tokens

5. DETOKENIZATION (Automatic):
   Token IDs → Text
   [8070, 220, 18] → "Found 3"

===============================================================================
KEY PARAMETERS EXPLAINED
===============================================================================

temperature=0.3
  - Controls randomness
  - 0.0 = Always most likely token (deterministic)
  - 1.0 = Sample according to probabilities (creative)
  - 0.3 = Mostly deterministic, slight variation
  - YOUR USE: Factual answers, minimal hallucination

max_tokens=1000
  - Maximum response length
  - 1 token ≈ 0.75 words
  - 1000 tokens ≈ 750 words
  - Prevents runaway generation

top_p=1.0 (nucleus sampling)
  - Only consider top tokens that sum to probability p
  - 1.0 = Consider all tokens (standard)
  - 0.9 = Only top 90% probability mass
  - YOUR USE: Standard setting, full vocabulary

===============================================================================
"""