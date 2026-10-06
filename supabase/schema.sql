create extension if not exists pgcrypto;

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  age_group text check (age_group in ('60–69', '70–79', '80+')),
  genres text[] not null default '{}',
  favourite_movie_ids bigint[] not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Safe migration for an existing project created from an earlier version.
alter table public.profiles add column if not exists age_group text;
alter table public.profiles drop constraint if exists profiles_age_group_check;
alter table public.profiles add constraint profiles_age_group_check check (age_group is null or age_group in ('60–69', '70–79', '80+'));

create table if not exists public.movies (
  id bigint primary key,
  title text not null,
  overview text,
  release_date date,
  genres text[] not null default '{}',
  "cast" text[] NOT NULL DEFAULT '{}'::text[],
  director text,
  keywords text[] not null default '{}',
  poster_path text,
  source text not null default 'tmdb',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.ratings (
  user_id uuid not null references auth.users(id) on delete cascade,
  movie_id bigint not null references public.movies(id) on delete cascade,
  rating numeric(2,1) not null check (rating >= 1 and rating <= 5),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (user_id, movie_id)
);

create table if not exists public.interactions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  movie_id bigint references public.movies(id) on delete set null,
  action text not null check (action in ('view','search','save','rate','recommendation_click')),
  metadata jsonb not null default '{}',
  created_at timestamptz not null default now()
);

alter table public.profiles enable row level security;
alter table public.profiles force row level security;
alter table public.movies enable row level security;
alter table public.ratings enable row level security;
alter table public.ratings force row level security;
alter table public.interactions enable row level security;
alter table public.interactions force row level security;

drop policy if exists profiles_self on public.profiles;
create policy profiles_self on public.profiles for all to authenticated using (auth.uid() = id) with check (auth.uid() = id);

drop policy if exists movies_read on public.movies;
create policy movies_read on public.movies for select to anon, authenticated using (true);

drop policy if exists ratings_self on public.ratings;
create policy ratings_self on public.ratings for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists interactions_self on public.interactions;
create policy interactions_self on public.interactions for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public
as $$ begin insert into public.profiles(id) values (new.id) on conflict do nothing; return new; end; $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users for each row execute procedure public.handle_new_user();
