// src/app/dashboard/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { onAuthStateChanged, signOut, User } from 'firebase/auth';
import { auth } from '../../lib/firebase';
import { ThemeToggle } from '../../components/ui/theme-toggle';

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (currentUser) {
        setUser(currentUser);
      } else {
        router.push('/auth/login'); // Redirect to login if not authenticated
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, [router]);

  const handleLogout = async () => {
    try {
      await signOut(auth);
      router.push('/auth/login');
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background dark:bg-dark-background text-primary dark:text-dark-primary">
        Loading...
      </div>
    );
  }

  if (!user) {
    return null; // Should redirect by useEffect
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background dark:bg-dark-background text-neutral-dark dark:text-dark-neutral-dark p-4">
      <h1 className="text-3xl font-bold text-primary dark:text-dark-primary mb-4">Dashboard</h1>
      <p className="text-lg mb-2">Welcome, {user.email}</p>
      {user.emailVerified ? (
        <p className="text-green-500 mb-4">Email Verified</p>
      ) : (
        <p className="text-red-500 mb-4">Email Not Verified</p>
      )}
      <button
        onClick={handleLogout}
        className="bg-accent hover:bg-accent-dark text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline mb-4"
      >
        Logout
      </button>
      <ThemeToggle />
    </div>
  );
}
