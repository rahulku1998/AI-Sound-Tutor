import React, { useState } from "react";

function Chat({ topicId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input) return;
    const userMsg = { text: input, sender: "user" };
    setMessages([...messages, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input, topicId }),
      });
      const data = await res.json();
      const aiMsg = { text: data.answer, sender: "ai", image: data.image };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ minHeight: "300px", border: "1px solid #ccc", padding: "8px", overflowY: "auto" }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ textAlign: msg.sender === "user" ? "right" : "left", margin: "8px 0" }}>
            <div style={{ display: "inline-block", padding: "8px", borderRadius: "12px", background: msg.sender==="user"?"#4caf50":"#eee", color: msg.sender==="user"?"#fff":"#000" }}>
              {msg.text}
              {msg.image && <div><img src={`http://127.0.0.1:8000${msg.image}`} alt="AI Diagram" style={{maxWidth:"200px", marginTop:"4px"}}/></div>}
            </div>
          </div>
        ))}
      </div>
      <div style={{ display: "flex", marginTop: "8px" }}>
        <input style={{ flex: 1, padding: "8px" }} value={input} onChange={e => setInput(e.target.value)} placeholder="Ask something..." />
        <button onClick={sendMessage} disabled={loading} style={{ marginLeft: "8px" }}>
          {loading ? "Loading..." : "Send"}
        </button>
      </div>
    </div>
  );
}

export default Chat;
