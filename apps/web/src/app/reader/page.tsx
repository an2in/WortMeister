"use client";

import { useState } from 'react';
import { AppLayout } from '@/components/AppLayout';
import { useVocabulary } from '@/hooks/use-vocabulary';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { 
  analyzeCustomTextForVocabulary, 
  AnalyzeCustomTextForVocabularyOutput 
} from '@/ai/flows/analyze-custom-text-for-vocabulary';
import { getAudioUrl } from '@/lib/api';
import { Loader2, BookOpen, Volume2, Highlighter } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export default function ContextReader() {
  const { vocabulary } = useVocabulary();
  const [inputText, setInputText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<AnalyzeCustomTextForVocabularyOutput | null>(null);
  const { toast } = useToast();

  const handleAnalyze = async () => {
    if (!inputText.trim()) return;
    setIsAnalyzing(true);
    try {
      const knownWords = vocabulary.map(v => v.word);
      const result = await analyzeCustomTextForVocabulary({
        germanText: inputText,
        knownVocabulary: knownWords
      });
      setAnalysis(result);
    } catch (error) {
      toast({
        title: "Analysis Failed",
        description: "Something went wrong while analyzing the text.",
        variant: "destructive"
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handlePronounce = async (text: string) => {
    try {
      const audio = new Audio(getAudioUrl(text));
      await audio.play();
    } catch (error) {
      toast({ title: "Audio Error", description: "Could not play pronunciation.", variant: "destructive" });
    }
  };

  return (
    <AppLayout>
      <header className="mb-8">
        <h1 className="text-4xl font-headline font-bold mb-2">Context Analyzer</h1>
        <p className="text-muted-foreground">Import text to identify target vocabulary and hear pronunciations in context.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <Card className="glass">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <BookOpen size={20} className="text-primary" />
                Input German Text
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea 
                placeholder="Paste news articles, book excerpts, or your own writing here..."
                className="min-h-[300px] bg-secondary/30 resize-none text-lg leading-relaxed"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
              />
              <Button 
                className="w-full mt-4 h-12 text-lg" 
                onClick={handleAnalyze} 
                disabled={isAnalyzing || !inputText}
              >
                {isAnalyzing ? <><Loader2 className="animate-spin mr-2" /> Analyzing...</> : 'Analyze Text'}
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          {!analysis ? (
            <div className="h-full flex flex-col items-center justify-center p-12 text-center border-2 border-dashed border-border rounded-xl text-muted-foreground">
              <Highlighter size={48} className="mb-4 opacity-20" />
              <p>Your analysis results will appear here after processing.</p>
            </div>
          ) : (
            <>
              <Card className="glass border-accent/20">
                <CardHeader>
                  <CardTitle className="text-lg">Target Vocabulary</CardTitle>
                  <CardDescription>Unknown words found in this text</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {analysis.unknownWordsInText.map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-accent/5 hover:bg-accent/10 transition-colors border border-accent/10">
                      <div>
                        <span className="font-bold text-accent">{item.word}</span>
                        <p className="text-xs text-muted-foreground">{item.meaning}</p>
                      </div>
                      <Button variant="ghost" size="icon" onClick={() => handlePronounce(item.word)}>
                        <Volume2 size={16} className="text-accent" />
                      </Button>
                    </div>
                  ))}
                  {analysis.unknownWordsInText.length === 0 && (
                    <p className="text-sm text-muted-foreground italic">You seem to know all words in this text! Well done.</p>
                  )}
                </CardContent>
              </Card>

              <Card className="glass">
                <CardHeader>
                  <CardTitle className="text-lg">Mastery Check</CardTitle>
                  <CardDescription>Previously learned words identified</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {analysis.knownWordsInText.map((word, idx) => (
                      <span key={idx} className="px-3 py-1 bg-primary/10 text-primary border border-primary/20 rounded-full text-sm font-medium">
                        {word}
                      </span>
                    ))}
                    {analysis.knownWordsInText.length === 0 && (
                      <p className="text-sm text-muted-foreground italic">No familiar words detected yet.</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
