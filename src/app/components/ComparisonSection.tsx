import { useState, useEffect } from 'react';
import { Item, ComparisonPair, chooseWinner, resetRanking } from '../api';
import { CheckIcon, ArrowLeftCircleIcon, ArrowRightCircleIcon } from '@heroicons/react/24/solid';

interface ComparisonSectionProps {
  currentPair: ComparisonPair | null;
  items: Item[];
  onWinnerChosen: () => Promise<void>;
  onReset: () => Promise<void>;
}

export function ComparisonSection({ 
  currentPair, 
  items, 
  onWinnerChosen,
  onReset 
}: ComparisonSectionProps) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);

  // Keyboard navigation
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (!currentPair || currentPair.complete || isAnimating) return;

      switch (e.key) {
        case 'ArrowLeft':
          e.preventDefault();
          handleSelection(0);
          break;
        case 'ArrowRight':
          e.preventDefault();
          handleSelection(1);
          break;
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentPair, isAnimating]);

  async function handleSelection(index: number) {
    if (!currentPair || isAnimating) return;
    
    try {
      setSelectedIndex(index);
      setIsAnimating(true);

      // Wait for animation
      await new Promise(resolve => setTimeout(resolve, 300));

      const winner = currentPair.pair[index];
      const loser = currentPair.pair[index === 0 ? 1 : 0];
      
      await chooseWinner(winner.id, loser.id);
      await onWinnerChosen();
    } catch (error) {
      console.error('Selection failed:', error);
    } finally {
      setSelectedIndex(null);
      setIsAnimating(false);
    }
  }

  async function handleRestartRanking() {
    try {
      setSelectedIndex(null);
      await onReset();
    } catch (error) {
      console.error('Failed to restart ranking:', error);
    }
  }

  return (
    <section className="bg-white">
      <h2 className="text-lg font-medium mb-4 text-gray-900">
        Compare Items
      </h2>
      {currentPair?.pair && !currentPair.complete ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {currentPair.pair.map((entry, index) => (
            <button
              key={entry.id}
              onClick={() => handleSelection(index)}
              disabled={isAnimating}
              className={`p-6 text-left rounded-lg transition-all duration-300 ${
                selectedIndex === index
                  ? "bg-blue-100 border-blue-500 scale-105 transform"
                  : selectedIndex === null
                  ? "bg-white hover:bg-gray-50 border-gray-200"
                  : "bg-gray-50 border-gray-200"
              } border-2 relative min-h-[200px]`}
            >
              <div className="mb-12">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{entry.title}</h3>
                <p className="text-gray-600 text-sm">{entry.description}</p>
              </div>
              {selectedIndex === index && (
                <div className="absolute inset-0 flex items-center justify-center bg-blue-500/10 rounded-lg">
                  <div className="bg-white p-2 rounded-full">
                    <CheckIcon className="w-6 h-6 text-blue-500" />
                  </div>
                </div>
              )}
              <div className={`absolute ${index === 0 ? 'left-4' : 'right-4'} bottom-4 flex items-center gap-2 text-gray-500`}>
                {index === 0 ? (
                  <>
                    <ArrowLeftCircleIcon className="w-6 h-6" />
                    <span className="text-sm">Left Arrow</span>
                  </>
                ) : (
                  <>
                    <span className="text-sm">Right Arrow</span>
                    <ArrowRightCircleIcon className="w-6 h-6" />
                  </>
                )}
              </div>
            </button>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <p className="text-gray-600 mb-4">
            {items.length < 2 
              ? "Add at least two items to start ranking!"
              : "All items are ranked! Want to refine the order?"}
          </p>
          {items.length >= 2 && (
            <button
              onClick={handleRestartRanking}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            >
              Start New Ranking Session
            </button>
          )}
        </div>
      )}
    </section>
  );
} 