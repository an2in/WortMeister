"use client";

import { useCallback, useEffect, useState } from 'react';
import { AppLayout } from '@/components/AppLayout';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Volume2,
  RotateCcw,
  CheckCircle,
  XCircle,
  HelpCircle,
  Trophy
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { getAudioUrl, getNextCard, updateCard, type FlashcardResponse } from '@/lib/api';

export default function Flashcards() {
  const [currentWord, setCurrentWord] = useState<FlashcardResponse | null>(null);
  const [showMeaning, setShowMeaning] = useState(false);
  const [sessionFinished, setSessionFinished] = useState(false);
  const [reviewedCount, setReviewedCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const loadNextCard = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const card = await getNextCard('en');
      setCurrentWord(card);
      setSessionFinished(false);
      setShowMeaning(false);
    } catch (e) {
      setCurrentWord(null);
      setSessionFinished(true);
      if (e instanceof Error && !e.message.includes('404')) {
        setError(e.message);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadNextCard();
  }, [loadNextCard]);

  const meaning = currentWord?.meaning || currentWord?.meaning_en || currentWord?.translation || 'No meaning available';

  const handlePronounce = () => {
    if (!currentWord) return;
    new Audio(getAudioUrl(currentWord.word)).play().catch(() => {
      setError('Unable to play pronunciation from the Python TTS service.');
    });
  };

  const handleRating = async (rating: number) => {
    if (!currentWord) return;

    setIsLoading(true);
    setError('');
    try {
      await updateCard(currentWord.word, rating);
      setReviewedCount(prev => prev + 1);
      await loadNextCard();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to update review.');
      setIsLoading(false);
    }
  };

  if (isLoading && !currentWord) {
    return (
      <AppLayout>
        <div className="h-[70vh] flex flex-col items-center justify-center text-center p-8">
          <div className="h-24 w-24 bg-primary/10 rounded-full flex items-center justify-center mb-6">
            <Trophy size={48} className="text-primary" />
          </div>
          <h1 className="text-4xl font-headline font-bold mb-4">Loading Review...</h1>
          <p className="text-muted-foreground max-w-md mx-auto">Fetching your next card from the Python SRS service.</p>
        </div>
      </AppLayout>
    );
  }

  if (!currentWord || sessionFinished) {
    return (
      <AppLayout>
        <div className="h-[70vh] flex flex-col items-center justify-center text-center p-8">
          <div className="h-24 w-24 bg-primary/10 rounded-full flex items-center justify-center mb-6">
            <Trophy size={48} className="text-primary" />
          </div>
          <h1 className="text-4xl font-headline font-bold mb-4">Great Job!</h1>
          <p className="text-muted-foreground max-w-md mx-auto mb-8">
            {error || "You've completed your vocabulary review session for now. Come back later for more!"}
          </p>
          <Button asChild size="lg" className="rounded-full px-8">
            <a href="/">Back to Dashboard</a>
          </Button>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="max-w-xl mx-auto pt-12">
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-headline font-bold">Review Session</h1>
            <p className="text-sm text-muted-foreground">{reviewedCount + 1} word{reviewedCount === 0 ? '' : 's'} reviewed</p>
          </div>
          <div className="h-2 w-32 bg-secondary rounded-full overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-500"
              style={{ width: `${Math.min(100, (reviewedCount + 1) * 20)}%` }}
            />
          </div>
        </header>

        {error && <p className="text-destructive text-sm mb-4 text-center">{error}</p>}

        <div className="relative perspective-1000">
          <Card
            className={cn(
              "h-96 glass cursor-pointer transition-all duration-500 transform-style-3d relative",
              showMeaning ? "[transform:rotateY(180deg)]" : ""
            )}
            onClick={() => !showMeaning && setShowMeaning(true)}
          >
            <div className="absolute inset-0 backface-hidden flex flex-col items-center justify-center p-8">
              <span className="text-[10px] uppercase font-bold tracking-widest text-primary mb-4">{currentWord.level}</span>
              <h2 className="text-5xl font-bold mb-8">{currentWord.word}</h2>
              <div className="flex gap-4">
                 <Button variant="outline" size="icon" className="rounded-full h-12 w-12" onClick={(e) => { e.stopPropagation(); handlePronounce(); }}>
                  <Volume2 size={24} />
                 </Button>
                 <Button variant="secondary" className="rounded-full px-6" onClick={() => setShowMeaning(true)}>
                  Reveal Meaning
                 </Button>
              </div>
            </div>

            <div className="absolute inset-0 backface-hidden [transform:rotateY(180deg)] flex flex-col items-center justify-center p-8 bg-primary/5">
              <h3 className="text-2xl text-muted-foreground mb-2">Meaning</h3>
              <p className="text-4xl font-headline font-bold mb-6 text-center">{meaning}</p>

              <p className="text-xs text-muted-foreground italic mb-8">How well did you know this?</p>

              <div className="flex gap-2 w-full max-w-xs">
                {[
                  { q: 1, label: 'Hard', icon: XCircle, color: 'text-destructive' },
                  { q: 3, label: 'Good', icon: HelpCircle, color: 'text-accent' },
                  { q: 5, label: 'Easy', icon: CheckCircle, color: 'text-green-500' }
                ].map((rating) => (
                  <Button
                    key={rating.q}
                    variant="ghost"
                    className="flex-1 flex flex-col h-auto py-3 gap-1 hover:bg-white/5"
                    disabled={isLoading}
                    onClick={(e) => { e.stopPropagation(); handleRating(rating.q); }}
                  >
                    <rating.icon size={24} className={rating.color} />
                    <span className="text-[10px] font-bold uppercase">{rating.label}</span>
                  </Button>
                ))}
              </div>
            </div>
          </Card>
        </div>

        <div className="mt-8 flex justify-center">
          <Button variant="ghost" className="text-muted-foreground hover:text-foreground" onClick={() => setShowMeaning(!showMeaning)}>
            <RotateCcw size={16} className="mr-2" />
            Flip Card (Spacebar)
          </Button>
        </div>
      </div>

      <style jsx global>{`
        .perspective-1000 { perspective: 1000px; }
        .backface-hidden { backface-visibility: hidden; -webkit-backface-visibility: hidden; }
        .transform-style-3d { transform-style: preserve-3d; -webkit-transform-style: preserve-3d; }
      `}</style>
    </AppLayout>
  );
}
