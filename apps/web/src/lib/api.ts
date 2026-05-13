const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
const USER_ID_STORAGE_KEY = 'wortmeister_user_id';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const text = await response.text();
    let message = text;
    try {
      const payload = JSON.parse(text) as { detail?: string };
      message = payload.detail || message;
    } catch {
      // Keep the raw response text when the server does not return JSON.
    }
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

function userHeaders(): HeadersInit {
  return { 'X-User-Id': getUserId() };
}

function getUserId(): string {
  if (typeof window === 'undefined') return 'server-render';

  const existingUserId = window.localStorage.getItem(USER_ID_STORAGE_KEY);
  if (existingUserId) return existingUserId;

  const generatedUserId = `user_${generateClientId()}`;
  window.localStorage.setItem(USER_ID_STORAGE_KEY, generatedUserId);
  return generatedUserId;
}

function generateClientId(): string {
  const randomUuid = window.crypto?.randomUUID?.();
  if (randomUuid) return randomUuid.replaceAll('-', '');

  const bytes = new Uint8Array(16);
  window.crypto?.getRandomValues?.(bytes);
  if (bytes.some((byte) => byte !== 0)) {
    return Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('');
  }

  return `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 18)}`;
}

export type FlashcardResponse = {
  word: string;
  meaning: string;
  meaning_en: string;
  example: string;
  translation: string;
  level: string;
  interval: number;
  repetitions: number;
  easiness: number;
  due: number;
};

export type UpdateCardResponse = {
  success: boolean;
  word: string;
  new_interval: number;
  new_due: string;
  message: string;
};

export type SRSStatsResponse = {
  total_cards: number;
  due_cards: number;
  learned_cards: number;
  next_due: number | null;
  current_streak_days: number;
  longest_streak_days: number;
  last_activity_date: string | null;
  streak_last_7_days: boolean[];
};

export type NotebookEntry = {
  word: string;
  meaning: string;
  meaning_en: string;
  example: string;
  article: string;
  pos: string;
  image_url: string;
  image_source: string;
  created_at: string;
};

export type NotebookListResponse = {
  entries: NotebookEntry[];
};

export type NotebookUpsertRequest = {
  word: string;
  meaning: string;
  meaning_en?: string;
  example?: string;
  article?: string;
  image_url?: string;
};

export type MazePositionPayload = {
  row: number;
  col: number;
};

export type MazeCellPayload = {
  row: number;
  col: number;
  kind: string;
  letter: string;
};

export type MazeSessionResponse = {
  session_id: string;
  target_word: string;
  collected_letters: string[];
  remaining_letters: string[];
  player_position: MazePositionPayload;
  cells: MazeCellPayload[][];
  status: string;
  steps_taken: number;
  shortest_goal_distance: number | null;
  next_target_letter: string;
  next_target_position: MazePositionPayload | null;
  next_target_distance: number | null;
  next_target_path: MazePositionPayload[];
};

export type MazeMoveResponse = {
  moved: boolean;
  hit_wall: boolean;
  collected_letter: string;
  completed: boolean;
  state: MazeSessionResponse;
  message: string;
};

export function getSrsStats() {
  return request<SRSStatsResponse>('/api/srs/stats', {
    headers: userHeaders(),
  });
}

export function getNextCard(lang = 'vi') {
  return request<FlashcardResponse>(`/api/next-card?lang=${encodeURIComponent(lang)}`, {
    headers: userHeaders(),
  });
}

export function updateCard(word: string, quality: number) {
  return request<UpdateCardResponse>('/api/update-card', {
    method: 'POST',
    headers: userHeaders(),
    body: JSON.stringify({ word, quality }),
  });
}

export function getNotebookEntries() {
  return request<NotebookListResponse>('/api/notebook', {
    headers: userHeaders(),
  });
}

export function createNotebookEntry(entry: NotebookUpsertRequest) {
  return request<NotebookEntry>('/api/notebook', {
    method: 'POST',
    headers: userHeaders(),
    body: JSON.stringify(entry),
  });
}

export function updateNotebookEntry(word: string, entry: NotebookUpsertRequest) {
  return request<NotebookEntry>(`/api/notebook/${encodeURIComponent(word)}`, {
    method: 'PUT',
    headers: userHeaders(),
    body: JSON.stringify(entry),
  });
}

export function deleteNotebookEntry(word: string) {
  return request<{ success: boolean; word: string }>(`/api/notebook/${encodeURIComponent(word)}`, {
    method: 'DELETE',
    headers: userHeaders(),
  });
}

export function startMaze(targetWord: string) {
  return request<MazeSessionResponse>('/api/maze/start', {
    method: 'POST',
    body: JSON.stringify({ target_word: targetWord }),
  });
}

export function getMazeSession(sessionId: string) {
  return request<MazeSessionResponse>(`/api/maze/${encodeURIComponent(sessionId)}`);
}

export function moveMaze(sessionId: string, direction: 'up' | 'down' | 'left' | 'right') {
  return request<MazeMoveResponse>(`/api/maze/${sessionId}/move`, {
    method: 'POST',
    body: JSON.stringify({ direction }),
  });
}

export function getAudioUrl(word: string) {
  return `${API_BASE_URL}/api/audio?word=${encodeURIComponent(word)}`;
}
