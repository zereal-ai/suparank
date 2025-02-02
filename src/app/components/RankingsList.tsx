import { TrophyIcon, XMarkIcon, QueueListIcon } from '@heroicons/react/24/outline';
import { Item, deleteItem } from '../api';

interface RankingsListProps {
  items: Item[];
  loading: boolean;
  onItemDeleted: () => void;
  sortedList?: string[] | null;
}

export function RankingsList({ items, loading, onItemDeleted, sortedList }: RankingsListProps) {
  const handleDelete = async (itemId: string) => {
    try {
      await deleteItem(itemId);
      onItemDeleted();
    } catch (error) {
      console.error('Failed to delete item:', error);
      // You might want to show a toast notification here
    }
  };

  // Split items into ranked and unranked
  const rankedItems = sortedList 
    ? items.filter(item => sortedList.includes(item.id))
    : [];
  const unrankedItems = items.filter(item => !sortedList?.includes(item.id));

  const ItemRow = ({ item }: { item: Item }) => (
    <div
      key={item.id}
      className="flex items-center gap-4 p-4 bg-white rounded-lg border border-gray-200 hover:border-blue-200 group transition-all duration-200"
    >
      <div className="flex-grow min-w-0">
        <h3 className="text-lg font-medium text-gray-900 leading-tight">{item.title}</h3>
        {item.description && (
          <p className="text-gray-600 text-sm mt-1">{item.description}</p>
        )}
      </div>
      <button
        onClick={() => handleDelete(item.id)}
        className="p-2 text-gray-400 hover:text-red-500 transition-colors duration-200 opacity-0 group-hover:opacity-100"
        title="Delete item"
      >
        <XMarkIcon className="h-5 w-5" />
      </button>
    </div>
  );

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
          <div className="space-y-6">
            {/* Ranked items */}
            {rankedItems.length > 0 && (
              <div className="space-y-2">
                {rankedItems.map((item) => (
                  <ItemRow key={item.id} item={item} />
                ))}
              </div>
            )}

            {/* Divider and unranked items */}
            {unrankedItems.length > 0 && (
              <>
                <div className="relative">
                  <div className="absolute inset-0 flex items-center" aria-hidden="true">
                    <div className="w-full border-t border-gray-200" />
                  </div>
                  <div className="relative flex justify-center">
                    <div className="flex items-center gap-2 bg-white px-3 text-sm text-gray-500">
                      <QueueListIcon className="h-5 w-5" />
                      <span>Missing comparisons</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-2 opacity-75">
                  {unrankedItems.map((item) => (
                    <ItemRow key={item.id} item={item} />
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </section>
  );
} 