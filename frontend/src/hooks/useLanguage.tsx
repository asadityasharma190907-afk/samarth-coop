import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { en } from '../i18n/en';
import { hi } from '../i18n/hi';

type Language = 'en' | 'hi';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(() => {
    try {
      const saved =
        typeof window !== 'undefined' && window.localStorage
          ? localStorage.getItem('samarth_lang')
          : null;
      return saved === 'hi' ? 'hi' : 'en';
    } catch {
      return 'en';
    }
  });

  useEffect(() => {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.setItem('samarth_lang', language);
      }
    } catch {
      // Ignore errors in test environments
    }
  }, [language]);

  const t = (key: string) => {
    const keys = key.split('.');

    let result: any = language === 'hi' ? hi : en;
    for (const k of keys) {
      if (result === undefined) break;
      result = result[k];
    }
    return result || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    // Graceful fallback for test environments that don't wrap components in LanguageProvider
    return {
      language: 'en' as Language,
      setLanguage: () => {},
      t: (key: string) => {
        const keys = key.split('.');

        let result: any = en;
        for (const k of keys) {
          if (result === undefined) break;
          result = result[k as keyof typeof result];
        }
        return result || key;
      },
    };
  }
  return context;
}
