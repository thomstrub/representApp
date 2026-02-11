Request:
curl -X 'GET' \
  'https://v3.openstates.org/people.geo?lat=47.6105&lng=-122.3115&apikey=<API-KEY-HERE>' \
  -H 'accept: application/json'

Response:
```
{
  "results": [
    {
      "id": "ocd-person/55a28978-7661-5a33-a2be-a505a07e2a8e",
      "name": "Adam Smith",
      "party": "Democratic",
      "current_role": {
        "title": "Representative",
        "org_classification": "lower",
        "district": "WA-9",
        "division_id": "ocd-division/country:us/state:wa/cd:9"
      },
      "jurisdiction": {
        "id": "ocd-jurisdiction/country:us/government",
        "name": "United States",
        "classification": "country"
      },
      "given_name": "Adam",
      "family_name": "Smith",
      "image": "https://unitedstates.github.io/images/congress/450x550/S000510.jpg",
      "email": "https://adamsmith.house.gov/contact/email-me",
      "gender": "Male",
      "birth_date": "1965-06-15",
      "death_date": "",
      "extras": {},
      "created_at": "2021-05-10T15:11:31.636275+00:00",
      "updated_at": "2025-02-13T23:53:44.560234+00:00",
      "openstates_url": "https://openstates.org/person/adam-smith-2bactkrtSvcRa2m9xpmAO6/"
    },
    {
      "id": "ocd-person/84aaed1c-e50a-4bbc-8f63-afd22e825ec2",
      "name": "Chipalo Street",
      "party": "Democratic",
      "current_role": {
        "title": "Representative",
        "org_classification": "lower",
        "district": "37",
        "division_id": "ocd-division/country:us/state:wa/sldl:37"
      },
      "jurisdiction": {
        "id": "ocd-jurisdiction/country:us/state:wa/government",
        "name": "Washington",
        "classification": "state"
      },
      "given_name": "Chipalo",
      "family_name": "Street",
      "image": "https://leg.wa.gov/memberphoto/34036.jpg",
      "email": "chipalo.street@leg.wa.gov",
      "gender": "Male",
      "birth_date": "",
      "death_date": "",
      "extras": {
        "title": "Assistant Majority Whip"
      },
      "created_at": "2023-02-14T20:07:43.424363+00:00",
      "updated_at": "2026-01-28T02:44:08.942125+00:00",
      "openstates_url": "https://openstates.org/person/chipalo-street-42L6Ex4L1m5fcGRK8Fev2o/"
    },
    {
      "id": "ocd-person/46c3b77a-7d00-5ecc-83d0-04c8fa05bf04",
      "name": "Maria Cantwell",
      "party": "Democratic",
      "current_role": {
        "title": "Senator",
        "org_classification": "upper",
        "district": "Washington",
        "division_id": "ocd-division/country:us/state:wa"
      },
      "jurisdiction": {
        "id": "ocd-jurisdiction/country:us/government",
        "name": "United States",
        "classification": "country"
      },
      "given_name": "Maria",
      "family_name": "Cantwell",
      "image": "https://unitedstates.github.io/images/congress/450x550/C000127.jpg",
      "email": "https://www.cantwell.senate.gov/contact/email/form",
      "gender": "Female",
      "birth_date": "1958-10-13",
      "death_date": "",
      "extras": {},
      "created_at": "2021-05-10T15:12:47.595536+00:00",
      "updated_at": "2025-03-29T02:32:15.313430+00:00",
      "openstates_url": "https://openstates.org/person/maria-cantwell-29Wu9Q8ZqykHNPmKu4H0U8/"
    },
    {
      "id": "ocd-person/eb3ab543-13a1-53db-a8a1-459e8e91b701",
      "name": "Patty Murray",
      "party": "Democratic",
      "current_role": {
        "title": "Senator",
        "org_classification": "upper",
        "district": "Washington",
        "division_id": "ocd-division/country:us/state:wa"
      },
      "jurisdiction": {
        "id": "ocd-jurisdiction/country:us/government",
        "name": "United States",
        "classification": "country"
      },
      "given_name": "Patty",
      "family_name": "Murray",
      "image": "https://unitedstates.github.io/images/congress/450x550/M001111.jpg",
      "email": "https://www.murray.senate.gov/write-to-patty/",
      "gender": "Female",
      "birth_date": "1950-10-11",
      "death_date": "",
      "extras": {},
      "created_at": "2021-05-10T15:10:20.057444+00:00",
      "updated_at": "2025-03-29T02:28:58.340002+00:00",
      "openstates_url": "https://openstates.org/person/patty-murray-79s1drBZWjuTnJt809WXIH/"
    },
    {
      "id": "ocd-person/1d4a95b2-4a4f-4acb-b5c6-64850b8e34b9",
      "name": "Rebecca Saldaña",
      "party": "Democratic",
      "current_role": {
        "title": "Senator",
        "org_classification": "upper",
        "district": "37",
        "division_id": "ocd-division/country:us/state:wa/sldu:37"
      },
      "jurisdiction": {
        "id": "ocd-jurisdiction/country:us/state:wa/government",
        "name": "Washington",
        "classification": "state"
      },
      "given_name": "Rebecca",
      "family_name": "Saldaña",
      "image": "https://leg.wa.gov/memberphoto/27290.jpg",
      "email": "rebecca.saldana@leg.wa.gov",
      "gender": "Female",
      "birth_date": "1977-04-01",
      "death_date": "",
      "extras": {
        "title": "Majority Caucus Vice Chair"
      },
      "created_at": "2018-10-18T16:13:59.399906+00:00",
      "updated_at": "2026-01-28T02:44:02.268240+00:00",
      "openstates_url": "https://openstates.org/person/rebecca-saldana-tGrUddzcoHtVVMa9K7CJ7/"
    },
    {
      "id": "ocd-person/50800e36-5c44-43d0-b786-7828523e92cd",
      "name": "Sharon Tomiko Santos",
      "party": "Democratic",
      "current_role": {
        "title": "Representative",
        "org_classification": "lower",
        "district": "37",
        "division_id": "ocd-division/country:us/state:wa/sldl:37"
      },
      "jurisdiction": {
        "id": "ocd-jurisdiction/country:us/state:wa/government",
        "name": "Washington",
        "classification": "state"
      },
      "given_name": "Sharon Tomiko",
      "family_name": "Santos",
      "image": "https://leg.wa.gov/memberphoto/3483.jpg",
      "email": "sharontomiko.santos@leg.wa.gov",
      "gender": "Female",
      "birth_date": "1961-07-05",
      "death_date": "",
      "extras": {},
      "created_at": "2018-10-18T16:14:00.030551+00:00",
      "updated_at": "2026-01-28T02:44:26.211113+00:00",
      "openstates_url": "https://openstates.org/person/sharon-tomiko-santos-2RtuHApuOo7XZor7yEP13t/"
    }
  ],
  "pagination": {
    "per_page": 10,
    "page": 1,
    "max_page": 1,
    "total_items": 6
  }
}
```