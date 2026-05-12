export type GermanGender = 'der' | 'die' | 'das';

export interface VocabularyEntry {
  id: string;
  word: string;
  meaning: string;
  gender?: GermanGender;
  plural?: string;
  pos: string; // Part of Speech
  level: 'A1' | 'A2' | 'B1';
  imageUrl?: string;
  examples?: string[];
  
  // SRS properties
  lastReviewed?: number;
  interval: number; // in days
  easeFactor: number;
  repetitions: number;
}

export const INITIAL_EASE_FACTOR = 2.5;

export const STATIC_VOCABULARY: Omit<VocabularyEntry, 'lastReviewed' | 'interval' | 'easeFactor' | 'repetitions'>[] = [
  { id: '1', word: 'Hund', meaning: 'Dog', gender: 'der', plural: 'Hunde', pos: 'Noun', level: 'A1' },
  { id: '2', word: 'Katze', meaning: 'Cat', gender: 'die', plural: 'Katzen', pos: 'Noun', level: 'A1' },
  { id: '3', word: 'Haus', meaning: 'House', gender: 'das', plural: 'Häuser', pos: 'Noun', level: 'A1' },
  { id: '4', word: 'essen', meaning: 'to eat', pos: 'Verb', level: 'A1' },
  { id: '5', word: 'trinken', meaning: 'to drink', pos: 'Verb', level: 'A1' },
  { id: '6', word: 'schnell', meaning: 'fast', pos: 'Adjective', level: 'A1' },
  { id: '7', word: 'langsam', meaning: 'slow', pos: 'Adjective', level: 'A1' },
  { id: '8', word: 'Wasser', meaning: 'Water', gender: 'das', plural: 'Wässer', pos: 'Noun', level: 'A1' },
  { id: '9', word: 'Apfel', meaning: 'Apple', gender: 'der', plural: 'Äpfel', pos: 'Noun', level: 'A1' },
  { id: '10', word: 'Buch', meaning: 'Book', gender: 'das', plural: 'Bücher', pos: 'Noun', level: 'A1' },
  { id: '11', word: 'lernen', meaning: 'to learn', pos: 'Verb', level: 'A1' },
  { id: '12', word: 'sprechen', meaning: 'to speak', pos: 'Verb', level: 'A1' },
  { id: '13', word: 'schön', meaning: 'beautiful', pos: 'Adjective', level: 'A1' },
  { id: '14', word: 'hässlich', meaning: 'ugly', pos: 'Adjective', level: 'A1' },
  { id: '15', word: 'Tisch', meaning: 'Table', gender: 'der', plural: 'Tische', pos: 'Noun', level: 'A1' },
];

export function getFullWordDisplay(entry: VocabularyEntry | Partial<VocabularyEntry>) {
  if (entry.pos === 'Noun' && entry.gender) {
    return `${entry.gender} ${entry.word}${entry.plural ? ` (Pl. ${entry.plural})` : ''}`;
  }
  return entry.word;
}
