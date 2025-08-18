import React from 'react';
import styles from '../styles/PreferenceChecklist.module.css';

interface PreferenceChecklistProps {
  preferences: {
    tone_of_voice: string;
    response_format: string;
    language_preference: string;
    interaction_style: string;
    news_topics: string;
  };
  completed: {
    tone_of_voice: boolean;
    response_format: boolean;
    language_preference: boolean;
    interaction_style: boolean;
    news_topics: boolean;
  };
}

const PreferenceChecklist: React.FC<PreferenceChecklistProps> = ({ preferences, completed }) => {
  const preferenceItems = [
    {
      key: 'tone_of_voice',
      label: 'Preferred Tone of Voice',
      description: 'e.g., formal, casual, enthusiastic',
      value: preferences.tone_of_voice
    },
    {
      key: 'response_format',
      label: 'Preferred Response Format',
      description: 'e.g., bullet points, paragraphs',
      value: preferences.response_format
    },
    {
      key: 'language_preference',
      label: 'Language Preference',
      description: 'e.g., English, Spanish',
      value: preferences.language_preference
    },
    {
      key: 'interaction_style',
      label: 'Interaction Style',
      description: 'e.g., concise, detailed',
      value: preferences.interaction_style
    },
    {
      key: 'news_topics',
      label: 'Preferred News Topics',
      description: 'e.g., technology, sports, politics',
      value: preferences.news_topics
    }
  ];

  return (
    <div className={styles.checklistContainer}>
      <div className={styles.checklistHeader}>
        <h3>Preference Collection Progress</h3>
        <p>Complete these preferences to personalize your news experience</p>
      </div>
      
      <div className={styles.checklistItems}>
        {preferenceItems.map((item) => (
          <div
            key={item.key}
            className={`${styles.checklistItem} ${
              completed[item.key as keyof typeof completed] ? styles.completed : styles.pending
            }`}
          >
            <div className={styles.checkboxContainer}>
              <div className={styles.checkbox}>
                {completed[item.key as keyof typeof completed] ? (
                  <span className={styles.checkmark}>✓</span>
                ) : (
                  <span className={styles.pendingMark}>○</span>
                )}
              </div>
            </div>
            
            <div className={styles.itemContent}>
              <div className={styles.itemLabel}>
                {item.label}
              </div>
              <div className={styles.itemDescription}>
                {item.description}
              </div>
              {completed[item.key as keyof typeof completed] && (
                <div className={styles.itemValue}>
                  <strong>Your choice:</strong> {item.value}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      
      <div className={styles.progressBar}>
        <div className={styles.progressText}>
          {Object.values(completed).filter(Boolean).length} of 5 preferences completed
        </div>
        <div className={styles.progressBarContainer}>
          <div 
            className={styles.progressBarFill}
            style={{ 
              width: `${(Object.values(completed).filter(Boolean).length / 5) * 100}%` 
            }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default PreferenceChecklist;
