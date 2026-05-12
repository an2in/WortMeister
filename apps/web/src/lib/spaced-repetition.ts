import { VocabularyEntry, INITIAL_EASE_FACTOR } from './vocabulary';

export function calculateNextReview(
  entry: VocabularyEntry,
  quality: number // 0-5
): VocabularyEntry {
  let { interval, repetitions, easeFactor } = entry;

  if (quality >= 3) {
    // Correct response
    if (repetitions === 0) {
      interval = 1;
    } else if (repetitions === 1) {
      interval = 6;
    } else {
      interval = Math.round(interval * easeFactor);
    }
    repetitions++;
  } else {
    // Incorrect response
    repetitions = 0;
    interval = 1;
  }

  // Adjust ease factor
  easeFactor = easeFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02));
  if (easeFactor < 1.3) easeFactor = 1.3;

  return {
    ...entry,
    interval,
    repetitions,
    easeFactor,
    lastReviewed: Date.now(),
  };
}

export function isDue(entry: VocabularyEntry): boolean {
  if (!entry.lastReviewed) return true;
  const now = Date.now();
  const diffInDays = (now - entry.lastReviewed) / (1000 * 60 * 60 * 24);
  return diffInDays >= entry.interval;
}
