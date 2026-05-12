"use client";

import { useState, useEffect, useCallback } from 'react';
import { AppLayout } from '@/components/AppLayout';
import { useVocabulary } from '@/hooks/use-vocabulary';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { moveMaze, startMaze, type MazeSessionResponse } from '@/lib/api';
import { Trophy, ArrowBigUp, ArrowBigDown, ArrowBigLeft, ArrowBigRight } from 'lucide-react';

export default function VocabularyMaze() {
  const { vocabulary } = useVocabulary();
  const [gameStatus, setGameStatus] = useState<'start' | 'playing' | 'won'>('start');
  const [mazeSession, setMazeSession] = useState<MazeSessionResponse | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const [error, setError] = useState('');

  const initGame = useCallback(async () => {
    const randomWord = vocabulary[Math.floor(Math.random() * vocabulary.length)]?.word;
    if (!randomWord) {
      setError('Add vocabulary before starting the maze.');
      return;
    }

    setIsBusy(true);
    setError('');
    try {
      const session = await startMaze(randomWord);
      setMazeSession(session);
      setGameStatus(session.status === 'completed' ? 'won' : 'playing');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to start maze.');
    } finally {
      setIsBusy(false);
    }
  }, [vocabulary]);

  const move = useCallback(async (direction: 'up' | 'down' | 'left' | 'right') => {
    if (!mazeSession || gameStatus !== 'playing' || isBusy) return;

    setIsBusy(true);
    setError('');
    try {
      const response = await moveMaze(mazeSession.session_id, direction);
      setMazeSession(response.state);
      if (response.completed || response.state.status === 'completed') {
        setGameStatus('won');
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to move.');
    } finally {
      setIsBusy(false);
    }
  }, [gameStatus, isBusy, mazeSession]);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (gameStatus !== 'playing') return;
      if (e.key === 'ArrowUp') void move('up');
      if (e.key === 'ArrowDown') void move('down');
      if (e.key === 'ArrowLeft') void move('left');
      if (e.key === 'ArrowRight') void move('right');
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [gameStatus, move]);

  const targetWord = mazeSession?.target_word ?? '';
  const collectedChars = mazeSession?.collected_letters.join('') ?? '';
  const gridSize = mazeSession?.cells.length ?? 0;

  if (gameStatus === 'start') {
    return (
      <AppLayout>
        <div className="max-w-xl mx-auto text-center pt-20">
          <h1 className="text-5xl font-headline font-bold mb-4">Vocabulary Maze</h1>
          <p className="text-muted-foreground text-lg mb-12">Navigate the grid and collect letters in the correct order to spell the target word.</p>
          {error && <p className="text-destructive text-sm mb-6">{error}</p>}
          <Button size="lg" className="h-16 px-12 text-xl rounded-full" onClick={initGame} disabled={isBusy}>
            {isBusy ? 'Starting...' : 'Start Maze'}
          </Button>
        </div>
      </AppLayout>
    );
  }

  if (gameStatus === 'won') {
    return (
      <AppLayout>
        <div className="max-w-xl mx-auto text-center pt-20">
          <Trophy size={80} className="text-yellow-500 mx-auto mb-8" />
          <h1 className="text-4xl font-headline font-bold mb-2">Word Completed!</h1>
          <p className="text-3xl text-primary font-bold mb-8">{targetWord}</p>
          {error && <p className="text-destructive text-sm mb-6">{error}</p>}
          <div className="flex gap-4 justify-center">
            <Button size="lg" className="rounded-full" onClick={initGame} disabled={isBusy}>{isBusy ? 'Loading...' : 'Next Word'}</Button>
            <Button size="lg" variant="outline" className="rounded-full" asChild><a href="/games">Back to Hub</a></Button>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto flex gap-12">
        <div className="flex-1">
          <header className="mb-8">
            <h1 className="text-2xl font-bold text-muted-foreground uppercase tracking-widest">Spelling Target:</h1>
            <div className="flex gap-2 mt-2">
              {targetWord.split('').map((char, i) => (
                <div key={i} className={cn(
                  "h-12 w-12 rounded-lg border-2 flex items-center justify-center text-2xl font-bold",
                  i < collectedChars.length ? "border-primary bg-primary text-white" : "border-border text-muted-foreground"
                )}>
                  {i < collectedChars.length ? char : ''}
                </div>
              ))}
            </div>
            {error && <p className="text-destructive text-sm mt-4">{error}</p>}
          </header>

          <div
            className="grid gap-1 bg-secondary/30 p-2 rounded-xl border border-border"
            style={{ gridTemplateColumns: `repeat(${gridSize}, 1fr)` }}
          >
            {mazeSession?.cells.flat().map((cell) => {
              const isPlayer = mazeSession.player_position.row === cell.row && mazeSession.player_position.col === cell.col;
              const isWall = cell.kind === 'wall';
              const hasLetter = cell.kind === 'goal' && cell.letter;

              return (
                <div
                  key={`${cell.row}-${cell.col}`}
                  className={cn(
                    "aspect-square rounded-md flex items-center justify-center text-lg font-bold transition-all duration-200",
                    isPlayer ? "bg-primary scale-110 shadow-lg z-10" : isWall ? "bg-secondary" : "bg-card/50"
                  )}
                >
                  {isPlayer ? "P" : hasLetter ? cell.letter : ""}
                </div>
              );
            })}
          </div>
        </div>

        <aside className="w-64 space-y-8 flex flex-col justify-center">
          <div className="bg-card p-6 rounded-2xl border border-border">
            <h3 className="text-xs uppercase font-bold text-muted-foreground mb-4">Controls</h3>
            <div className="grid grid-cols-3 gap-2">
              <div />
              <Button size="icon" onClick={() => move('up')} disabled={isBusy}><ArrowBigUp /></Button>
              <div />
              <Button size="icon" onClick={() => move('left')} disabled={isBusy}><ArrowBigLeft /></Button>
              <Button size="icon" onClick={() => move('down')} disabled={isBusy}><ArrowBigDown /></Button>
              <Button size="icon" onClick={() => move('right')} disabled={isBusy}><ArrowBigRight /></Button>
            </div>
            <p className="text-[10px] text-muted-foreground mt-4 text-center">Use Arrow keys or buttons to move</p>
          </div>

          <div className="bg-primary/5 p-6 rounded-2xl border border-primary/20">
             <h3 className="text-xs uppercase font-bold text-primary mb-2">Instructions</h3>
             <p className="text-xs text-muted-foreground leading-relaxed">
               Collect letters in the order they appear in the word. Incorrect letters won't be collected.
             </p>
          </div>
        </aside>
      </div>
    </AppLayout>
  );
}
