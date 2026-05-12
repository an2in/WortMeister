"use client";

import { useState, useMemo } from 'react';
import { AppLayout } from '@/components/AppLayout';
import { useVocabulary } from '@/hooks/use-vocabulary';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Search, Volume2, Plus, Check } from 'lucide-react';
import { generateCustomPronunciation } from '@/ai/flows/generate-custom-pronunciation-flow';
import { getFullWordDisplay } from '@/lib/vocabulary';
import { useToast } from '@/hooks/use-toast';

export default function VocabularyLookup() {
  const [searchQuery, setSearchQuery] = useState('');
  const { vocabulary, addWord } = useVocabulary();
  const [isPronouncing, setIsPronouncing] = useState<string | null>(null);
  const { toast } = useToast();

  const filteredVocab = useMemo(() => {
    if (!searchQuery) return [];
    const q = searchQuery.toLowerCase();
    return vocabulary.filter(v => 
      v.word.toLowerCase().includes(q) || 
      v.meaning.toLowerCase().includes(q)
    ).slice(0, 8);
  }, [searchQuery, vocabulary]);

  const handlePronounce = async (text: string) => {
    try {
      setIsPronouncing(text);
      const { media } = await generateCustomPronunciation({ text });
      const audio = new Audio(media);
      await audio.play();
    } catch (error) {
      toast({
        title: "Pronunciation Error",
        description: "Failed to generate audio. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsPronouncing(null);
    }
  };

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto">
        <header className="mb-12 text-center">
          <h1 className="text-5xl font-headline font-bold mb-4">Wort-Suche</h1>
          <p className="text-muted-foreground text-lg">Super-fast German dictionary lookup with audio support.</p>
        </header>

        <div className="relative mb-8">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" size={24} />
          <Input 
            autoFocus
            className="pl-14 h-16 text-xl rounded-2xl glass border-primary/20 focus:border-primary focus:ring-primary/20"
            placeholder="Type a German word or meaning..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="space-y-4">
          {searchQuery && filteredVocab.length === 0 ? (
            <Card className="p-8 text-center border-dashed">
              <p className="text-muted-foreground">No matches found for "{searchQuery}" in your current database.</p>
              <Button variant="outline" className="mt-4" onClick={() => toast({ title: "Custom additions coming soon", description: "Use the Visual Notebook to add words." })}>
                Add "{searchQuery}" manually?
              </Button>
            </Card>
          ) : (
            filteredVocab.map((v) => (
              <Card key={v.id} className="glass card-hover overflow-hidden">
                <CardContent className="p-4 flex items-center gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <span className="text-2xl font-bold">{getFullWordDisplay(v)}</span>
                      <span className="text-[10px] bg-primary/20 text-primary px-2 py-0.5 rounded-full font-bold">{v.level}</span>
                    </div>
                    <p className="text-muted-foreground italic">{v.meaning}</p>
                  </div>
                  <div className="flex gap-2">
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="rounded-full h-12 w-12 hover:bg-primary/10"
                      onClick={() => handlePronounce(v.word)}
                      disabled={isPronouncing === v.word}
                    >
                      <Volume2 className={cn("text-primary", isPronouncing === v.word && "animate-pulse")} />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {searchQuery === '' && (
          <div className="mt-20">
            <h3 className="text-muted-foreground text-center uppercase tracking-widest text-sm mb-6">Popular Searches</h3>
            <div className="flex flex-wrap justify-center gap-3">
              {['Haus', 'lernen', 'schnell', 'Apfel', 'essen'].map(word => (
                <button 
                  key={word}
                  onClick={() => setSearchQuery(word)}
                  className="px-6 py-3 rounded-xl bg-secondary hover:bg-primary/20 transition-colors text-lg"
                >
                  {word}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}

import { cn } from '@/lib/utils';
