import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { v4 as uuidv4 } from 'uuid'; 
import remarkGfm from 'remark-gfm';
import './Agent.css';

const Agent = () => {

    const [messages, setMessages] = useState([]);
    const [currentResearch, setCurrentResearch] = useState([]);
    const [input, setInput] = useState("");
    const [isStreaming, setIsStreaming] = useState(false);
    
    const [threadId, setThreadId] = useState(""); 
    const scrollRef = useRef(null);

   
    useEffect(() => {
        const newThreadId = `thread_${uuidv4()}`;
        setThreadId(newThreadId);
        console.log("Session Started with Thread ID:", newThreadId);
    }, []);


    useEffect(() => {
        scrollRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, currentResearch]);


    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim() || isStreaming) return;

        const userMsg = { role: "user", content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput("");
        setIsStreaming(true);
        setCurrentResearch([]); 
        
        let aiResponse = "";
        

        try {
            
            const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
            
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    messages: [...messages, userMsg], 
                    thread_id: threadId 
                })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let lineBuffer = ""; 

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                lineBuffer += decoder.decode(value, { stream: true });
                const lines = lineBuffer.split("\n");
                lineBuffer = lines.pop(); 

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const data = JSON.parse(line);
                        
                        if (data.type === "tool_call") {
                            setCurrentResearch(prev => [...prev, { 
                                type: 'call', 
                                name: data.calls[0]?.name || "tool" 
                            }]);
                        } 
                        else if (data.type === "tool_output") {
                            setCurrentResearch(prev => [...prev, { 
                                type: 'output', 
                                name: data.tool, 
                                data: data.output 
                            }]);
                        } 
                        else if (data.type === "content") {
                            aiResponse += data.text;
                            setMessages(prev => {
                                const last = prev[prev.length - 1];
                                return last?.role === "assistant" 
                                    ? [...prev.slice(0, -1), { ...last, content: aiResponse }]
                                    : [...prev, { role: "assistant", content: aiResponse }];
                            });
                        }
                    } catch (err) {
                        console.error("JSON Parse error on line:", line);
                    }
                }
            }
        } catch (e) { 
            console.error("Stream error:", e); 
        } finally { 
            setIsStreaming(false); 
        }
    };

    return (
        <div className="gemini-container">
            <div className="chat-area">
                {messages.map((m, i) => (
                    <div key={i} className={`msg-wrapper ${m.role}`}>
                        <div className="msg-content">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                        </div>
                    </div>
                ))}
                
                {currentResearch.length > 0 && (
                    <div className="research-stream">
                        {currentResearch.map((res, i) => (
                            <details key={i} className="research-card" open={res.type === 'output'}>
                                <summary>
                                    <span className="sparkle">✨</span> 
                                    {res.type === 'call' ? `Agent thinking: ${res.name}...` : `Data received from ${res.name}`}
                                </summary>
                                {res.data && <pre className="raw-data">{res.data}</pre>}
                            </details>
                        ))}
                    </div>
                )}
                <div ref={scrollRef} style={{ height: "20px" }} />
            </div>

            <div className="input-container">
                <form onSubmit={handleSubmit} className="gemini-input-bar">
                    <input 
                        value={input} 
                        onChange={e => setInput(e.target.value)}
                        placeholder="Analyze stocks or market trends..."
                        disabled={isStreaming}
                    />
                    <button type="submit" disabled={isStreaming || !input.trim()}>
                        {isStreaming ? "..." : "↑"}
                    </button>
                </form>
            </div>
        </div>
    );
};
export default Agent;

