/* Updated API utilities for merge sort service */

const API_URL = process.env.NEXT_PUBLIC_VERCEL_URL ? `https://${process.env.NEXT_PUBLIC_VERCEL_URL}/api` : 'http://localhost:8000/api';

const NO_CACHE_HEADERS = {
  'Content-Type': 'application/json',
  'Cache-Control': 'no-store'
};

export interface Item {
  id: string;
  title: string;
  description?: string;
}

/**
 * Fetches items from Airtable
 */
export async function getItems(): Promise<Item[]> {
  const response = await fetch(`${API_URL}/items`, {
    method: 'GET',
    headers: NO_CACHE_HEADERS
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch items: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Deletes an item from Airtable
 */
export async function deleteItem(itemId: string): Promise<void> {
  const response = await fetch(`${API_URL}/items/${itemId}`, {
    method: 'DELETE',
    headers: NO_CACHE_HEADERS
  });
  if (!response.ok) {
    throw new Error(`Failed to delete item: ${response.statusText}`);
  }
}

/**
 * Adds a new item to Airtable
 */
export async function addItem(title: string, description?: string): Promise<Item> {
  const response = await fetch(`${API_URL}/items`, {
    method: 'POST',
    headers: NO_CACHE_HEADERS,
    body: JSON.stringify({ title, description })
  });
  if (!response.ok) {
    throw new Error(`Failed to add item: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Starts a new merge sort session.
 * Expects an array of strings as items.
 * Returns the session ID.
 */
export async function startSortSession(items: string[]): Promise<string> {
  const response = await fetch(`${API_URL}/sort/start`, {
    method: 'POST',
    mode: 'cors',
    headers: NO_CACHE_HEADERS,
    body: JSON.stringify({ items })
  });
  if (!response.ok) {
    throw new Error(`Failed to start sort session: ${response.statusText}`);
  }
  const data = await response.json();
  return data.session_id;
}

/**
 * Retrieves the next pair to compare for the given session.
 * Returns either a comparison object with item_a and item_b, or a message if sorting is complete.
 */
export async function getNextPair(sessionId: string): Promise<any> {
  const response = await fetch(`${API_URL}/sort/${sessionId}/next`, {
    method: 'GET',
    mode: 'cors',
    headers: NO_CACHE_HEADERS
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch next pair: ${response.statusText}`);
  }
  const data = await response.json();
  return data;
}

/**
 * Submits a comparison decision for the given session.
 * Choice is expected to be "A" or "B".
 */
export async function postComparison(sessionId: string, choice: 'A' | 'B'): Promise<any> {
  const response = await fetch(`${API_URL}/sort/${sessionId}/compare`, {
    method: 'POST',
    mode: 'cors',
    headers: NO_CACHE_HEADERS,
    body: JSON.stringify({ choice })
  });
  if (!response.ok) {
    throw new Error(`Failed to submit comparison: ${response.statusText}`);
  }
  const data = await response.json();
  return data;
}

/**
 * Retrieves the final sorted list for the given session.
 */
export async function getResult(sessionId: string): Promise<string[]> {
  const response = await fetch(`${API_URL}/sort/${sessionId}/result`, {
    method: 'GET',
    mode: 'cors',
    headers: NO_CACHE_HEADERS
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch result: ${response.statusText}`);
  }
  const data = await response.json();
  return data.sorted_list;
} 