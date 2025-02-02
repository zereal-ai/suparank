import React, { useEffect, useState } from 'react';
import { ArrowLeftIcon, ArrowRightIcon } from '@heroicons/react/24/outline';

interface ComparisonSectionProps {
  currentPair: { 
    item_a: { title: string; description?: string }; 
    item_b: { title: string; description?: string }; 
  } | null;
  onChoice: (choice: 'A' | 'B') => Promise<void>;
}

export function ComparisonSection({ currentPair, onChoice }: ComparisonSectionProps) {
  const [selectedChoice, setSelectedChoice] = useState<'A' | 'B' | null>(null);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'ArrowLeft') {
        setSelectedChoice('A');
        onChoice('A');
      } else if (e.key === 'ArrowRight') {
        setSelectedChoice('B');
        onChoice('B');
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onChoice]);

  const handleClick = async (choice: 'A' | 'B') => {
    setSelectedChoice(choice);
    await onChoice(choice);
  };

  if (!currentPair) return null;
  
  return (
    <section className="bg-white rounded-xl border border-gray-200 p-8 mt-4 shadow-sm">
      <h2 className="text-2xl font-medium mb-8 text-center text-gray-900">Which do you prefer?</h2>
      <div className="flex flex-col md:flex-row justify-center gap-8 items-stretch max-w-4xl mx-auto">
        <button
          onClick={() => handleClick('A')}
          disabled={selectedChoice !== null}
          className={`
            relative w-full md:w-[320px] p-6 bg-white border-2 rounded-xl
            transition-all duration-300 ease-out flex flex-col
            ${selectedChoice === 'A' 
              ? 'border-blue-500 shadow-lg scale-105' 
              : selectedChoice === 'B'
                ? 'border-gray-100 opacity-50'
                : 'border-gray-200 hover:border-blue-200 hover:shadow-md'
            }
          `}
        >
          <div className="flex-1">
            <p className="text-lg font-medium text-gray-900">{currentPair.item_a.title}</p>
            {currentPair.item_a.description && (
              <p className="mt-2 text-sm text-gray-600">{currentPair.item_a.description}</p>
            )}
          </div>
        </button>

        <button
          onClick={() => handleClick('B')}
          disabled={selectedChoice !== null}
          className={`
            relative w-full md:w-[320px] p-6 bg-white border-2 rounded-xl
            transition-all duration-300 ease-out flex flex-col
            ${selectedChoice === 'B' 
              ? 'border-blue-500 shadow-lg scale-105' 
              : selectedChoice === 'A'
                ? 'border-gray-100 opacity-50'
                : 'border-gray-200 hover:border-blue-200 hover:shadow-md'
            }
          `}
        >
          <div className="flex-1">
            <p className="text-lg font-medium text-gray-900">{currentPair.item_b.title}</p>
            {currentPair.item_b.description && (
              <p className="mt-2 text-sm text-gray-600">{currentPair.item_b.description}</p>
            )}
          </div>
        </button>
      </div>

      <div className="text-sm text-gray-400 flex flex-col items-center gap-1 mt-6">
        <p className="flex items-center gap-2">
          <ArrowLeftIcon className="h-4 w-4" /> 
          <ArrowRightIcon className="h-4 w-4" />
        </p>
        <p>use arrows or click</p>
      </div>
    </section>
  );
} 