import React, { useEffect } from 'react';
import { ArrowLeftIcon, ArrowRightIcon } from '@heroicons/react/24/outline';

interface ComparisonSectionProps {
  currentPair: { item_a: string; item_b: string } | null;
  onChoice: (choice: 'A' | 'B') => Promise<void>;
}

export function ComparisonSection({ currentPair, onChoice }: ComparisonSectionProps) {
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'ArrowLeft') {
        onChoice('A');
      } else if (e.key === 'ArrowRight') {
        onChoice('B');
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onChoice]);

  if (!currentPair) return null;
  
  return (
    <section className="bg-white rounded-lg border border-gray-200 p-6 mt-4 shadow-sm">
      <h2 className="text-xl font-medium mb-6 text-gray-900">Which do you prefer?</h2>
      <div className="flex flex-col md:flex-row justify-around gap-6 items-center">
        <button
          onClick={() => onChoice('A')}
          className="w-full md:w-[300px] p-6 bg-white border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all duration-200 group relative"
        >
          <div className="absolute -left-2 top-1/2 -translate-y-1/2 text-gray-400 group-hover:text-blue-500">
            <ArrowLeftIcon className="h-5 w-5" />
          </div>
          <p className="text-lg font-medium text-gray-900">{currentPair.item_a}</p>
        </button>

        <div className="text-sm text-gray-500">
          <p>Use arrow keys ← →</p>
          <p>or click to choose</p>
        </div>

        <button
          onClick={() => onChoice('B')}
          className="w-full md:w-[300px] p-6 bg-white border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all duration-200 group relative"
        >
          <div className="absolute -right-2 top-1/2 -translate-y-1/2 text-gray-400 group-hover:text-blue-500">
            <ArrowRightIcon className="h-5 w-5" />
          </div>
          <p className="text-lg font-medium text-gray-900">{currentPair.item_b}</p>
        </button>
      </div>
    </section>
  );
} 