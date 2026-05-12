"use client";

import { useEffect, useState } from 'react';
import { AppLayout } from '@/components/AppLayout';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { getNotebookEntries, getSrsStats, type NotebookEntry, type SRSStatsResponse } from '@/lib/api';
import { cn } from '@/lib/utils';
import { Layers, Zap, Trophy, TrendingUp } from 'lucide-react';
import Link from 'next/link';

export default function Dashboard() {
  const [srsStats, setSrsStats] = useState<SRSStatsResponse | null>(null);
  const [notebookEntries, setNotebookEntries] = useState<NotebookEntry[]>([]);
  const [isStatsLoading, setIsStatsLoading] = useState(true);
  const [isNotebookLoading, setIsNotebookLoading] = useState(true);

  useEffect(() => {
    getSrsStats()
      .then(setSrsStats)
      .finally(() => setIsStatsLoading(false));

    getNotebookEntries()
      .then((response) => setNotebookEntries(response.entries))
      .finally(() => setIsNotebookLoading(false));
  }, []);

  const dueCount = srsStats?.due_cards ?? 0;
  const learnedCount = srsStats?.learned_cards ?? 0;
  const totalCount = srsStats?.total_cards ?? 0;
  const currentStreak = srsStats?.current_streak_days ?? 0;
  const streakDays = srsStats?.streak_last_7_days ?? Array.from({ length: 7 }, () => false);
  const masteredPercent = totalCount > 0 ? (learnedCount / totalCount) * 100 : 0;
  const recentWords = [...notebookEntries]
    .sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at))
    .slice(0, 4);

  return (
    <AppLayout>
      <header className="mb-8">
        <h1 className="text-4xl font-headline font-bold mb-2">Guten Tag!</h1>
        <p className="text-muted-foreground">Ready to master some German today?</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card className="glass card-hover">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Due for Review</CardTitle>
            <Layers className="text-accent" size={20} />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{isStatsLoading ? '...' : dueCount}</div>
            <p className="text-xs text-muted-foreground mt-1">Words waiting for review</p>
            <Button asChild className="w-full mt-4 bg-accent hover:bg-accent/90" size="sm" disabled={dueCount === 0}>
              <Link href="/flashcards">Start Review</Link>
            </Button>
          </CardContent>
        </Card>

        <Card className="glass card-hover">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Words Mastered</CardTitle>
            <Trophy className="text-yellow-500" size={20} />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{isStatsLoading ? '...' : learnedCount}</div>
            <p className="text-xs text-muted-foreground mt-1">From a total of {totalCount} words</p>
            <div className="h-1.5 w-full bg-secondary rounded-full mt-4">
              <div 
                className="h-full bg-yellow-500 rounded-full transition-all" 
                style={{ width: `${masteredPercent}%` }} 
              />
            </div>
          </CardContent>
        </Card>

        <Card className="glass card-hover">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Learning Streak</CardTitle>
            <Zap className="text-primary fill-primary" size={20} />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{isStatsLoading ? '...' : `${currentStreak} ${currentStreak === 1 ? 'Day' : 'Days'}`}</div>
            <p className="text-xs text-muted-foreground mt-1">Keep it up! Consistency is key.</p>
            <div className="flex gap-1 mt-4">
              {streakDays.map((active, i) => (
                <div key={i} className={cn("h-6 flex-1 rounded-sm", active ? "bg-primary" : "bg-secondary")} />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Card className="glass">
          <CardHeader>
            <CardTitle>Quick Practice</CardTitle>
            <CardDescription>Strengthen your reflexes with mini-games</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Link href="/games/gender" className="flex items-center justify-between p-4 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors group">
              <div>
                <h4 className="font-semibold">Der/Die/Das Reflex</h4>
                <p className="text-xs text-muted-foreground">Identify noun genders at lightning speed</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center group-hover:bg-primary transition-colors">
                <TrendingUp size={16} />
              </div>
            </Link>
            <Link href="/reader" className="flex items-center justify-between p-4 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors group">
              <div>
                <h4 className="font-semibold">Context Analyzer</h4>
                <p className="text-xs text-muted-foreground">Study articles and extract vocabulary</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-accent/20 flex items-center justify-center group-hover:bg-accent transition-colors">
                <TrendingUp size={16} />
              </div>
            </Link>
          </CardContent>
        </Card>

        <Card className="glass">
          <CardHeader>
            <CardTitle>Recent Words</CardTitle>
            <CardDescription>Newest additions to your visual notebook</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {isNotebookLoading ? (
                <p className="text-sm text-muted-foreground italic">Loading notebook...</p>
              ) : recentWords.length === 0 ? (
                <p className="text-sm text-muted-foreground italic">No notebook words yet. Add your first word to see it here.</p>
              ) : recentWords.map((entry) => (
                <Link
                  key={entry.word}
                  href={`/notebook?word=${encodeURIComponent(entry.word)}`}
                  className="flex items-center gap-3 p-2 rounded-md hover:bg-secondary/30 transition-colors"
                >
                  <div className="h-10 w-10 bg-primary/10 rounded flex items-center justify-center font-bold text-primary">
                    {entry.word[0].toUpperCase()}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-sm">{entry.word}</p>
                    <p className="text-xs text-muted-foreground">{entry.meaning}</p>
                  </div>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-secondary text-muted-foreground uppercase">{entry.pos}</span>
                </Link>
              ))}
            </div>
            <Button asChild variant="ghost" className="w-full mt-4 text-xs">
              <Link href="/notebook">View Visual Notebook</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
