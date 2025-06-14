from editing.models import ViewAllAdsResponse


async def get_view_all_ads_response():
    msg = await ViewAllAdsResponse.objects.afirst()
    return msg.text if msg else "Нажмите на кнопку ниже, чтобы перейти на сайт со всеми объявлениями. На сайте вы можете настроить фильтры и найти интересующие вас объявления."
