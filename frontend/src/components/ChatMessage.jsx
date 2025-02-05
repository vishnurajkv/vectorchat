import React from 'react';
import { MessageTypes } from '../utils/constants';

const ChatMessage = ({ message }) => {
  const getMessageStyles = () => {
    switch (message.type) {
      case MessageTypes.USER:
        return 'bg-blue-500 text-white';
      case MessageTypes.ERROR:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className={`flex flex-col ${message.type === MessageTypes.USER ? 'items-end' : 'items-start'}`}>
      <div className={`max-w-3/4 p-3 rounded-lg ${getMessageStyles()}`}>
        <p>{message.content}</p>
        {message.sources && (
          <div className="mt-2 text-sm text-gray-500">
            <p>Sources: {message.sources.join(', ')}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
