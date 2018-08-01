from meowth.core.data_manager import schema

def setup(bot):
    lang_table = bot.dbi.table('languages')
    lang_table.new_columns = [
        schema.IDColumn('language_id', primary_key=True),
        schema.StringColumn('iso639', required=True),
        schema.StringColumn('iso3166', required=True),
        schema.StringColumn('identifier', required=True, unique=True),
        schema.BoolColumn('official', required=True)
    ]

    lang_table.initial_data = [
        {
            "language_id": 9,
            "iso639": "en",
            "iso3166": "us",
            "identifier": "en",
            "official": True
        },
        {
            "language_id": 12,
            "iso639": "en",
            "iso3166": "gb",
            "identifier": "en-gb",
            "official": False
        },
        {
            "language_id": 1,
            "iso639": "ja",
            "iso3166": "jp",
            "identifier": "ja",
            "official": True
        },
        {
            "language_id": 11,
            "iso639": "ja",
            "iso3166": "jp",
            "identifier": "ja-kanji",
            "official": True
        },
        {
            "language_id": 2,
            "iso639": "ja",
            "iso3166": "jp",
            "identifier": "roomaji",
            "official": True
        },
        {
            "language_id": 3,
            "iso639": "ko",
            "iso3166": "kr",
            "identifier": "ko",
            "official": True
        },
        {
            "language_id": 4,
            "iso639": "zh",
            "iso3166": "cn",
            "identifier": "zh",
            "official": True
        },
        {
            "language_id": 5,
            "iso639": "fr",
            "iso3166": "fr",
            "identifier": "fr",
            "official": True
        },
        {
            "language_id": 6,
            "iso639": "de",
            "iso3166": "de",
            "identifier": "de",
            "official": True
        },
        {
            "language_id": 7,
            "iso639": "es",
            "iso3166": "es",
            "identifier": "es",
            "official": True
        },
        {
            "language_id": 8,
            "iso639": "it",
            "iso3166": "it",
            "identifier": "it",
            "official": True
        },
        {
            "language_id": 10,
            "iso639": "cs",
            "iso3166": "cz",
            "identifier": "cs",
            "official": False
        }
    ]

    return lang_table
