import React from 'react';

interface ComparisonSectionProps {
  currentPair: { item_a: string; item_b: string } | null;
  onChoice: (choice: 'A' | 'B') => Promise<void>;
}

export function ComparisonSection({ currentPair, onChoice }: ComparisonSectionProps) {
  if (!currentPair) return null;
  
  return (
    <section className="bg-white mt-4">
      <h2 className="text-lg font-medium mb-4">Choose your preferred item</h2>
      <div className="flex flex-col md:flex-row justify-around gap-4">
        <button
          onClick={() => onChoice('A')}
          className="px-4 py-2 bg-blue-500 text-white rounded"
        >
          {currentPair.item_a}
        </button>
        <button
          onClick={() => onChoice('B')}
          className="px-4 py-2 bg-green-500 text-white rounded"
        >
          {currentPair.item_b}
        </button>
      </div>
    </section>
  );
} 