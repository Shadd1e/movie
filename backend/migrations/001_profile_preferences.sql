-- Maple Movies profile fields required by the profile specification.
-- Run this in the Supabase SQL Editor before deploying the updated backend.

alter table public.profiles
  add column if not exists name text,
  add column if not exists region text,
  add column if not exists country text,
  add column if not exists preferred_movie_years text[] not null default '{}';

-- Existing profile columns expected by the current API remain unchanged:
-- id, age_group, genres, favourite_movie_ids.

alter table public.profiles
  drop constraint if exists profiles_preferred_movie_years_valid;

alter table public.profiles
  add constraint profiles_preferred_movie_years_valid
  check (preferred_movie_years <@ array[
    'before_1980', '1980_1999', '2000_2009', '2010_2019', '2020_onwards'
  ]::text[]);
