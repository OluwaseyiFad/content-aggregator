import feedparser


from celery import shared_task



from .models import *
from .utils import save_new_contents



# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.


def fetch_and_save(_feeds, content_model):
     print("Saving contents....")
     for feed_url in _feeds:
        _feed = feedparser.parse(feed_url)
        save_new_contents(_feed, content_model)


@shared_task
def fetch_crypto_content():
    """Fetches latest crypto contents"""
    _feeds = [
        "https://cointelegraph.com/rss",
        "https://bitcoinmagazine.com/.rss/full/",
        "https://cryptopotato.com/feed/",
        "https://crypto.news/feed/",
        "https://decrypt.co/feed",
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://thedefiant.io/feed/",
        "https://blockworks.co/feed/",
    ]
    fetch_and_save(_feeds, CryptoContent)



@shared_task
def fetch_tech_jobs():
    """Fetch latest tech job updates"""
    _feeds = [
        "https://weworkremotely.com/categories/remote-back-end-programming-jobs.rss",
        "https://weworkremotely.com/categories/remote-full-stack-programming-jobs.rss",
        "https://weworkremotely.com/remote-jobs.rss",
        "https://techcrunch.com/category/startups/feed/",
        "https://news.crunchbase.com/feed/",
        "https://stackoverflow.blog/feed/",
        "https://www.jobbio.com/feed/",
        "https://blog.hired.com/feed/",
    ]
    fetch_and_save(_feeds, JobUpdatesContent)


@shared_task
def fetch_cyber_content():
    """Fetches cyber security contents and news"""
    _feeds = [
        "https://feeds.feedburner.com/TheHackersNews",
        "https://www.darkreading.com/rss_simple.asp",
        "https://krebsonsecurity.com/feed/",
        "https://www.cyberscoop.com/feed/",
        "https://www.helpnetsecurity.com/feed/",
        "https://securityaffairs.co/feed",
        "https://securelist.com/feed/",
        "https://securityintelligence.com/feed/",
        "https://www.bleepingcomputer.com/feed/",
        "https://portswigger.net/daily-swig/rss",
        "https://www.recordedfuture.com/feed",
    ]
    fetch_and_save(_feeds, CyberSecurityContent)


@shared_task
def fetch_python_content():
    """Fetches pythonic contents"""
    _feeds = [
        "https://realpython.com/atom.xml?format=xml",
        "https://planetpython.org/rss20.xml",
        "https://blog.python.org/feeds/posts/default",
        "https://talkpython.fm/episodes/rss",
        "https://blog.jetbrains.com/pycharm/feed/",
        "https://devblogs.microsoft.com/python/feed/",
        "https://www.fullstackpython.com/feeds/all.atom.xml",
        "https://pythonbytes.fm/episodes/rss",
        "https://blog.miguelgrinberg.com/feed",
    ]
    fetch_and_save(_feeds, PythonContent)


@shared_task
def fetch_sd_content():
    """Fetches software development contents"""
    _feeds = [
        "https://news.ycombinator.com/rss",
        "https://feed.infoq.com/",
        "https://martinfowler.com/feed.atom",
        "https://sdtimes.com/feed/",
        "https://www.developer-tech.com/feed",
        "https://blog.codinghorror.com/rss/",
        "https://www.joelonsoftware.com/feed/",
        "https://dev.to/feed",
        "https://github.blog/feed/",
        "https://engineering.fb.com/feed/",
        "https://netflixtechblog.com/feed",
    ]
    fetch_and_save(_feeds, SoftwareDevelopmentContent)


@shared_task
def fetch_ui_ux_content():
    """Fetches UI contents"""
    _feeds = [
        "https://uxdesign.cc/feed",
        "https://uxplanet.org/feed",
        "https://www.smashingmagazine.com/feed/",
        "https://www.nngroup.com/feed/rss/",
        "https://usabilitygeek.com/feed/",
        "https://uxmastery.com/feed/",
        "https://www.invisionapp.com/inside-design/feed",
        "https://www.figma.com/blog/rss.xml",
        "https://alistapart.com/main/feed/",
        "https://css-tricks.com/feed/",
    ]
    fetch_and_save(_feeds, UiUxContent)


@shared_task
def fetch_mobile_pc_content():
    """Fetches news relating to mobile and pc devices & development"""
    _feeds = [
        "https://www.androidcentral.com/feed",
        "https://9to5mac.com/feed/",
        "https://9to5google.com/feed/",
        "https://www.androidpolice.com/feed/",
        "https://www.xda-developers.com/feed/",
        "https://www.macrumors.com/macrumors.xml",
        "https://www.theverge.com/mobile/rss/index.xml",
        "https://www.pcworld.com/feed",
        "https://www.tomshardware.com/feeds/all",
    ]
    fetch_and_save(_feeds, MobilePcContent)


@shared_task
def fetch_general_content():
    """Fetches general tech contents"""
    _feeds = [
        "https://techcrunch.com/feed/",
        "https://arstechnica.com/feed/",
        "https://www.wired.com/feed/rss/",
        "https://www.theverge.com/rss/index.xml",
        "https://thenextweb.com/feed/",
        "https://www.engadget.com/rss.xml",
        "https://gizmodo.com/rss",
        "https://www.techmeme.com/feed.xml",
        "https://mashable.com/feeds/rss/all",
    ]
    fetch_and_save(_feeds, GeneralContent)


@shared_task
def fetch_ai_content():
    """Fetches AI and machine learning content"""
    _feeds = [
        "https://www.zdnet.com/topic/artificial-intelligence/rss.xml",
        "https://www.technologyreview.com/feed/",
        "https://syncedreview.com/category/ai/feed/",
        "https://www.kdnuggets.com/feed/rss2",
        "https://www.aitrends.com/feed/",
        "https://www.analyticsinsight.net/category/artificial-intelligence/feed/",
        "https://machinelearningmastery.com/feed/",
        "https://openai.com/blog/rss/",
        "https://blogs.nvidia.com/feed/",
        "https://ai.googleblog.com/feeds/posts/default",
        "https://aws.amazon.com/blogs/machine-learning/feed/",
        "https://www.marktechpost.com/feed/",
        "https://towardsdatascience.com/feed/",
    ]
    fetch_and_save(_feeds, AIContent)


@shared_task
def fetch_medical_news():
    """Fetches medical news and healthcare content"""
    _feeds = [
        "https://www.sciencedaily.com/rss/health_medicine/diseases_and_conditions.xml",
        "https://www.medicalnewstoday.com/rss",
        "https://www.healthline.com/rss",
        "https://www.medscape.com/rss/public/medscapewire",
        "https://www.healio.com/rss/specialty",
        "https://www.fiercepharma.com/rss/xml",
        "https://www.statnews.com/feed/",
    ]
    fetch_and_save(_feeds, MedicalNewsContent)


@shared_task
def fetch_ai_medical_imaging():
    """Fetches AI in medical imaging content"""
    _feeds = [
        "https://www.rsna.org/rss/press-releases",
        "https://pubs.rsna.org/action/showFeed?type=etoc&feed=rss&jc=radiol",
        "https://www.nature.com/npjdigitalmed.rss",
        "https://blogs.nvidia.com/blog/category/healthcare/feed/",
        "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
        "https://www.medicaldevice-network.com/feed/",
    ]
    fetch_and_save(_feeds, AIMedicalImagingContent)


@shared_task
def cleanup_old_content():
    """Delete RSS content older than 30 days"""
    from django.utils import timezone
    from datetime import timedelta

    cutoff_date = timezone.now() - timedelta(days=30)

    content_models = [
        GeneralContent, AIContent, CryptoContent, CyberSecurityContent,
        PythonContent, SoftwareDevelopmentContent, UiUxContent, MobilePcContent,
        JobUpdatesContent, MedicalNewsContent, AIMedicalImagingContent
    ]

    total_deleted = 0
    for model in content_models:
        deleted = model.objects.filter(pub_date__lt=cutoff_date).delete()
        total_deleted += deleted[0]
        print(f"Deleted {deleted[0]} old items from {model.__name__}")

    print(f"Total cleanup: {total_deleted} items deleted")
    return total_deleted



