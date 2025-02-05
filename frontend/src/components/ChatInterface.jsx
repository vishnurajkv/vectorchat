import React, { useState } from 'react';
import FileUpload from './FileUpload';
import ChatMessage from './ChatMessage';
import { uploadFile, sendMessage } from '../services/api';
import { MessageTypes } from '../utils/constants';

const ChatInterface = () => {
  const [sessionId, set
