from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^submit/$', 'cms_saq.views.submit', name='cms_saq_submit'),
    url(r'^scores/$', 'cms_saq.views.scores', name='cms_saq_scores'),
    url(r'^edit/$', 'cms_saq.views.change_answer_set', name='cms_saq_edit'),
)

