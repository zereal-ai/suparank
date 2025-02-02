import { Item, deleteItem } from '../api';
import { XMarkIcon } from '@heroicons/react/20/solid';
import { TrophyIcon } from '@heroicons/react/24/outline';

interface RankingsListProps {
  items: Item[];
  loading: boolean;
  onItemDeleted: () => void;
}

export function RankingsList({ items, loading, onItemDeleted }: RankingsListProps) {
  const handleDelete = async (itemId: string) => {
    try {
      await deleteItem(itemId);
      onItemDeleted();
    } catch (error) {
      console.error('Failed to delete item:', error);
      // You might want to show a toast notification here
    }
  };

  return (
    <section className="bg-white rounded-lg border border-gray-200 p-6 mt-8 shadow-sm">
      <div className="flex items-center gap-2 mb-6">
        <TrophyIcon className="h-6 w-6 text-yellow-500" />
        <h2 className="text-xl font-medium text-gray-900">Current Rankings</h2>
      </div>
      <div className="space-y-3">
        {loading ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-50 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg border border-dashed border-gray-300">
            <p className="text-gray-500">
              No items yet. Add some items to start ranking!
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {items.map((entry, index) => (
              <div
                key={entry.id}
                className="flex items-center gap-4 p-4 bg-white rounded-lg border border-gray-200 hover:border-blue-200 group transition-all duration-200"
              >
                <div className="flex-none w-8 h-8 flex items-center justify-center rounded-full bg-gray-100 text-gray-700 font-medium">
                  {index + 1}
                </div>
                <div className="flex-grow min-w-0">
                  <h3 className="text-lg font-medium text-gray-900 leading-tight">{entry.title}</h3>
                  {entry.description && (
                    <p className="text-gray-600 text-sm mt-1">{entry.description}</p>
                  )}
                </div>
                <button
                  onClick={() => handleDelete(entry.id)}
                  className="p-2 text-gray-400 hover:text-red-500 transition-colors duration-200 opacity-0 group-hover:opacity-100"
                  title="Delete item"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
} 