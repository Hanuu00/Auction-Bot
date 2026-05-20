-- users 프로필
create table if not exists profiles (
  id uuid references auth.users primary key,
  nickname text not null,
  avatar_url text,
  created_at timestamptz default now()
);

-- 뽑기방
create table if not exists places (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references profiles(id),
  name text not null,
  address text not null,
  sido text not null,
  sigungu text not null,
  dong text,
  lat float not null,
  lng float not null,
  game_types text[] default '{}',
  difficulty int check (difficulty between 1 and 5),
  open_time text,
  parking boolean default false,
  tip text,
  photos text[] default '{}',
  status text default 'active',
  like_count int default 0,
  created_at timestamptz default now()
);

-- 후기
create table if not exists reviews (
  id uuid primary key default gen_random_uuid(),
  place_id uuid references places(id) on delete cascade,
  user_id uuid references profiles(id),
  rating int check (rating between 1 and 5),
  content text not null,
  photos text[] default '{}',
  created_at timestamptz default now()
);

-- 저장/좋아요
create table if not exists likes (
  id uuid primary key default gen_random_uuid(),
  place_id uuid references places(id) on delete cascade,
  user_id uuid references profiles(id),
  unique(place_id, user_id)
);

drop view if exists places_with_rating;

-- 평균 별점 뷰
create view places_with_rating as
select
  p.*,
  coalesce(avg(r.rating), 0)::numeric(3,1) as avg_rating,
  count(r.id) as review_count
from places p
left join reviews r on r.place_id = p.id
group by p.id;
