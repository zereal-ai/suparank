'use client';

import { useState, useEffect } from 'react';
import { startSortSession, getNextPair, postComparison } from './api';
import { ComparisonSection } from './components/ComparisonSection';

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentPair, setCurrentPair] = useState<{ item_a: string; item_b: string } | null>(null);
  const [sortedList, setSortedList] = useState<string[] | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  
  useEffect(() => {
    async function initSession() {
      setLoading(true);
      try {
        // Hardcoded initial items for the merge sort session
        const items = ['three', 'four', 'two', 'one', 'five'];
        const sId = await startSortSession(items);
        setSessionId(sId);
        const pair = await getNextPair(sId);
        if (pair.message && pair.message === 'Sorting complete.') {
          setSortedList(pair.sorted_list);
        } else {
          setCurrentPair(pair);
        }
      } catch (error) {
        console.error('Error initializing session:', error);
      }
      setLoading(false);
    }
    initSession();
  }, []);
  
  async function handleChoice(choice: 'A' | 'B') {
    if (!sessionId) return;
    setLoading(true);
    try {
      await postComparison(sessionId, choice);
      const pair = await getNextPair(sessionId);
      if (pair.message && pair.message === 'Sorting complete.') {
        setSortedList(pair.sorted_list);
        setCurrentPair(null);
      } else {
        setCurrentPair(pair);
      }
    } catch (error) {
      console.error('Error processing choice:', error);
    }
    setLoading(false);
  }
  
  return (
    <div className='min-h-screen bg-white'>
      <main className='max-w-2xl mx-auto px-4 py-8'>
        <h1 className='text-2xl font-bold mb-12 text-gray-900'>Suparank</h1>
        {loading && <p>Loading...</p>}
        {!loading && sortedList && (
          <div>
            <h2 className='text-xl font-semibold'>Sorted List:</h2>
            <ol className='list-decimal ml-5'>
              {sortedList.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ol>
          </div>
        )}
        {!loading && currentPair && (
          <ComparisonSection currentPair={currentPair} onChoice={handleChoice} />
        )}
      </main>
    </div>
  );
}
