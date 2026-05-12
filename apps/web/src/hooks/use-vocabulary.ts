import { useState, useEffect } from 'react';
import { VocabularyEntry, STATIC_VOCABULARY, INITIAL_EASE_FACTOR } from '@/lib/vocabulary';
import { calculateNextReview } from '@/lib/spaced-repetition';

const STORAGE_KEY = 'wortmeister_user_vocab';

export function useVocabulary() {
  const [vocabulary, setVocabulary] = useState<VocabularyEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        setVocabulary(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to parse vocabulary', e);
        initializeDefault();
      }
    } else {
      initializeDefault();
    }
    setIsLoading(false);
  }, []);

  const initializeDefault = () => {
    const initial = STATIC_VOCABULARY.map(v => ({
      ...v,
      interval: 0,
      repetitions: 0,
      easeFactor: INITIAL_EASE_FACTOR,
    }));
    setVocabulary(initial);
    save(initial);
  };

  const save = (data: VocabularyEntry[]) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  };

  const addWord = (entry: Omit<VocabularyEntry, 'interval' | 'repetitions' | 'easeFactor'>) => {
    const newEntry: VocabularyEntry = {
      ...entry,
      interval: 0,
      repetitions: 0,
      easeFactor: INITIAL_EASE_FACTOR,
    };
    const updated = [...vocabulary, newEntry];
    setVocabulary(updated);
    save(updated);
  };

  const updateReview = (id: string, quality: number) => {
    const updated = vocabulary.map(v => {
      if (v.id === id) {
        return calculateNextReview(v, quality);
      }
      return v;
    });
    setVocabulary(updated);
    save(updated);
  };

  const deleteWord = (id: string) => {
    const updated = vocabulary.filter(v => v.id !== id);
    setVocabulary(updated);
    save(updated);
  };

  return {
    vocabulary,
    addWord,
    updateReview,
    deleteWord,
    isLoading,
  };
}
