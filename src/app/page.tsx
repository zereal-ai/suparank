'use client';

import { useState, useEffect } from 'react';
import { startSortSession, getNextPair, postComparison, getItems, Item } from './api';
import { ComparisonSection } from './components/ComparisonSection';
import { RankingsList } from './components/RankingsList';
import { AddItemForm } from './components/AddItemForm';

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentPair, setCurrentPair] = useState<{ item_a: string; item_b: string } | null>(null);
  const [sortedList, setSortedList] = useState<string[] | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [items, setItems] = useState<Item[]>([]);
  const [itemsLoading, setItemsLoading] = useState<boolean>(true);
  
  // Fetch items from Airtable
  async function fetchItems() {
    setItemsLoading(true);
    try {
      const fetchedItems = await getItems();
      setItems(fetchedItems);
    } catch (error) {
      console.error('Error fetching items:', error);
    }
    setItemsLoading(false);
  }

  // Initial items fetch
  useEffect(() => {
    fetchItems();
  }, []);

  // Start sorting session when items are loaded
  useEffect(() => {
    async function initSession() {
      if (items.length < 2) return;
      setLoading(true);
      try {
        // Use item IDs from Airtable
        const itemIds = items.map(item => item.id);
        const sId = await startSortSession(itemIds);
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
    
    if (!itemsLoading && items.length >= 2) {
      initSession();
    }
  }, [items, itemsLoading]);
  
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

  // Get the item objects for the current pair
  const pairItems = currentPair ? {
    item_a: items.find(item => item.id === currentPair.item_a),
    item_b: items.find(item => item.id === currentPair.item_b)
  } : null;

  // Get the sorted items objects
  const sortedItems = sortedList 
    ? sortedList.map(id => items.find(item => item.id === id)).filter(Boolean) as Item[]
    : null;
  
  return (
    <div className='min-h-screen bg-gray-50'>
      <main className='max-w-3xl mx-auto px-4 py-12'>
        <div className='space-y-8'>
          <div>
            <h1 className='text-4xl font-bold mb-2 text-gray-900'>Suparank</h1>
            <p className='text-gray-600'>Rank your items through simple comparisons</p>
          </div>

          <AddItemForm onItemAdded={fetchItems} />

          {loading && (
            <div className='text-center py-12'>
              <div className='animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4'></div>
              <p className='text-gray-600'>Processing...</p>
            </div>
          )}

          {!loading && pairItems && (
            <ComparisonSection 
              currentPair={{
                item_a: pairItems.item_a || { title: '', description: '' },
                item_b: pairItems.item_b || { title: '', description: '' }
              }} 
              onChoice={handleChoice} 
            />
          )}

          <RankingsList 
            items={items} 
            loading={itemsLoading} 
            onItemDeleted={fetchItems}
            sortedList={sortedList}
          />
        </div>
      </main>
    </div>
  );
}
