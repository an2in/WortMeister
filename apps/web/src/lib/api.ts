const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
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
};

export type MazeMoveResponse = {
  moved: boolean;
  hit_wall: boolean;
  collected_letter: string;
  completed: boolean;
  state: MazeSessionResponse;
};

export function getNextCard(lang = 'vi') {
  return request<FlashcardResponse>(`/api/next-card?lang=${encodeURIComponent(lang)}`);
}

export function updateCard(word: string, quality: number) {
  return request<UpdateCardResponse>('/api/update-card', {
    method: 'POST',
    body: JSON.stringify({ word, quality }),
  });
}

export function startMaze(targetWord: string) {
  return request<MazeSessionResponse>('/api/maze/start', {
    method: 'POST',
    body: JSON.stringify({ target_word: targetWord }),
  });
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
