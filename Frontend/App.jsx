import React, { useState } from "react";
import Chat from "./components/Chat.jsx";
import PdfUpload from "./components/PdfUpload.jsx";

function App() {
  const [topicId, setTopicId] = useState("");

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto" }}>
      <h1>AI PDF Chat</h1>
      <PdfUpload onUpload={(id) => setTopicId(id)} />
      {topicId && <Chat topicId={topicId} />}
    </div>
  );
}

export default App;
