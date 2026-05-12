"use client";

import { useEffect, useRef, useState } from 'react';
import { AppLayout } from '@/components/AppLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Plus,
  Trash2,
  Image as ImageIcon,
  Volume2,
  Loader2,
  AlertCircle,
  Pencil,
  RotateCcw,
  Save
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { createNotebookEntry, deleteNotebookEntry, getAudioUrl, getNotebookEntries, updateNotebookEntry, type NotebookEntry } from '@/lib/api';
import { GermanGender } from '@/lib/vocabulary';
import { useSearchParams } from 'next/navigation';

export default function VisualNotebook() {
  const searchParams = useSearchParams();
  const highlightedWord = searchParams.get('word')?.toLowerCase() ?? '';
  const highlightedRef = useRef<HTMLDivElement | null>(null);
  const [entries, setEntries] = useState<NotebookEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newWord, setNewWord] = useState('');
  const [newMeaning, setNewMeaning] = useState('');
  const [gender, setGender] = useState<GermanGender | ''>('');
  const [isAdding, setIsAdding] = useState(false);
  const [editingImageWord, setEditingImageWord] = useState<string | null>(null);
  const [imageUrlDraft, setImageUrlDraft] = useState('');
  const [failedImageWords, setFailedImageWords] = useState<Set<string>>(new Set());
  const { toast } = useToast();

  useEffect(() => {
    getNotebookEntries()
      .then((response) => setEntries(response.entries))
      .catch(() => {
        toast({ title: "Notebook Error", description: "Could not load your notebook.", variant: "destructive" });
      })
      .finally(() => setIsLoading(false));
  }, [toast]);

  useEffect(() => {
    if (highlightedRef.current) {
      highlightedRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [highlightedWord, entries]);

  const handleAddWord = async () => {
    if (!newWord || !newMeaning) return;
    setIsAdding(true);
    try {
      const entry = await createNotebookEntry({
        word: newWord,
        meaning: newMeaning,
        article: gender || undefined,
      });

      setEntries((current) => [entry, ...current.filter((item) => item.word.toLowerCase() !== entry.word.toLowerCase())]);
      setNewWord('');
      setNewMeaning('');
      setGender('');
      toast({ title: "Word Added", description: `"${newWord}" is now in your notebook.` });
    } catch (error) {
      toast({ title: "Error", description: "Failed to add this word.", variant: "destructive" });
    } finally {
      setIsAdding(false);
    }
  };

  const handleDeleteWord = async (word: string) => {
    try {
      await deleteNotebookEntry(word);
      setEntries((current) => current.filter((entry) => entry.word.toLowerCase() !== word.toLowerCase()));
      toast({ title: "Word Deleted", description: `"${word}" was removed from your notebook.` });
    } catch (error) {
      toast({ title: "Delete Failed", description: "Could not delete this word.", variant: "destructive" });
    }
  };

  const startImageEdit = (entry: NotebookEntry) => {
    setEditingImageWord(entry.word);
    setImageUrlDraft(entry.image_url);
  };

  const saveImageUrl = async (entry: NotebookEntry, imageUrl: string) => {
    try {
      const updatedEntry = await updateNotebookEntry(entry.word, {
        word: entry.word,
        meaning: entry.meaning,
        meaning_en: entry.meaning_en,
        example: entry.example,
        article: entry.article,
        image_url: imageUrl,
      });
      setEntries((current) => current.map((item) => item.word === entry.word ? updatedEntry : item));
      setFailedImageWords((current) => {
        const next = new Set(current);
        next.delete(entry.word);
        return next;
      });
      setEditingImageWord(null);
      setImageUrlDraft('');
      toast({ title: "Image Updated", description: `The image for "${entry.word}" was updated.` });
    } catch (error) {
      toast({ title: "Image Update Failed", description: "Could not update this image.", variant: "destructive" });
    }
  };

  const handleImageError = (word: string) => {
    setFailedImageWords((current) => new Set(current).add(word));
  };

  const handlePronounce = async (text: string) => {
    try {
      await new Audio(getAudioUrl(text)).play();
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
      {isLoading ? (
        <div className="flex items-center justify-center py-16 text-muted-foreground">
          <Loader2 className="animate-spin mr-2" /> Loading notebook...
        </div>
      ) : entries.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="p-12 text-center text-muted-foreground">
            <AlertCircle className="mx-auto mb-4 opacity-40" size={40} />
            <p>Your notebook is empty. Add your first German word above.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {entries.map((entry) => {
            const isHighlighted = highlightedWord === entry.word.toLowerCase();
            const isEditingImage = editingImageWord === entry.word;
            const hasImage = entry.image_url && !failedImageWords.has(entry.word);
            return (
              <Card
                key={entry.word}
                ref={isHighlighted ? highlightedRef : undefined}
                className={`glass card-hover overflow-hidden group ${isHighlighted ? 'ring-2 ring-primary' : ''}`}
              >
                <div className="aspect-video relative bg-muted overflow-hidden">
                  {hasImage ? (
                    <img
                      src={entry.image_url}
                      alt={entry.word}
                      className="h-full w-full object-cover transition-transform group-hover:scale-110"
                      onError={() => handleImageError(entry.word)}
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full text-muted-foreground/30">
                      <ImageIcon size={48} />
                    </div>
                  )}
                  <div className="absolute top-2 right-2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      variant="secondary"
                      size="icon"
                      className="h-8 w-8 rounded-full"
                      onClick={() => startImageEdit(entry)}
                    >
                      <Pencil size={14} />
                    </Button>
                    <Button
                      variant="destructive"
                      size="icon"
                      className="h-8 w-8 rounded-full"
                      onClick={() => handleDeleteWord(entry.word)}
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </div>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <h4 className="text-xl font-bold flex items-center gap-2">
                        {entry.article && <span className="text-xs font-medium text-muted-foreground">{entry.article}</span>}
                        {entry.word}
                      </h4>
                      <p className="text-sm text-muted-foreground italic">{entry.meaning}</p>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-10 w-10 rounded-full text-primary hover:bg-primary/10"
                      onClick={() => handlePronounce(entry.word)}
                    >
                      <Volume2 size={20} />
                    </Button>
                  </div>
                  <div className="flex items-center gap-2 mt-4">
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-primary/10 text-primary font-bold uppercase">{entry.pos}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-secondary text-muted-foreground font-bold uppercase">{entry.image_source || 'no image'}</span>
                  </div>
                  {isEditingImage && (
                    <div className="mt-4 space-y-2">
                      <Input
                        placeholder="Paste an image URL, or leave blank for auto lookup"
                        value={imageUrlDraft}
                        onChange={(event) => setImageUrlDraft(event.target.value)}
                        className="bg-secondary/20 text-xs"
                      />
                      <div className="grid grid-cols-2 gap-2">
                        <Button size="sm" className="text-xs" onClick={() => saveImageUrl(entry, imageUrlDraft)}>
                          <Save size={14} className="mr-1" /> Save image
                        </Button>
                        <Button size="sm" variant="outline" className="text-xs" onClick={() => saveImageUrl(entry, '')}>
                          <RotateCcw size={14} className="mr-1" /> Reset auto
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </AppLayout>
  );
}
