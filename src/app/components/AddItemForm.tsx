import { useState } from 'react';
import { addItem } from '../api';

interface AddItemFormProps {
  onItemAdded: () => void;
}

export function AddItemForm({ onItemAdded }: AddItemFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  async function handleAddItem(e: React.FormEvent) {
    e.preventDefault();
    try {
      await addItem(title, description);
      setTitle('');
      setDescription('');
      onItemAdded();
    } catch (error) {
      console.error('Failed to add item:', error);
    }
  }

  return (
    <section className="bg-white">
      <h2 className="text-lg font-medium mb-4 text-gray-900">
        Add New Item
      </h2>
      <form onSubmit={handleAddItem} className="space-y-3">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter task title"
          required
        />
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          rows={2}
          placeholder="Enter task description"
          required
        />
        <button
          type="submit"
          className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Add Task
        </button>
      </form>
    </section>
  );
} 