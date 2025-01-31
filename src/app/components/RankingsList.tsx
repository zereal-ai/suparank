import { Item } from '../api';

interface RankingsListProps {
  items: Item[];
  loading: boolean;
}

export function RankingsList({ items, loading }: RankingsListProps) {
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
            {items.map((entry, index) => (
              <div
                key={entry.id}
                className={`flex items-center gap-4 p-4 bg-white rounded-lg shadow-sm border border-gray-200`}
              >
                <div className="flex-shrink-0 flex items-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold
                    ${entry.rank !== null 
                      ? "bg-blue-500 text-white" 
                      : "border-2 border-blue-500 text-transparent"
                    }`}
                  >
                    {entry.rank}
                  </div>
                </div>
                <div className="flex-grow min-w-0">
                  <h3 className="text-lg font-semibold text-gray-900 leading-tight">{entry.title}</h3>
                  <p className="text-gray-600 text-sm">{entry.description}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
} 