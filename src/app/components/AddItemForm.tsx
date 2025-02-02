import { useState } from 'react';
import { addItem } from '../api';
import { PlusIcon } from '@heroicons/react/24/outline';

interface AddItemFormProps {
  onItemAdded: () => void;
}

export function AddItemForm({ onItemAdded }: AddItemFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);

  async function handleAddItem(e: React.FormEvent) {
    e.preventDefault();
    try {
      await addItem(title, description);
      setTitle('');
      setDescription('');
      setIsExpanded(false);
      onItemAdded();
    } catch (error) {
      console.error('Failed to add item:', error);
    }
  }

  return (
    <section className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      {!isExpanded ? (
        <button
          onClick={() => setIsExpanded(true)}
          className="w-full flex items-center gap-2 text-gray-500 hover:text-gray-900 transition-colors duration-200"
        >
          <PlusIcon className="h-5 w-5" />
          <span>Add new item to rank...</span>
        </button>
      ) : (
        <form onSubmit={handleAddItem} className="space-y-4">
          <div>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full p-3 text-lg font-medium bg-transparent border-none focus:ring-0 focus:outline-none placeholder-gray-400"
              placeholder="Enter item title..."
              autoFocus
              required
            />
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full p-3 bg-transparent border-none focus:ring-0 focus:outline-none placeholder-gray-400 resize-none"
              rows={2}
              placeholder="Add a description... (optional)"
            />
          </div>
          <div className="flex items-center gap-2 pt-2 border-t border-gray-100">
            <button
              type="submit"
              className="px-4 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors duration-200"
            >
              Add item
            </button>
            <button
              type="button"
              onClick={() => setIsExpanded(false)}
              className="px-4 py-1.5 text-sm text-gray-500 hover:text-gray-700 transition-colors duration-200"
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </section>
  );
} 