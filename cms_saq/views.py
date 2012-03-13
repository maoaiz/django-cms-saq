import re

from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.cache import never_cache
from django.utils import simplejson

from lazysignup.decorators import allow_lazy_user

from cms_saq.models import Question, Answer, Submission

ANSWER_RE = re.compile(r'^[\w-]+(,[\w-]+)*$')

@require_POST
@allow_lazy_user
def submit(request):
    for question_slug, answers in request.POST.iteritems():
        # check answers is a list of slugs
        if not ANSWER_RE.match(answers):
            return HttpResponseBadRequest("Invalid answers: %s" % answers)
        # validate the question
        try:
            question = Question.objects.get(slug=question_slug)
        except Question.DoesNotExist:
            return HttpResponseBadRequest("Invalid question '%s'" % question_slug)
        # validate and score the answer
        try:
            score = question.score(answers)
        except Answer.DoesNotExist:
            return HttpResponseBadRequest("Invalid answer '%s:%s'" % (question_slug, answers))
        # save!
        filter_attrs = {'user': request.user, 'question': question_slug}
        attrs = {'answer': answers, 'score': score}
        rows = Submission.objects.filter(**filter_attrs).update(**attrs)
        if not rows:
            attrs.update(filter_attrs)
            Submission.objects.create(**attrs)
    return HttpResponse("OK")

@require_GET
@never_cache
@login_required
def scores(request):
    slugs = request.GET.getlist('q')
    if slugs == []:
        return HttpResponseBadRequest("No questions supplied")
    submissions = Submission.objects.filter(user=request.user, question__in=slugs)
    submissions = [[s.question, {'answer': s.answer, 'score': s.score}]
            for s in submissions]
    data = {
        "questions": slugs,
        "submissions": dict(submissions),
        "complete": len(submissions) == len(slugs)
    }
    return HttpResponse(simplejson.dumps(data), mimetype="application/json")

# TODO benchmarking

