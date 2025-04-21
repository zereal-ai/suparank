-- Create items table
create table if not exists items (
    id uuid default gen_random_uuid() primary key,
    title text not null,
    description text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create sessions table
create table if not exists sessions (
    id uuid default gen_random_uuid() primary key,
    state jsonb not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create RLS policies
alter table items enable row level security;
alter table sessions enable row level security;

-- Allow anonymous access for now (you might want to restrict this in production)
create policy "Allow anonymous access to items"
    on items for all
    to anon
    using (true)
    with check (true);

create policy "Allow anonymous access to sessions"
    on sessions for all
    to anon
    using (true)
    with check (true); 