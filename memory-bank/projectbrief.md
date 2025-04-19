# Suparank Project Brief

## Project Summary
Suparank is a web application for ranking items using a merge sort algorithm. It presents users with a series of pairwise comparisons, where users choose their preference between two items, ultimately creating a ranked list.

## Core Requirements
1. Allow users to add items with titles and descriptions
2. Present pairs of items for comparison
3. Use a merge sort algorithm to efficiently determine the ranking
4. Store items and rankings in Airtable
5. Provide a clean, intuitive user interface
6. Support keyboard navigation for quick comparisons

## Technical Goals
1. Create a responsive web application using Next.js for the frontend
2. Build a FastAPI backend for the sorting algorithm and data operations
3. Connect to Airtable as the data store
4. Support deployment to Vercel

## User Goals
1. Efficiently rank lists of items through simple binary choices
2. View the resulting ranked list after completing comparisons
3. Add, remove, and manage items in the ranking pool
4. Reset and restart ranking sessions as needed

## Project Scope
The initial version focuses on the core ranking functionality with a clean UI. Future enhancements could include:
- User accounts and authentication
- Multiple ranking sessions per user
- More advanced item metadata
- Analytics on ranking patterns
- Export functionality for rankings 