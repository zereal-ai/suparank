const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const NO_CACHE_HEADERS = {
  'Content-Type': 'application/json',
  'Cache-Control': 'no-cache, no-store, must-revalidate',
  'Pragma': 'no-cache',
  'Expires': '0'
};

export interface Item {
  id: string;
  title: string;
  description: string;
  rank: number | null;
}

export interface ComparisonPair {
  pair: [Item, Item];
  complete: boolean;
}

export async function getRankings(): Promise<Item[]> {
  const response = await fetch(`${API_URL}/api/rankings`, {
    method: 'GET',
    mode: 'cors',
    headers: NO_CACHE_HEADERS
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch rankings: ${response.statusText}`);
  }
  const data = await response.json();
  return data.rankings || [];
}

export async function getNextPair(): Promise<ComparisonPair | null> {
  const response = await fetch(`${API_URL}/api/next-pair`, {
    method: 'GET',
    mode: 'cors',
    headers: NO_CACHE_HEADERS
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch next pair: ${response.statusText}`);
  }
  const data = await response.json();
  if (data.complete) {
    return null;
  }
  return data;
}

export async function addItem(title: string, description: string): Promise<Item> {
  const response = await fetch(`${API_URL}/api/entries`, {
    method: 'POST',
    mode: 'cors',
    headers: NO_CACHE_HEADERS,
    body: JSON.stringify({ title, description }),
  });
  if (!response.ok) {
    throw new Error(`Failed to add item: ${response.statusText}`);
  }
  const data = await response.json();
  return data.entry;
}

export async function chooseWinner(winnerId: string, loserId: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/choose`, {
    method: 'POST',
    mode: 'cors',
    headers: NO_CACHE_HEADERS,
    body: JSON.stringify({
      winner_id: winnerId,
      loser_id: loserId
    }),
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to choose winner: ${errorText}`);
  }
}

export async function resetRanking(): Promise<void> {
  const response = await fetch(`${API_URL}/api/reset`, {
    method: 'POST',
    mode: 'cors',
    headers: NO_CACHE_HEADERS
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to reset rankings: ${errorText}`);
  }
  // Force reload rankings after reset
  await getRankings();
} 