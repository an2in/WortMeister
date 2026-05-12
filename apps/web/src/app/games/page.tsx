"use client";

import { AppLayout } from '@/components/AppLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { Gamepad2, Brain, Map } from 'lucide-react';

export default function GamesHub() {
  return (
    <AppLayout>
      <header className="mb-12">
        <h1 className="text-4xl font-headline font-bold mb-2">Practice Games</h1>
        <p className="text-muted-foreground">Gamified learning routines to boost retention.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Card className="glass card-hover">
          <div className="h-48 bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center">
            <Brain size={64} className="text-primary animate-pulse" />
          </div>
          <CardHeader>
            <CardTitle>Der/Die/Das Reflex</CardTitle>
            <CardDescription>Rapidly identify noun genders. Essential for German mastery.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full h-12 text-lg">
              <Link href="/games/gender">Play Now</Link>
            </Button>
          </CardContent>
        </Card>

        <Card className="glass card-hover">
          <div className="h-48 bg-gradient-to-br from-accent/20 to-green-500/20 flex items-center justify-center">
            <Map size={64} className="text-accent" />
          </div>
          <CardHeader>
            <CardTitle>Vocabulary Maze</CardTitle>
            <CardDescription>Navigate a maze while spelling target vocabulary. Gamified translation check.</CardDescription>
          </CardHeader>
          <CardContent>
             <Button asChild className="w-full h-12 text-lg" variant="secondary">
              <Link href="/games/maze">Explore Maze</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
