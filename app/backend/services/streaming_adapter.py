"""
Streaming adapter for converting LangChain Python streaming events to AI SDK compatible format
"""
import json
import asyncio
from typing import AsyncGenerator, Dict, Any, Optional
from datetime import datetime
import uuid


class AISDKStreamAdapter:
    """Converts LangChain streaming events to AI SDK data stream format."""
    
    @staticmethod
    def create_text_delta_event(content: str) -> str:
        """Create an AI SDK text-delta event."""
        return f'0:"{content}"\n'
    
    @staticmethod
    def create_data_event(data: Dict[str, Any]) -> str:
        """Create an AI SDK data event."""
        # Format: 2:[{"type":"tool-call","toolCallId":"...","toolName":"...","args":{...}}]
        return f'2:[{json.dumps(data)}]\n'
    
    @staticmethod
    def create_error_event(error: str) -> str:
        """Create an AI SDK error event."""
        return f'3:"{error}"\n'
    
    @staticmethod
    def create_finish_event(data: Optional[Dict[str, Any]] = None) -> str:
        """Create an AI SDK finish event."""
        if data:
            return f'd:{json.dumps(data)}\n'
        return 'd:{}\n'
    
    @staticmethod
    async def convert_langchain_to_ai_sdk(
        langchain_events: AsyncGenerator[str, None]
    ) -> AsyncGenerator[str, None]:
        """
        Convert LangChain streaming events to AI SDK format.
        
        LangChain events come as JSON strings with different event types.
        We convert them to AI SDK's streaming format.
        """
        accumulated_content = []
        
        async for event_str in langchain_events:
            try:
                # Skip [DONE] marker
                if event_str == "[DONE]":
                    # Send any accumulated content
                    if accumulated_content:
                        yield AISDKStreamAdapter.create_text_delta_event(''.join(accumulated_content))
                    yield AISDKStreamAdapter.create_finish_event()
                    break
                
                # Parse the event
                event = json.loads(event_str)
                event_type = event.get("type", "")
                data = event.get("data", {})
                
                # Handle different event types
                if event_type == "llm_thinking":
                    # Convert thinking events to tool calls for visibility
                    yield AISDKStreamAdapter.create_data_event({
                        "type": "tool-call",
                        "toolCallId": str(uuid.uuid4()),
                        "toolName": "thinking",
                        "args": {"message": data.get("message", ""), "details": data.get("details", "")}
                    })
                    
                elif event_type == "agent_action":
                    # Convert agent actions to tool calls
                    yield AISDKStreamAdapter.create_data_event({
                        "type": "tool-call", 
                        "toolCallId": str(uuid.uuid4()),
                        "toolName": data.get("tool", "unknown"),
                        "args": {"input": data.get("tool_input", ""), "message": data.get("message", "")}
                    })
                    
                elif event_type == "tool_start":
                    # Tool start events
                    yield AISDKStreamAdapter.create_data_event({
                        "type": "tool-call-streaming-start",
                        "toolCallId": str(uuid.uuid4()),
                        "toolName": data.get("tool_name", "unknown"),
                        "args": {"input": data.get("input", ""), "message": data.get("message", "")}
                    })
                    
                elif event_type == "tool_end":
                    # Tool end events - accumulate the output
                    output = data.get("output", "")
                    if output:
                        accumulated_content.append(f"\n\n{data.get('message', 'Result')}:\n{output}")
                        
                elif event_type == "final_result":
                    # Final result - send as text
                    output = data.get("output", "")
                    if output:
                        # Send any accumulated content first
                        if accumulated_content:
                            yield AISDKStreamAdapter.create_text_delta_event(''.join(accumulated_content))
                            accumulated_content = []
                        # Then send the final output
                        yield AISDKStreamAdapter.create_text_delta_event(output)
                        
                elif event_type == "error":
                    yield AISDKStreamAdapter.create_error_event(data.get("error", "Unknown error"))
                    
                else:
                    # For any other event type, check if there's a message to display
                    message = data.get("message", "")
                    if message:
                        accumulated_content.append(f"\n{message}")
                        
            except json.JSONDecodeError:
                # If it's not JSON, treat it as plain text content
                yield AISDKStreamAdapter.create_text_delta_event(event_str)
            except Exception as e:
                yield AISDKStreamAdapter.create_error_event(f"Stream processing error: {str(e)}")
                
        # Ensure we send finish event
        yield AISDKStreamAdapter.create_finish_event()


class LangChainToSSEAdapter:
    """Adapter to convert LangChain events to Server-Sent Events format."""
    
    @staticmethod
    async def convert_to_sse(
        langchain_events: AsyncGenerator[str, None],
        include_reasoning: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Convert LangChain events to SSE format that's compatible with AI SDK expectations.
        
        Args:
            langchain_events: Stream of LangChain events
            include_reasoning: Whether to include reasoning/thinking events
        """
        message_id = str(uuid.uuid4())
        
        # Send initial message start event
        yield f"data: {json.dumps({'type': 'message-start', 'id': message_id, 'role': 'assistant'})}\n\n"
        
        accumulated_text = []
        has_sent_text = False
        buffer_content = []
        
        async for event_str in langchain_events:
            if event_str == "[DONE]":
                break
                
            try:
                event = json.loads(event_str)
                event_type = event.get("type", "")
                data = event.get("data", {})
                
                # Convert events based on type
                if event_type == "llm_thinking" and include_reasoning:
                    # Send as a reasoning event
                    message = data.get("message", "")
                    if message:
                        yield f"data: {json.dumps({'type': 'llm_thinking', 'data': {'message': message}})}\n\n"
                        
                elif event_type == "agent_action" and include_reasoning:
                    # Send tool usage info
                    message = data.get("message", "")
                    tool = data.get("tool", "")
                    if message:
                        yield f"data: {json.dumps({'type': 'agent_action', 'data': {'message': message, 'tool': tool}})}\n\n"
                        
                elif event_type == "tool_start" and include_reasoning:
                    # Send tool start info
                    message = data.get("message", "")
                    tool_name = data.get("tool_name", "")
                    if message:
                        yield f"data: {json.dumps({'type': 'tool_start', 'data': {'message': message, 'tool_name': tool_name}})}\n\n"
                        
                elif event_type == "tool_end":
                    # Buffer tool results for inclusion in final response
                    output = data.get("output", "")
                    message = data.get("message", "")
                    if output:
                        # Store for later inclusion
                        buffer_content.append((message, output))
                        
                elif event_type == "final_result":
                    # This is the main response content
                    output = data.get("output", "")
                    if output:
                        # First send any buffered tool results as part of the response
                        if buffer_content and include_reasoning:
                            for msg, result in buffer_content:
                                preview = result[:100] + "..." if len(result) > 100 else result
                                text = f"\n📊 {msg}: {preview}\n" if msg else f"\n📊 Result: {preview}\n"
                                yield f"data: {json.dumps({'type': 'text-delta', 'textDelta': text})}\n\n"
                            yield f"data: {json.dumps({'type': 'text-delta', 'textDelta': '\n---\n\n'})}\n\n"
                        
                        # Then send the main response in chunks for smooth streaming
                        chunk_size = 50  # Characters per chunk
                        for i in range(0, len(output), chunk_size):
                            chunk = output[i:i + chunk_size]
                            yield f"data: {json.dumps({'type': 'text-delta', 'textDelta': chunk})}\n\n"
                            await asyncio.sleep(0.01)  # Small delay for smooth streaming
                        has_sent_text = True
                        
                elif event_type == "error":
                    # Send error
                    error_msg = data.get("error", "Unknown error")
                    yield f"data: {json.dumps({'type': 'error', 'error': error_msg})}\n\n"
                    
            except json.JSONDecodeError:
                # Treat as content if not JSON
                if event_str.strip():
                    yield f"data: {json.dumps({'type': 'text-delta', 'textDelta': event_str})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        # Send message end event
        yield f"data: {json.dumps({'type': 'message-end', 'id': message_id})}\n\n"
        yield "data: [DONE]\n\n" 