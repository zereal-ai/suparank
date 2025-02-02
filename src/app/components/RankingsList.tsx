import { Item, deleteItem } from '../api';
import { XMarkIcon } from '@heroicons/react/20/solid';

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
    <section className="bg-white">
      <h2 className="text-lg font-medium mb-4 text-gray-900">
        Current Rankings
      </h2>
      <div className="space-y-3">
        {loading ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : items.length === 0 ? (
          <p className="text-center py-8 text-gray-500">
            No items yet. Add some items to start ranking!
          </p>
        ) : (
          <div className="space-y-4">
            {items.map((entry) => (
              <div
                key={entry.id}
                className={`flex items-center gap-4 p-4 bg-white rounded-lg shadow-sm border border-gray-200 group`}
              >
                <div className="flex-grow min-w-0">
                  <h3 className="text-lg font-semibold text-gray-900 leading-tight">{entry.title}</h3>
                  <p className="text-gray-600 text-sm">{entry.description}</p>
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