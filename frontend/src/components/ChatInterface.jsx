import React, { useState } from 'react';
import FileUpload from './FileUpload';
import ChatMessage from './ChatMessage';
import { uploadFile, sendMessage } from '../services/api';
import { MessageTypes } from '../utils/constants';

const ChatInterface = () => {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleFileUpload = async (file) => {
    setUploading(true);
    try {
      const { session_id } = await uploadFile(file);
      setSessionId(session_id);
      setMessages([{ 
        type: MessageTypes.SYSTEM, 
        content: 'PDF uploaded successfully! You can now ask questions about the document.' 
      }]);
    } catch (error) {
      setMessages([{ 
        type: MessageTypes.ERROR, 
        content: error.message || 'Failed to upload PDF. Please try again.' 
      }]);
    } finally {
      setUploading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !sessionId || loading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setMessages(prev => [...prev, { type: MessageTypes.USER, content: userMessage }]);
    setLoading(true);

    try {
      const chatHistory = messages
        .filter(m => m.type === MessageTypes.USER || m.type === MessageTypes.ASSISTANT)
        .map(m => [m.content, '']);

      const { answer, sources } = await sendMessage(userMessage, chatHistory, sessionId);
      setMessages(prev => [...prev, {
        type: MessageTypes.ASSISTANT,
        content: answer,
        sources
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        type: MessageTypes.ERROR,
        content: error.message || 'Failed to get response. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      <div className="mb-4">
        <FileUpload onUpload={handleFileUpload} isUploading={uploading} />
      </div>

      <div className="flex-1 overflow-auto bg-white rounded-lg shadow mb-4">
        <div className="p-4 space-y-4">
          {messages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}
          {loading && (
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100" />
              <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200" />
            </div>
          )}
        </div>
      </div>

      <div className="flex space-x-2">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Ask a question about your document..."
          className="flex-1 p-2 border rounded-lg"
          disabled={!sessionId || loading}
        />
        <button
          onClick={handleSendMessage}
          disabled={!sessionId || loading || !inputMessage.trim()}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg disabled:bg-gray-300"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
