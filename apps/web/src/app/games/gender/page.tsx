"use client";

import { useState, useEffect } from 'react';
import { AppLayout } from '@/components/AppLayout';
import { useVocabulary } from '@/hooks/use-vocabulary';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Brain, Trophy, XCircle, CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';

export default function GenderReflexGame() {
  const { vocabulary } = useVocabulary();
  const [gameState, setGameState] = useState<'start' | 'playing' | 'end'>('start');
  const [score, setScore] = useState(0);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [nouns, setNouns] = useState<any[]>([]);
  const [feedback, setFeedback] = useState<'correct' | 'wrong' | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    if (gameState === 'playing') {
      const allNouns = vocabulary.filter(v => v.pos === 'Noun' && v.gender);
      setNouns(allNouns.sort(() => Math.random() - 0.5).slice(0, 15));
      setScore(0);
      setCurrentIndex(0);
    }
  }, [gameState, vocabulary]);

  const handleChoice = (gender: string) => {
    const current = nouns[currentIndex];
    if (gender === current.gender) {
      setScore(s => s + 1);
      setFeedback('correct');
    } else {
      setFeedback('wrong');
    }

    setTimeout(() => {
      setFeedback(null);
      if (currentIndex < nouns.length - 1) {
        setCurrentIndex(i => i + 1);
      } else {
        setGameState('end');
      }
    }, 600);
  };

  if (gameState === 'start') {
    return (
      <AppLayout>
        <div className="max-w-xl mx-auto text-center pt-20">
          <Brain size={80} className="text-primary mx-auto mb-8 animate-bounce" />
          <h1 className="text-5xl font-headline font-bold mb-4">Der/Die/Das Reflex</h1>
          <p className="text-muted-foreground text-lg mb-12">Train your brain to recognize German noun genders instantly. Speed matters!</p>
          <Button size="lg" className="h-16 px-12 text-xl rounded-full" onClick={() => setGameState('playing')}>
            Start Training
          </Button>
        </div>
      </AppLayout>
    );
  }

  if (gameState === 'end') {
    return (
      <AppLayout>
        <div className="max-w-xl mx-auto text-center pt-20">
          <Trophy size={80} className="text-yellow-500 mx-auto mb-8" />
          <h1 className="text-4xl font-headline font-bold mb-2">Training Session Complete</h1>
          <p className="text-xl text-muted-foreground mb-8">Score: {score} / {nouns.length}</p>
          <div className="flex gap-4 justify-center">
            <Button size="lg" className="rounded-full" onClick={() => setGameState('playing')}>Play Again</Button>
            <Button size="lg" variant="outline" className="rounded-full" asChild><a href="/games">Back to Hub</a></Button>
          </div>
        </div>
      </AppLayout>
    );
  }

  const currentNoun = nouns[currentIndex];

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto">
        <header className="flex items-center justify-between mb-12">
          <div className="text-lg font-bold">Progress: {currentIndex + 1} / {nouns.length}</div>
          <div className="text-2xl font-headline font-bold text-primary">Score: {score}</div>
        </header>

        <Card className={cn(
          "h-64 flex flex-col items-center justify-center glass mb-12 relative overflow-hidden transition-all duration-300 border-4",
          feedback === 'correct' ? 'border-green-500 bg-green-500/10' : feedback === 'wrong' ? 'border-destructive bg-destructive/10' : 'border-transparent'
        )}>
          {feedback === 'correct' && <CheckCircle className="absolute top-4 right-4 text-green-500 animate-in zoom-in" size={48} />}
          {feedback === 'wrong' && <XCircle className="absolute top-4 right-4 text-destructive animate-in zoom-in" size={48} />}
          
          <h2 className="text-6xl font-bold mb-4">{currentNoun?.word}</h2>
          <p className="text-xl text-muted-foreground">{currentNoun?.meaning}</p>
        </Card>

        <div className="grid grid-cols-3 gap-6">
          {[
            { g: 'der', color: 'bg-blue-600 hover:bg-blue-500 shadow-blue-500/20' },
            { g: 'die', color: 'bg-pink-600 hover:bg-pink-500 shadow-pink-500/20' },
            { g: 'das', color: 'bg-green-600 hover:bg-green-500 shadow-green-500/20' }
          ].map(btn => (
            <Button
              key={btn.g}
              className={cn("h-24 text-3xl font-headline font-bold rounded-2xl shadow-lg transition-transform active:scale-95 disabled:opacity-50", btn.color)}
              onClick={() => handleChoice(btn.g)}
              disabled={feedback !== null}
            >
              {btn.g}
            </Button>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
