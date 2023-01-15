# function/overpass-proxy


```bash
echo "data=node[name='Gielgen'];out;" > query.osm
curl "https://osm-faas.etica.ai/function/overpass-proxy" --data @query.osm --output output.osm

```