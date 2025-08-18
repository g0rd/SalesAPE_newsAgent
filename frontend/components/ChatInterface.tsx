import { useState, useRef, useEffect } from 'react';
import styles from '../styles/ChatInterface.module.css';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatInterfaceProps {
  userPreferences: any;
  preferencesCompleted: any;
  updatePreferences: (prefs: any) => void;
  updatePreferencesCompleted: (completed: any) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  userPreferences,
  preferencesCompleted,
  updatePreferences,
  updatePreferencesCompleted
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize chat with welcome message
  useEffect(() => {
    if (messages.length === 0) {
      sendMessage('');
    }
  }, []);

  const sendMessage = async (message: string = '') => {
    if (message.trim() === '' && messages.length > 0) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: message || 'Hello'
    };

    // Add user message to chat
    if (message.trim() !== '') {
      setMessages(prev => [...prev, userMessage]);
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message || 'Hello',
          conversation_history: messages,
          user_preferences: userPreferences
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Add AI response to chat
      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: data.response
      };
      
      setMessages(prev => [...prev, aiMessage]);

      // Update preferences completion status
      if (data.preferences_completed) {
        updatePreferencesCompleted(data.preferences_completed);
      }

      // Extract and update user preferences from the conversation
      extractPreferencesFromMessage(message);

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const extractPreferencesFromMessage = (message: string) => {
    const messageLower = message.toLowerCase();
    const newPreferences: any = {};

    // Extract tone preferences
    if (messageLower.includes('tone') || messageLower.includes('formal') || messageLower.includes('casual') || messageLower.includes('enthusiastic')) {
      if (messageLower.includes('formal')) {
        newPreferences.tone_of_voice = 'formal';
      } else if (messageLower.includes('casual')) {
        newPreferences.tone_of_voice = 'casual';
      } else if (messageLower.includes('enthusiastic')) {
        newPreferences.tone_of_voice = 'enthusiastic';
      }
    }

    // Extract format preferences
    if (messageLower.includes('format') || messageLower.includes('bullet') || messageLower.includes('paragraph')) {
      if (messageLower.includes('bullet')) {
        newPreferences.response_format = 'bullet points';
      } else if (messageLower.includes('paragraph')) {
        newPreferences.response_format = 'paragraphs';
      }
    }

    // Extract language preferences
    if (messageLower.includes('language') || messageLower.includes('english') || messageLower.includes('spanish')) {
      if (messageLower.includes('english')) {
        newPreferences.language_preference = 'English';
      } else if (messageLower.includes('spanish')) {
        newPreferences.language_preference = 'Spanish';
      }
    }

    // Extract interaction style preferences
    if (messageLower.includes('style') || messageLower.includes('concise') || messageLower.includes('detailed')) {
      if (messageLower.includes('concise')) {
        newPreferences.interaction_style = 'concise';
      } else if (messageLower.includes('detailed')) {
        newPreferences.interaction_style = 'detailed';
      }
    }

    // Extract news topic preferences
    if (messageLower.includes('topic') || messageLower.includes('technology') || messageLower.includes('sports') || messageLower.includes('politics')) {
      const topics = [];
      if (messageLower.includes('technology')) topics.push('technology');
      if (messageLower.includes('sports')) topics.push('sports');
      if (messageLower.includes('politics')) topics.push('politics');
      if (messageLower.includes('business')) topics.push('business');
      if (messageLower.includes('entertainment')) topics.push('entertainment');
      
      if (topics.length > 0) {
        newPreferences.news_topics = topics.join(', ');
      }
    }

    // Update preferences if any were found
    if (Object.keys(newPreferences).length > 0) {
      updatePreferences(newPreferences);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputMessage.trim() && !isLoading) {
      sendMessage(inputMessage);
      setInputMessage('');
    }
  };

  return (
    <div className={styles.chatContainer}>
      <div className={styles.chatHeader}>
        <h3>Chat with AI News Agent</h3>
      </div>
      
      <div className={styles.messagesContainer}>
        {messages.map((message, index) => (
          <div
            key={index}
            className={`${styles.message} ${
              message.role === 'user' ? styles.userMessage : styles.aiMessage
            }`}
          >
            <div className={styles.messageContent}>
              {message.content}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className={`${styles.message} ${styles.aiMessage}`}>
            <div className={styles.messageContent}>
              <div className={styles.typingIndicator}>
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className={styles.inputForm}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type your message here..."
          disabled={isLoading}
          className={styles.messageInput}
        />
        <button
          type="submit"
          disabled={isLoading || !inputMessage.trim()}
          className={styles.sendButton}
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;
