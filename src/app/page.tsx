'use client';

import { useState, useEffect } from 'react';
import { Item, ComparisonPair, getRankings, getNextPair, resetRanking } from './api';
import { AddItemForm } from './components/AddItemForm';
import { ComparisonSection } from './components/ComparisonSection';
import { RankingsList } from './components/RankingsList';

export default function Home() {
  const [items, setItems] = useState<Item[]>([]);
  const [currentPair, setCurrentPair] = useState<ComparisonPair | null>(null);
  const [loading, setLoading] = useState(true);

  // Initial data loading
  useEffect(() => {
    loadRankings();
    loadNextPair();
  }, []);

  async function loadRankings() {
    try {
      const rankings = await getRankings();
      setItems(rankings);
    } catch (error) {
      console.error('Failed to load rankings:', error);
    } finally {
      setLoading(false);
    }
  }

  async function loadNextPair() {
    try {
      const pair = await getNextPair();
      setCurrentPair(pair);
    } catch (error) {
      console.error('Failed to load next pair:', error);
      setCurrentPair(null);
    }
  }

  async function handleWinnerChosen() {
    await loadRankings();
    await loadNextPair();
  }

  async function handleReset() {
    try {
      setLoading(true);
      setCurrentPair(null);
      
      // Force a delay to ensure visual feedback
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Call the reset endpoint
      await resetRanking();
      
      // Get fresh data
      const rankings = await getRankings();
      setItems(rankings);
      
      // Keep trying to get a new pair until we succeed
      let attempts = 0;
      let pair = null;
      while (attempts < 3) {
        pair = await getNextPair();
        if (pair && !pair.complete) {
          break;
        }
        await new Promise(resolve => setTimeout(resolve, 500)); // Wait before retrying
        attempts++;
      }
      
      if (!pair || pair.complete) {
        throw new Error('No pairs available after reset');
      }
      
      setCurrentPair(pair);
    } catch (error) {
      console.error('Failed to restart ranking:', error);
      setCurrentPair(null);
    } finally {
      setLoading(false);
    }
  }

  async function handleItemAdded() {
    await loadRankings();
    await loadNextPair();
  }

  return (
    <div className="min-h-screen bg-white">
      <main className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-12 text-gray-900">
          Suparank
        </h1>
        
        <div className="space-y-12">
          <AddItemForm onItemAdded={handleItemAdded} />
          <ComparisonSection 
            currentPair={currentPair}
            items={items}
            onWinnerChosen={handleWinnerChosen}
            onReset={handleReset}
          />
          <RankingsList items={items} loading={loading} />
        </div>
      </main>
    </div>
  );
}
