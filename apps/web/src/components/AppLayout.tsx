import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  BookOpen, 
  Search, 
  Layers, 
  Gamepad2, 
  PenTool, 
  Home,
  MessageSquare,
  Zap
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/', label: 'Dashboard', icon: Home },
  { href: '/search', label: 'Lookup', icon: Search },
  { href: '/flashcards', label: 'SRS Cards', icon: Layers },
  { href: '/reader', label: 'Context Reader', icon: BookOpen },
  { href: '/notebook', label: 'Visual Notebook', icon: PenTool },
  { href: '/games', label: 'Games', icon: Gamepad2 },
];

export function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-card/30 flex flex-col">
        <div className="p-6">
          <h1 className="text-2xl font-headline font-bold text-primary flex items-center gap-2">
            <Zap className="fill-primary" />
            WortMeister
          </h1>
        </div>
        
        <nav className="flex-1 px-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-md transition-colors",
                  isActive 
                    ? "bg-primary text-white" 
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                )}
              >
                <Icon size={20} />
                <span className="font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 mt-auto border-t border-border">
          <div className="bg-primary/10 rounded-lg p-3">
            <p className="text-xs text-muted-foreground mb-1 uppercase font-bold tracking-wider">Session Goal</p>
            <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
              <div className="h-full bg-primary w-[65%]" />
            </div>
            <p className="text-[10px] mt-2 text-primary-foreground/70">13 / 20 words learned today</p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto relative">
        <div className="max-w-5xl mx-auto p-8 animate-fade-in">
          {children}
        </div>
      </main>
    </div>
  );
}
