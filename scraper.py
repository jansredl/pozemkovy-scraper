
data = scrape()

if detail:
    okres = detail.get("okres")
    geotext = f"{lokalita}, {okres}, Česká republika" if okres else f"{lokalita}, Česká republika"
else:
    geotext = f"{lokalita}, Česká republika"
