import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from models import ChatRequest 
from graph import agent

app = FastAPI(title="Stock Analysis Agent")


origins = [
    "https://stock-analysis-frontend-9nry.onrender.com", 
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # Prepare the messages for LangGraph
    input_messages = []
    for msg in request.messages:
        if msg["role"] == "user":
            input_messages.append(HumanMessage(content=msg["content"]))
        else:
            input_messages.append(AIMessage(content=msg["content"]))

    config = {"configurable": {"thread_id": request.thread_id}}

    async def event_generator():
        try:
            async for chunk in agent.astream({"messages": input_messages}, config=config, stream_mode="updates"):
                for node_name, node_update in chunk.items():
                    if "messages" in node_update:
                        last_msg = node_update["messages"][-1]
                        
                        # 1. Tool Call (The "Thinking" phase)
                        if getattr(last_msg, "tool_calls", None):
                            yield json.dumps({
                                "type": "tool_call", 
                                "node": node_name, 
                                "calls": last_msg.tool_calls
                            }) + "\n"

                        # 2. Tool Output (The "Data" phase)
                        elif isinstance(last_msg, ToolMessage):
                            yield json.dumps({
                                "type": "tool_output",
                                "tool": last_msg.name,
                                "output": str(last_msg.content)[:1500] 
                            }) + "\n"

                        # 3. Final Content (The "Answering" phase)
                        elif last_msg.content:
                            yield json.dumps({
                                "type": "content", 
                                "text": last_msg.content
                            }) + "\n"
        except Exception as e:
            yield json.dumps({"type": "error", "text": str(e)}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")