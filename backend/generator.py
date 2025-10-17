"""
LLM generator module with strict and prefer mode prompts.
Supports OpenAI, Ollama, and other LLM providers.
"""

import os
import requests
from typing import List, Dict, Any, Optional
from openai import OpenAI


# Prompt templates
STRICT_MODE_PROMPT = """You are a STEM solver. Use ONLY the following retrieved chunks (listed below). For every step include a citation in the format [doc:<filename> | p:<page> | chunk:<id>]. If any required step cannot be supported by the chunks, respond exactly: "No supported solution found in resources." Do NOT invent methods, facts, or steps outside the chunks. Keep steps concise and match the style of the retrieved content where possible.

Retrieved chunks:
{chunks}

Question:
{question}

Provide a step-by-step solution using ONLY the information from the retrieved chunks above. Include citations for every step."""

PREFER_MODE_PROMPT = """You are a STEM solver. Prefer using the following retrieved chunks. For steps not supported by the chunks, you may use general knowledge but mark those steps clearly with (UNSUPPORTED) and include a confidence score for each such step. Provide inline citations when you use chunks.

Retrieved chunks:
{chunks}

Question:
{question}

Provide a step-by-step solution. Prefer the retrieved chunks, but if needed, supplement with general knowledge. Mark any unsupported steps with (UNSUPPORTED) and rate confidence (HIGH/MEDIUM/LOW)."""


class LLMGenerator:
    """Handles LLM generation with strict and prefer modes."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        provider: str = "openai",
        ollama_base_url: str = "http://localhost:11434"
    ):
        """
        Initialize LLM generator.
        
        Args:
            api_key: API key (for OpenAI, Gemini, etc.)
            model: Model name (gpt-4, mistral, gemini-pro, etc.)
            provider: LLM provider (openai, ollama, gemini)
            ollama_base_url: Base URL for Ollama server
        """
        self.provider = provider.lower()
        self.model = model
        self.ollama_base_url = ollama_base_url
        
        # Initialize based on provider
        if self.provider == "ollama":
            print(f"✓ Ollama client initialized with model: {model} at {ollama_base_url}")
        elif self.provider == "openai":
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
            self.client = OpenAI(api_key=api_key)
            print(f"✓ OpenAI client initialized with model: {model}")
        elif self.provider == "gemini":
            # Gemini support can be added here
            print(f"✓ Gemini client initialized with model: {model}")
        else:
            raise ValueError(f"Unsupported provider: {provider}. Use 'openai', 'ollama', or 'gemini'")
    
    def generate_solution(
        self,
        question: str,
        retrieved_chunks: List[Dict[str, Any]],
        mode: str = "prefer",
        method_constraints: Optional[List[str]] = None,
        max_tokens: int = 2000,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Generate a solution using the LLM.
        
        Args:
            question: The question to solve
            retrieved_chunks: List of retrieved chunk dictionaries
            mode: "strict" or "prefer"
            method_constraints: Optional list of allowed methods
            max_tokens: Maximum response tokens
            temperature: Sampling temperature
            
        Returns:
            Dictionary with solution and metadata
        """
        # Format retrieved chunks
        chunks_text = self._format_chunks(retrieved_chunks)
        
        # Select prompt template
        if mode == "strict":
            prompt = STRICT_MODE_PROMPT.format(chunks=chunks_text, question=question)
        else:
            prompt = PREFER_MODE_PROMPT.format(chunks=chunks_text, question=question)
        
        # Add method constraints if provided
        if method_constraints:
            constraints_text = ", ".join(method_constraints)
            prompt += f"\n\nMethod constraints: Use only {constraints_text} methods."
        
        # Generate response based on provider
        if self.provider == "ollama":
            response_text = self._generate_ollama(prompt, max_tokens, temperature)
        elif self.provider == "openai":
            response_text = self._generate_openai(prompt, max_tokens, temperature)
        elif self.provider == "gemini":
            response_text = self._generate_gemini(prompt, max_tokens, temperature)
        else:
            response_text = f"Error: Unsupported provider {self.provider}"
        
        return {
            "solution": response_text,
            "mode": mode,
            "model": self.model,
            "provider": self.provider,
            "chunks_used": len(retrieved_chunks),
            "prompt_length": len(prompt)
        }
    
    def _generate_openai(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful STEM tutor that provides accurate, step-by-step solutions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating solution: {str(e)}"
    
    def _generate_ollama(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using Ollama API."""
        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json().get("response", "No response from Ollama")
            else:
                return f"Ollama error: {response.status_code} - {response.text}"
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Make sure Ollama is running (ollama serve) and the model is pulled (ollama pull mistral)"
        except Exception as e:
            return f"Error generating solution with Ollama: {str(e)}"
    
    def _generate_gemini(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using Google Gemini API (placeholder for future implementation)."""
        return "Gemini support coming soon. Please use Ollama or OpenAI for now."
    
    def _generate_local_transformers(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using local transformers model (for future HuggingFace support)."""
        try:
            import torch
            
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.local_model.device)
            
            outputs = self.local_model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.95
            )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract response after prompt
            if prompt in response:
                response = response.split(prompt)[1].strip()
            
            return response
        except Exception as e:
            return f"Error generating with local LLM: {str(e)}"
    
    def _format_chunks(self, chunks: List[Dict[str, Any]]) -> str:
        """Format chunks for prompt."""
        formatted = []
        
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get('metadata', {})
            chunk_text = chunk.get('chunk_text', '')
            chunk_id = chunk.get('chunk_id', 'unknown')
            
            filename = metadata.get('filename', 'unknown')
            page = metadata.get('page', 0)
            
            citation = f"[doc:{filename} | p:{page} | chunk:{chunk_id}]"
            formatted.append(f"Chunk {i}: {citation}\n{chunk_text}")
        
        return "\n\n---\n\n".join(formatted)
    
    def parse_solution_steps(self, solution_text: str) -> List[Dict[str, Any]]:
        """
        Parse solution into individual steps.
        
        Args:
            solution_text: Generated solution text
            
        Returns:
            List of step dictionaries
        """
        # Simple step parsing - look for numbered steps or newlines
        lines = solution_text.split('\n')
        steps = []
        current_step = []
        step_num = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_step:
                    steps.append({
                        "step_num": step_num,
                        "text": "\n".join(current_step),
                        "citations": self._extract_citations("\n".join(current_step)),
                        "unsupported": "(UNSUPPORTED)" in "\n".join(current_step)
                    })
                    current_step = []
                continue
            
            # Check if new numbered step
            if line[0].isdigit() and ('. ' in line or ') ' in line):
                if current_step:
                    steps.append({
                        "step_num": step_num,
                        "text": "\n".join(current_step),
                        "citations": self._extract_citations("\n".join(current_step)),
                        "unsupported": "(UNSUPPORTED)" in "\n".join(current_step)
                    })
                
                step_num += 1
                current_step = [line]
            else:
                current_step.append(line)
        
        # Add last step
        if current_step:
            steps.append({
                "step_num": step_num,
                "text": "\n".join(current_step),
                "citations": self._extract_citations("\n".join(current_step)),
                "unsupported": "(UNSUPPORTED)" in "\n".join(current_step)
            })
        
        return steps
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract citation strings from text."""
        import re
        
        # Pattern: [doc:filename | p:page | chunk:id]
        pattern = r'\[doc:[^\]]+\]'
        citations = re.findall(pattern, text)
        
        return citations


def generate_step_by_step(
    question: str,
    chunks: List[Dict[str, Any]],
    mode: str = "prefer",
    api_key: Optional[str] = None
) -> str:
    """
    Convenience function for generating solutions.
    
    Args:
        question: The question
        chunks: Retrieved chunks
        mode: "strict" or "prefer"
        api_key: OpenAI API key
        
    Returns:
        Solution text
    """
    generator = LLMGenerator(api_key=api_key)
    result = generator.generate_solution(question, chunks, mode=mode)
    return result['solution']
