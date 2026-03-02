import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage
from models import ChatRequest 
from graph import agent

app = FastAPI(title="Stock Analysis Agent")

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    async def event_generator():
        async for chunk in agent.astream(
            {"messages": input_messages}, 
            config=config, 
            stream_mode="updates" 
        ):
            for node_name, node_update in chunk.items():
                if "messages" in node_update:
                    last_msg = node_update["messages"][-1]
                    
                    if getattr(last_msg, "tool_calls", None):
                        yield json.dumps({
                            "type": "tool_call",
                            "node": node_name,
                            "calls": last_msg.tool_calls
                        }) + "\n"

                 
                    elif last_msg.content:
                        yield json.dumps({
                            "type": "content",
                            "text": last_msg.content
                        }) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")