// src/app/page.tsx
import { ThemeToggle } from '../components/ui/theme-toggle';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold text-primary dark:text-dark-primary mb-8">
        Aquatics Scheduler
      </h1>
      <p className="text-lg text-neutral-dark dark:text-dark-neutral-dark mb-8">
        Welcome to the new frontend!
      </p>
      <ThemeToggle />
      <div className="mt-8 p-4 rounded-md bg-accent-light dark:bg-dark-accent-light text-accent-dark dark:text-dark-accent-dark">
        This is a themed box.
      </div>
    </main>
  );
}