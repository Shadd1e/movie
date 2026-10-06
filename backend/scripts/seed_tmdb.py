import argparse, asyncio, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.tmdb import search_movies, movie_details
from app.db import supabase

async def main():
    p=argparse.ArgumentParser(); p.add_argument('--query', action='append', required=True); args=p.parse_args()
    for q in args.query:
        data=await search_movies(q)
        if not data.get('results'): print('No result:', q); continue
        m=await movie_details(data['results'][0]['id'])
        genres=[g['name'] for g in m.get('genres',[])]
        credits=m.get('credits',{})
        cast=[x['name'] for x in credits.get('cast',[])[:8]]
        director=next((x['name'] for x in credits.get('crew',[]) if x.get('job')=='Director'),None)
        keywords=[x['name'] for x in m.get('keywords',{}).get('keywords',[])[:20]]
        row={'id':m['id'],'title':m.get('title'),'overview':m.get('overview'),'release_date':m.get('release_date'),'genres':genres,'cast':cast,'director':director,'keywords':keywords,'poster_path':m.get('poster_path'),'source':'tmdb'}
        supabase.table('movies').upsert(row).execute(); print('Seeded:', row['title'])

asyncio.run(main())
