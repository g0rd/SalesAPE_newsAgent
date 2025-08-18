import { useState, useEffect, useRef } from 'react';
import Head from 'next/head';
import ChatInterface from '../components/ChatInterface';
import PreferenceChecklist from '../components/PreferenceChecklist';
import styles from '../styles/Home.module.css';

export default function Home() {
  const [userPreferences, setUserPreferences] = useState({
    tone_of_voice: '',
    response_format: '',
    language_preference: '',
    interaction_style: '',
    news_topics: ''
  });

  const [preferencesCompleted, setPreferencesCompleted] = useState({
    tone_of_voice: false,
    response_format: false,
    language_preference: false,
    interaction_style: false,
    news_topics: false
  });

  const updatePreferences = (newPreferences: any) => {
    setUserPreferences(prev => ({ ...prev, ...newPreferences }));
  };

  const updatePreferencesCompleted = (newCompleted: any) => {
    setPreferencesCompleted(prev => ({ ...prev, ...newCompleted }));
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>SalesAPE News Agent</title>
        <meta name="description" content="AI-powered news agent with personalized preferences" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <h1 className={styles.title}>
          SalesAPE News Agent
        </h1>
        
        <div className={styles.content}>
          <div className={styles.preferencesSection}>
            <h2>Your Preferences</h2>
            <PreferenceChecklist 
              preferences={userPreferences}
              completed={preferencesCompleted}
            />
          </div>
          
          <div className={styles.chatSection}>
            <ChatInterface 
              userPreferences={userPreferences}
              preferencesCompleted={preferencesCompleted}
              updatePreferences={updatePreferences}
              updatePreferencesCompleted={updatePreferencesCompleted}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
