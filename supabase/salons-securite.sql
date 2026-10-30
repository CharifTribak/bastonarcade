-- =====================================================================
-- Baston Arcade : verrouillage de la table des salons (Supabase)
-- À coller dans Supabase > SQL Editor > New query, puis « Run ».
-- Le script peut être relancé sans danger.
-- =====================================================================

-- ---------- ÉTAPE 1 (facultative) : état actuel, pour vérifier ----------
-- Lancez d'abord ces deux requêtes seules si vous voulez voir l'existant.
-- select policyname, cmd, roles, qual, with_check from pg_policies where schemaname = 'public' and tablename = 'salons';
-- select column_name, data_type, is_nullable from information_schema.columns where table_schema = 'public' and table_name = 'salons';

-- ---------- ÉTAPE 2 : verrouillage ----------
begin;

-- un secret par salon : seul le créateur (qui le connaît) peut mettre à jour ou supprimer son salon
alter table public.salons add column if not exists secret text;

-- on repart propre : les anciennes lignes sans secret disparaissent
delete from public.salons where secret is null;

-- formats acceptés
alter table public.salons drop constraint if exists salons_code_fmt;
alter table public.salons add constraint salons_code_fmt check (code ~ '^[A-Z0-9]{4}$');
alter table public.salons drop constraint if exists salons_host_fmt;
alter table public.salons add constraint salons_host_fmt check (char_length(host) between 1 and 14 and host !~* '(https?|www|//|@)');
alter table public.salons drop constraint if exists salons_game_fmt;
alter table public.salons add constraint salons_game_fmt check (game ~ '^[a-z]{2,12}$');
alter table public.salons drop constraint if exists salons_players_rng;
alter table public.salons add constraint salons_players_rng check (players between 0 and 5);
alter table public.salons drop constraint if exists salons_secret_fmt;
alter table public.salons add constraint salons_secret_fmt check (secret ~ '^[0-9a-f]{32}$');

-- règles d'accès : lecture seule des salons récents, plus aucune écriture directe
alter table public.salons enable row level security;
do $$ declare p record; begin
  for p in select policyname from pg_policies where schemaname = 'public' and tablename = 'salons' loop
    execute format('drop policy %I on public.salons', p.policyname);
  end loop;
end $$;
create policy salons_lecture on public.salons for select to anon, authenticated
  using (updated_at > now() - interval '10 minutes');
revoke all on public.salons from anon, authenticated;
grant select (code, host, game, players, updated_at) on public.salons to anon, authenticated;   -- le secret n'est jamais lisible

-- annoncer / rafraîchir son salon
create or replace function public.salon_upsert(p_code text, p_host text, p_game text, p_players int, p_secret text)
returns void language plpgsql security definer set search_path = public as $$
declare cur text;
begin
  if p_secret is null or p_secret !~ '^[0-9a-f]{32}$' then raise exception 'secret invalide'; end if;
  delete from salons where updated_at < now() - interval '1 hour';                         -- ménage
  if (select count(*) from salons where updated_at > now() - interval '2 minutes' and code <> upper(p_code)) >= 150
    then raise exception 'trop de salons'; end if;                                          -- anti-inondation
  select secret into cur from salons where code = upper(p_code);
  if found and cur is distinct from p_secret then raise exception 'salon d''un autre'; end if;
  insert into salons (code, host, game, players, updated_at, secret)
  values (upper(p_code), p_host, p_game, p_players, now(), p_secret)
  on conflict (code) do update set host = excluded.host, game = excluded.game, players = excluded.players, updated_at = now();
end $$;

-- retirer son salon
create or replace function public.salon_delete(p_code text, p_secret text)
returns void language plpgsql security definer set search_path = public as $$
begin
  delete from salons where code = upper(p_code) and secret = p_secret;
end $$;

revoke all on function public.salon_upsert(text, text, text, int, text) from public;
revoke all on function public.salon_delete(text, text) from public;
grant execute on function public.salon_upsert(text, text, text, int, text) to anon, authenticated;
grant execute on function public.salon_delete(text, text) to anon, authenticated;

commit;

-- ---------- ÉTAPE 3 : contrôle ----------
-- Doit afficher une seule règle, « salons_lecture », de type SELECT :
select policyname, cmd from pg_policies where schemaname = 'public' and tablename = 'salons';
