"use client";

import { useState } from 'react';
import { AppLayout } from '@/components/AppLayout';
import { useVocabulary } from '@/hooks/use-vocabulary';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Plus, 
  Trash2, 
  Image as ImageIcon, 
  Volume2, 
  Loader2,
  AlertCircle
} from 'lucide-react';
import { augmentNewVocabularyWithAI } from '@/ai/flows/augment-new-vocabulary-with-ai';
import { generateCustomPronunciation } from '@/ai/flows/generate-custom-pronunciation-flow';
import { useToast } from '@/hooks/use-toast';
import { GermanGender } from '@/lib/vocabulary';
import Image from 'next/image';

export default function VisualNotebook() {
  const { vocabulary, addWord, deleteWord } = useVocabulary();
  const [newWord, setNewWord] = useState('');
  const [newMeaning, setNewMeaning] = useState('');
  const [gender, setGender] = useState<GermanGender | ''>('');
  const [isAdding, setIsAdding] = useState(false);
  const { toast } = useToast();

  const handleAddWord = async () => {
    if (!newWord || !newMeaning) return;
    setIsAdding(true);
    try {
      // AI Augmentation: Get POS and Image
      const aiResult = await augmentNewVocabularyWithAI({ word: newWord });
      
      addWord({
        id: Date.now().toString(),
        word: newWord,
        meaning: newMeaning,
        gender: gender as GermanGender || undefined,
        pos: aiResult.partOfSpeech,
        level: 'A1',
        imageUrl: aiResult.imageUrl,
      });

      setNewWord('');
      setNewMeaning('');
      setGender('');
      toast({ title: "Word Added", description: `"${newWord}" is now in your notebook.` });
    } catch (error) {
      toast({ title: "Error", description: "Failed to augment word with AI.", variant: "destructive" });
    } finally {
      setIsAdding(false);
    }
  };

  const handlePronounce = async (text: string) => {
    try {
      const { media } = await generateCustomPronunciation({ text });
      new Audio(media).play();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <AppLayout>
      <header className="mb-12">
        <h1 className="text-4xl font-headline font-bold mb-2 text-primary">Visual Notebook</h1>
        <p className="text-muted-foreground italic">Your personalized collection of German vocabulary with visual cues.</p>
      </header>

      {/* Add New Word Form */}
      <Card className="glass mb-12 border-primary/20">
        <CardContent className="p-6">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
            <Plus className="text-primary" size={20} />
            Quick Add
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] uppercase tracking-tighter text-muted-foreground font-bold">German Word</label>
              <Input 
                placeholder="e.g. Freiheit" 
                value={newWord}
                onChange={(e) => setNewWord(e.target.value)}
                className="bg-secondary/20"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[10px] uppercase tracking-tighter text-muted-foreground font-bold">Meaning (English)</label>
              <Input 
                placeholder="e.g. Freedom" 
                value={newMeaning}
                onChange={(e) => setNewMeaning(e.target.value)}
                className="bg-secondary/20"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[10px] uppercase tracking-tighter text-muted-foreground font-bold">Gender (Optional)</label>
              <div className="flex gap-2">
                {['der', 'die', 'das'].map((g) => (
                  <Button
                    key={g}
                    variant={gender === g ? 'default' : 'outline'}
                    size="sm"
                    className="flex-1 text-xs"
                    onClick={() => setGender(g === gender ? '' : (g as GermanGender))}
                  >
                    {g}
                  </Button>
                ))}
              </div>
            </div>
            <div className="flex items-end">
              <Button 
                className="w-full h-10 font-bold" 
                onClick={handleAddWord}
                disabled={isAdding || !newWord || !newMeaning}
              >
                {isAdding ? <Loader2 className="animate-spin" /> : 'Add to Collection'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Word Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {vocabulary.map((v) => (
          <Card key={v.id} className="glass card-hover overflow-hidden group">
            <div className="aspect-video relative bg-muted overflow-hidden">
              {v.imageUrl ? (
                <Image 
                  src={v.imageUrl} 
                  alt={v.word} 
                  fill 
                  className="object-cover transition-transform group-hover:scale-110" 
                />
              ) : (
                <div className="flex items-center justify-center h-full text-muted-foreground/30">
                  <ImageIcon size={48} />
                </div>
              )}
              <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button 
                  variant="destructive" 
                  size="icon" 
                  className="h-8 w-8 rounded-full"
                  onClick={() => deleteWord(v.id)}
                >
                  <Trash2 size={14} />
                </Button>
              </div>
            </div>
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <h4 className="text-xl font-bold flex items-center gap-2">
                    {v.gender && <span className="text-xs font-medium text-muted-foreground">{v.gender}</span>}
                    {v.word}
                  </h4>
                  <p className="text-sm text-muted-foreground italic">{v.meaning}</p>
                </div>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="h-10 w-10 rounded-full text-primary hover:bg-primary/10"
                  onClick={() => handlePronounce(v.word)}
                >
                  <Volume2 size={20} />
                </Button>
              </div>
              <div className="flex items-center gap-2 mt-4">
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-primary/10 text-primary font-bold uppercase">{v.pos}</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-secondary text-muted-foreground font-bold uppercase">{v.level}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </AppLayout>
  );
}
