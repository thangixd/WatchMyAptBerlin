from modules.job import WBMScrapingJob, DegewoScrapingJob

housing_association = {
    'WBM': [
        'https://www.wbm.de/wohnungen-berlin/angebote/',
        WBMScrapingJob,
        "openimmo-search-list-item",
        None,
        "imageTitle",
        "address",
        "check-property-list",
        "main-property-size",
        "main-property-rent"
    ],
    'Degewo': [
        'https://immosuche.degewo.de/de/search',
        DegewoScrapingJob,
        "article-list__item",
        1,
        "article__title",
        "article__meta",
        "article__tags",
        "article__properties",
        "article__price-tag"
    ],
    'Gewobag': [
        'https://www.gewobag.de/fuer-mieter-und-mietinteressenten/mietangebote/?objekttyp%5B%5D=wohnung&gesamtmiete_von=&gesamtmiete_bis=&gesamtflaeche_von=&gesamtflaeche_bis=&zimmer_von=&zimmer_bis=&sort-by=',
        WBMScrapingJob,
        "angebot-big-box",
        None,
        "angebot-title",
        "angebot-address",  # Needs to be fixed, as the more appropriate div class is "screen-reader-text". However, there are two divs with the same class, so "find.next" is not reliable in this case.
        'angebot-characteristics',
        "angebot-area",
        "angebot-kosten"
    ]
}
