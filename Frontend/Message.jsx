import React from "react";

function Message({ text, sender }) {
  const isUser = sender === "user";
  return (
    <div style={{ textAlign: isUser ? "right" : "left", margin: "8px 0" }}>
      <span
        style={{
          display: "inline-block",
          padding: "8px 12px",
          borderRadius: "12px",
          backgroundColor: isUser ? "#4caf50" : "#eee",
          color: isUser ? "#fff" : "#000",
        }}
      >
        {text}
      </span>
    </div>
  );
}

export default Message;
