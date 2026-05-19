import type { NotebookEntry } from './api';

const SRS_CARDS_KEY = 'wortmeister_srs_cards';
const ACTIVITY_DATES_KEY = 'wortmeister_activity_dates';
const NOTEBOOK_ENTRIES_KEY = 'wortmeister_notebook_entries';

export type LocalReviewCard = {
  interval: number;
  repetitions: number;
  easiness: number;
  due: number;
};

export type LocalSrsCards = Record<string, LocalReviewCard>;

function readJson<T>(key: string, fallback: T): T {
  if (typeof window === 'undefined') return fallback;

  const rawValue = window.localStorage.getItem(key);
  if (!rawValue) return fallback;

  try {
    return JSON.parse(rawValue) as T;
  } catch {
    return fallback;
  }
}

function writeJson<T>(key: string, value: T): void {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(key, JSON.stringify(value));
}

export function loadSrsCards(): LocalSrsCards {
  return readJson<LocalSrsCards>(SRS_CARDS_KEY, {});
}

export function saveSrsCards(cards: LocalSrsCards): void {
  writeJson(SRS_CARDS_KEY, cards);
}

export function loadActivityDates(): string[] {
  return readJson<string[]>(ACTIVITY_DATES_KEY, []);
}

export function saveActivityDates(activityDates: string[]): void {
  writeJson(ACTIVITY_DATES_KEY, activityDates);
}

export function recordActivityDate(activityDate = new Date().toISOString().slice(0, 10)): string[] {
  const dates = new Set(loadActivityDates());
  dates.add(activityDate);
  const activityDates = Array.from(dates).sort();
  saveActivityDates(activityDates);
  return activityDates;
}

export function loadNotebookEntries(): NotebookEntry[] {
  return readJson<NotebookEntry[]>(NOTEBOOK_ENTRIES_KEY, []);
}

export function saveNotebookEntries(entries: NotebookEntry[]): void {
  writeJson(NOTEBOOK_ENTRIES_KEY, entries);
}
