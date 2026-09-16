from toddle import client, API
with client() as c:
    r = c.post(API, json={"query": "{ __schema { queryType { fields { name } } } }"})
    print(r.status_code)
    print(r.text[:2000])
