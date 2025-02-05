import React from 'react';
import ChatInterface from './components/ChatInterface';

const App = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-4xl mx-auto py-4 px-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Document Chat Assistant
          </h1>
        </div>
      </header>
      <main>
        <ChatInterface />
      </main>
    </div>
  );
};

export default App;
